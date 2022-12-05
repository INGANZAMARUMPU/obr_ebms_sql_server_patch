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

def sendToOBR(facture_dict):
    global headers
    if variables.obr_user not in facture_dict["invoice_signature"]:
        return STATUS.IGNORED

    if not headers.get('Authorization'):
        if not login():
            return STATUS.FAILED
    r = requests.post(
        variables.obr_url+"/addInvoice/",
        data=json.dumps(facture_dict),
        headers=headers,
        timeout=20
    )
    if r.status_code == 403:
        if not login():
            return STATUS.FAILED
        return sendToOBR(facture_dict)
    response = r.json()
    if (not response["success"]):
        if ('existe déjà' in response["msg"] or 'date actuelle' in response["msg"]):
            console_log(response["msg"])
            return STATUS.IGNORED
        console_log(response["msg"])
        return STATUS.FAILED
    if(facture_dict["cancelled_invoice_ref"]):
        return STATUS.UPDATED
    return STATUS.SUCCESS
