from enum import Enum

import requests
import json
import variables

headers = {}

class STATUS(Enum):
    FAILED = 0
    SUCCESS = 1
    IGNORED = 2

def login():
	data = {
		"username": variables.obr_user,
		"password": variables.obr_pass
	}
	r  = requests.post(
		variables.obr_url+"/login/",
		data=json.dumps(data)
	)
	global headers
	try:
		token = r.json()["result"]["token"]
		headers = {
			'Authorization': "Bearer "+token
		}
		return True
	except Exception as e:
		print(f"Erreur d'authentification:\n{e}")
		return False

def sendToOBR(facture):
	global headers
	if not headers.get('Authorization'):
		if not login():
			return STATUS.FAILED
	r = requests.post(
		variables.obr_url+"/addInvoice/",
		data=json.dumps(facture),
		headers=headers
	)
	if r.status_code == 403:
		if not login():
			return STATUS.FAILED
		return sendToOBR(facture)
	response = r.json()
	if(not response["success"]):
		if('existe déjà' in response["msg"] or 'date actuelle' in response["msg"]):
			return STATUS.IGNORED
		print(f"\nEchec Facture {facture['invoice_number']}\n", response["msg"])
		return STATUS.FAILED
	return STATUS.SUCCESS