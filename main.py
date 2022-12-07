import pyodbc
from facture import Facture
from datetime import datetime
import schedule
import time

import variables
from functions import *

def successCallBack(facture):
    with open("LAST.DAT", 'w') as file:
        last_date = datetime.strptime(facture.invoice_date, '%Y-%m-%d %H:%M:%S')
        file.write(last_date.strftime("%Y-%d-%m %H:%M:%S"))
        file.seek(0)

def updatedCallBack(facture, deleted_facture):
    successCallBack(facture)
    with open("DELETED.DAT", 'w') as file:
        last_date = datetime.strptime(deleted_facture.invoice_date, '%Y-%m-%d %H:%M:%S')
        file.write(last_date.strftime("%Y-%d-%m %H:%M:%S"))
        file.seek(0)

def sendCorrect(cursor, items, deleted_items):
    console_log(f"\nSENDING {len(items)} CORRECT INVOICES\n{'='*100}")
    for i, item in enumerate(items):
        facture = Facture(*item)
        facture.generateObrFact(cursor)
        deleted_facture = None
        
        if(len(deleted_items) > 0):
            deleted_facture = Facture(*deleted_items[0])
            facture.cancelled_invoice_ref = deleted_facture.invoice_ref
            console_log(f"[REPLACING] facture no. {deleted_facture.invoice_ref}")

        send_status = sendToOBR(facture.__dict__)
        if send_status == STATUS.SUCCESS:
            console_log(f"[SUCCESS] facture no. {facture.invoice_number}")
            successCallBack(facture)
            continue
        if send_status == STATUS.UPDATED:
            console_log(f"[UPDATED] facture no. {facture.cancelled_invoice_ref} replaced by facture no. {facture.invoice_number}")
            updatedCallBack(facture, deleted_facture)
            del deleted_items[0]
            continue
        elif send_status == STATUS.FAILED:
            console_log(f"[FAILED] facture no. {facture.invoice_number}")
            break
        console_log(f"[IGNORED] facture no. {facture.invoice_number}")

def sendDeleted(cursor, items):
    console_log(f"\nSENDING {len(items)} DELETED INVOICES\n{'='*100}")
    for i, item in enumerate(items):
        facture = Facture(*item)
        facture.generateObrFact(cursor)

        send_status = sendToOBR(facture.__dict__)
        console_log(f"[{send_status.value}] facture no. {facture.invoice_number}")

def main():
    console_log("connecting to the server")
    try:
        conn = pyodbc.connect(
            driver=variables.driver,
            host=variables.host,
            database=variables.database,
            user=variables.user,
            password=variables.password,
        )
        cursor = conn.cursor()
    except Exception as e:
        console_log(f"[SQL SERVER] {e}")
        return

    # reading min date for invoices to send
    with open("LAST.DAT", 'r') as file:
        min_date = file.readline() or "2022-25-11 00:00:00"
        console_log(f"NEW PROCESS STARTING FROM {min_date}")

    # reading min date for invoices to replace
    with open("DELETED.DAT", 'r') as file:
        min_del_date = file.readline() or "2022-25-11 00:00:00"

    # reading invoices to send
    try:
        query = genFactureQuery("Facture")
        # console_log(query)
        cursor.execute(query, variables.obr_nif, min_date)
        items = cursor.fetchall()
    except Exception as e:
        console_log(f"[SQL SERVER] {e}")
        return

    # reading invoices to replace
    try:
        query = genFactureQuery("facturedel")
        # console_log(query)
        cursor.execute(query, variables.obr_nif, min_del_date)
        deleted_items = cursor.fetchall()
    except Exception as e:
        console_log(f"[SQL SERVER] {e}")
        return

    sendDeleted(cursor, deleted_items)
    sendCorrect(cursor, items, deleted_items)

if __name__ == "__main__":
    main()
    # schedule.every(5).minutes.do(main)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)