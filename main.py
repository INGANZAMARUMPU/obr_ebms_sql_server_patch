import pyodbc

from facture import Facture
import variables

conn = pyodbc.connect(
    driver=variables.driver,
    host=variables.host,
    database=variables.database,
    user=variables.user,
    password=variables.password,
)

cursor = conn.cursor()

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
        clients.nomCli+' '+clients.prenomCli+' '+clients.nomCommercial AS customer_name,
        clients.nif AS customer_TIN,
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
        Facture.DateFact >= '2019-30-04 00:00:00'
    ORDER BY
        Facture.DateFact
"""

cursor.execute(query, variables.obr_nif)

items = cursor.fetchall()
for item in items:
    # print(item)

    facture = Facture(*item)
    ligne_fact = facture.generateObrFact(cursor)
    print(f"========== {facture.invoice_number} {facture.invoice_date} ==========")
    print(facture.__dict__)
    break
    # for ligne in ligne_fact:
    #     print(ligne)