import pyodbc
from facture import Facture
from tqdm import tqdm
from datetime import datetime
import schedule 
import time 

import variables
from functions import *

def main():
    print("connecting to the server")
    conn = pyodbc.connect(
        driver=variables.driver,
        host=variables.host,
        database=variables.database,
        user=variables.user,
        password=variables.password,
    )

    cursor = conn.cursor()

    with open("LAST.DAT", 'r') as file:
        min_date = file.readline() or "2018-16-11 00:00:00"
        print(f"NEW PROCESS STARTING ON {min_date}")

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
            Facture.numFact AS invoice_ref,
            Facture.signatureobr AS invoice_signature,
            Facture.dateFact AS invoice_signature_date
        FROM
            Facture
        JOIN
            clients
        ON 
            Facture.idCli = clients.IdCli
        LEFT OUTER JOIN
            adresseCli
        ON
            Facture.IdCli = adresseCli.IdCli
        WHERE
            Facture.DateFact > ?
        ORDER BY
            Facture.DateFact
    """

    print("Sending SQL QUERY")
    # print(query)
    cursor.execute(query, variables.obr_nif, min_date)

    items = cursor.fetchall()

    print(f"iteration on {len(items)} got from db")
    # for item in tqdm(items):
    for i, item in enumerate(items):
        facture = Facture(*item)
        facture.generateObrFact(cursor)
        send_status = sendToOBR(facture.__dict__)
        if send_status == STATUS.SUCCESS:
            print(f"[SUCCESS] facture no. {facture.invoice_number}")
            with open("LAST.DAT", 'w') as file:
                last_date = datetime.strptime(facture.invoice_date, '%Y-%m-%d %H:%M:%S')
                file.write(last_date.strftime("%Y-%d-%m %H:%M:%S"))
                file.seek(0)
            continue
        elif send_status == STATUS.FAILED:
            print(f"[FAILED] facture no. {facture.invoice_number}")
            break
        print(f"[IGNORED] facture no. {facture.invoice_number}")

if __name__ == "__main__":
    main()
    # schedule.every(10).minutes.do(main)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)