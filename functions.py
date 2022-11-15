import requests
import json
import variables

base_url = "https://ebms.obr.gov.bi:9443/ebms_api"
token = ''

def login():
	data = {
		"username": variables.obr_user,
		"password": variables.obr_pass
	}
	r  = requests.post(base_url+"/login/", data=json.dumps(data))
	return r.json()

def sendToOBR(facture):
	global token
	if token == "":
		try:
			token = login()["result"]["token"]
		except Exception:
			return False
	return False