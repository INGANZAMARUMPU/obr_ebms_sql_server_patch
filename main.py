import pyodbc
from facture import Facture
from tqdm import tqdm
from datetime import datetime

import variables
from functions import *

conn = pyodbc.connect(
    driver=variables.driver,
    host=variables.host,
    database=variables.database,
    user=variables.user,
    password=variables.password,
)

cursor = conn.cursor()

with open("LAST.DAT", 'r') as file:
    min_date = file.readline() or "2022-16-11 00:00:00"

query = """
    SELECT
        Facture.numFact AS invoice_number,
        Facture.dateFact AS invoice_date,
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
        '' AS invoice_ref,
        '' AS invoice_signature,
        Facture.dateFact AS invoice_signature_date
    FROM
        Facture
    JOIN
        clients
    ON 
        Facture.idCli = clients.IdCli
    JOIN
        adresseCli
    ON
        Facture.IdCli = adresseCli.IdCli
    WHERE
        Facture.DateFact > ?
    ORDER BY
        Facture.DateFact
"""

cursor.execute(query, variables.obr_nif, min_date)

items = cursor.fetchall()

for item in tqdm(items):
    # print(item)

    facture = Facture(*item)
    facture.generateObrFact(cursor)
    if not sendToOBR(facture.__dict__):
        break
    with open("LAST.DAT", 'w') as file:
        last_date = datetime.strptime(facture.invoice_date, '%Y-%m-%d %H:%M:%S')
        file.write(last_date.strftime("%Y-%d-%m %H:%M:%S"))
        file.seek(0)