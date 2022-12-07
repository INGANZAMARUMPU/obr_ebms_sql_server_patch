from enum import Enum
from datetime import date

import requests
import json
import variables

headers = {}

class STATUS(Enum):
    FAILED = 0
    SUCCESS = 1
    UPDATED = 1
    IGNORED = 2

def console_log(*things):
    if variables.DEBUG:
        print(*things)
    else:
        with open(f"logs/{date.today()}.txt", "a") as file:
            print(*things, file=file)

def login():
    data = {
        "username": variables.obr_user,
        "password": variables.obr_pass
    }
    global headers
    try:
        r = requests.post(
            variables.obr_url+"/login/",
            data=json.dumps(data),
            timeout=20
        )
        token = r.json()["result"]["token"]
        headers = {
            'Authorization': "Bearer "+token
        }
        return True
    except Exception as e:
        console_log(f"Erreur d'authentification:\n{e}")
        return False

def sendToOBR(facture_dict, forcing_creation=False):
    global headers
    if variables.obr_user not in facture_dict["invoice_signature"]:
        return STATUS.IGNORED

    if not headers.get('Authorization'):
        if not login():
            return STATUS.FAILED
    try:
        r = requests.post(
            variables.obr_url+"/addInvoice/",
            data=json.dumps(facture_dict),
            headers=headers,
            timeout=20
        )
    except Exception as e:
        console_log(str(e)) 
        return STATUS.FAILED
    if r.status_code == 403:
        if not login():
            return STATUS.FAILED
        return sendToOBR(facture_dict)
    response = r.json()

    if (not response["success"]):
        if('déjà annulée' in response["msg"]):
            facture_dict['cancelled_invoice_ref'] = ''
            return sendToOBR(facture_dict, True)

        if ('existe déjà' in response["msg"] or
            'date actuelle' in response["msg"]):
            console_log(response["msg"])
            return STATUS.IGNORED

        console_log(response["msg"])
        return STATUS.FAILED

    if(facture_dict["cancelled_invoice_ref"] or forcing_creation):
        return STATUS.UPDATED
    return STATUS.SUCCESS

def genFactureQuery(table):
    return f"""
        SELECT
            {table}.numFact AS invoice_number,
            {table}.DateFact AS invoice_date,
            'FN' AS invoice_type,
            '2' AS tp_type,
            'NELIC TELECOM' AS tp_name,
            ? AS tp_TIN,
            '05267' AS tp_trade_number,
            '' AS tp_postal_number,
            '+25769069120' AS tp_phone_number,
            'BUJUMBURA' AS tp_address_province,
            'MUKAZA' AS tp_address_commune,
            'ROHERO' AS tp_address_quartier,
            'BUSINESS PLAZA' AS tp_address_avenue,
            'No. 20' AS tp_address_number,
            '0' AS vat_taxpayer,
            '0' AS ct_taxpayer,
            '0' AS tl_taxpayer,
            'DMC' AS tp_fiscal_center,
            'VENTE DE CARTE DE RECHARGE' AS tp_activity_sector,
            'S.U.' AS tp_legal_form,

            '1' AS payment_type,
            'BIF' AS invoice_currency,
            clients.NomCli+' '+clients.PrenomCli AS customer_name,
            clients.NIF AS customer_TIN,
            adresseCli.commune+' '+adresseCli.province AS customer_address,
            '1' AS vat_customer_payer,
            '' AS cancelled_invoice_ref,
            {table}.numFact AS invoice_ref,
            {table}.signatureobr AS invoice_signature,
            {table}.DateFact AS invoice_signature_date
        FROM
            {table}
        JOIN
            clients
        ON
            {table}.IdCli = clients.IdCli
        LEFT OUTER JOIN
            adresseCli
        ON
            {table}.IdCli = adresseCli.IdCli
        WHERE
            {table}.DateFact > ?
        AND
            {table}.signatureobr IS NOT NULL
        ORDER BY
            {table}.DateFact
    """
