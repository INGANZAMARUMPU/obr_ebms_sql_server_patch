import pyodbc
from facture import Facture
from datetime import datetime, timedelta
import schedule
import time

import variables
from functions import *

def writeInFile(file, facture):
    with open(f"{file}.DAT", 'w') as file:
        last_date = datetime.strptime(facture.invoice_date, '%Y-%m-%d %H:%M:%S')
        file.write(last_date.strftime("%Y-%d-%m %H:%M:%S"))
        file.seek(0)

def sendCorrect(cursor, items, deleted_items):
    console_log(f"\nSENDING {len(items)} CORRECT INVOICES\n{'='*50}")
    for i, item in enumerate(items):
        facture = Facture(*item)
        facture.generateObrFact(cursor, 'LigneFact')
        deleted_facture = None
        
        while 1:
            try:
                if(len(deleted_items) > 0):
                    deleted_facture = Facture(*deleted_items[0])
                    
                    deleted_date = datetime.strptime(deleted_facture.invoice_date, '%Y-%m-%d %H:%M:%S')
                    current_date = datetime.strptime(facture.invoice_date, '%Y-%m-%d %H:%M:%S')

                    if(deleted_date < current_date):
                        facture.cancelled_invoice_ref = deleted_facture.invoice_number
                        console_log(f"[REPLACING] facture no. {deleted_facture.invoice_number}")

                send_status = sendToOBR(facture.__dict__)
                if send_status == STATUS.SUCCESS:
                    console_log(f"[SUCCESS] facture no. {facture.invoice_number}")
                    writeInFile('LAST', facture)
                elif send_status == STATUS.UPDATED:
                    console_log(f"[UPDATED] facture no. {facture.cancelled_invoice_ref} replaced by facture no. {facture.invoice_number}")
                    writeInFile('LAST', facture)
                    writeInFile('DELETED', deleted_facture)
                    del deleted_items[0]
                elif send_status == STATUS.FAILED:
                    console_log(f"[FAILED] facture no. {facture.invoice_number}")
                    return 0
                else:
                    console_log(f"[IGNORED] facture no. {facture.invoice_number}")
                break
            except AlreadyDeletedException as e:
                console_log(str(e))
                writeInFile('DELETED', deleted_facture)
                if(len(deleted_items) > 0):
                    del deleted_items[0]

def sendDeleted(cursor, items):
    console_log(f"\nSENDING {len(items)} DELETED INVOICES\n{'='*50}")
    for i, item in enumerate(items):
        facture = Facture(*item)
        facture.generateObrFact(cursor, 'lignefactdel')

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

    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    max_date = tomorrow.strftime("%Y-%d-%m %H:%M:%S")

    # reading min date for invoices to send
    with open("LAST.DAT", 'r') as file:
        str_min_date = file.readline().strip() or "2023-19-01 00:00:00"
        console_log(f"NEW PROCESS STARTING FROM {str_min_date}")

    # reading min date for invoices to replace
    with open("DELETED.DAT", 'r') as file:
        str_min_del_date = file.readline().strip() or "2023-19-01 00:00:00"
        min_del_date = datetime.strptime(str_min_del_date, '%Y-%d-%m %H:%M:%S')
        if(min_del_date > today):
            yesterday = today - timedelta(days=1)
            str_min_del_date = yesterday.strftime("%Y-%d-%m %H:%M:%S")

    # reading invoices to send
    try:
        query = genFactureQuery("Facture")
        # console_log(query)
        cursor.execute(query, variables.obr_nif, str_min_date, max_date)
        items = cursor.fetchall()
    except Exception as e:
        console_log(f"[SQL SERVER] {e}")
        return

    # reading invoices to replace
    try:
        query = genFactureQuery("facturedel")
        # console_log(query)
        cursor.execute(query, variables.obr_nif, str_min_del_date, max_date)
        deleted_items = cursor.fetchall()
    except Exception as e:
        console_log(f"[SQL SERVER] {e}")
        return

    sendDeleted(cursor, deleted_items)
    sendCorrect(cursor, items, deleted_items)

if __name__ == "__main__":
    variables.DEBUG = True
    main()
    #schedule.every(5).minutes.do(main)

    #while True:
    #    schedule.run_pending()
    #    time.sleep(10)
