import requests
import json
import variables

headers = {}

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
			return False
	r = requests.post(
		variables.obr_url+"/addInvoice/",
		data=json.dumps(facture),
		headers=headers
	)
	if r.status_code == 403:
		if not login():
			return False
		return sendToOBR(facture)
	response = r.json()
	if(not response["success"]):
		if('existe déjà' in response["msg"]):
			return True
		print(f"\nEchec Facture {facture['invoice_number']}\n", response["msg"])
		return False
	return True