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
        Facture.numFact,
        Facture.numFactPapier,
        Facture.idUtil,
        Facture.idCli,
        Facture.dateFact,
        Facture.sommeFacture,
        Facture.commission,
        Facture.commissionRembourse,
        Facture.sommeRestante,
        Facture.autorisation,
        Facture.interet,
        Facture.commissionSupplementaire,
        Facture.commission_Supp_Rembourse,

        clients.nomCli,
        clients.prenomCli,
        clients.nomCommercial,
        clients.type,
        clients.comissionSupplentaire,
        clients.nif,

        adresseCli.province,
        adresseCli.commune,
        adresseCli.colline,
        adresseCli.numero,
        adresseCli.teleFixe,
        adresseCli.teleMobile,
        adresseCli.typeAdresse

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
"""

cursor.execute(query)

items = cursor.fetchall()
for item in items:
    # print(item)

    facture = Facture(*item)
    ligne_fact = facture.getLigneFact(cursor)
    print(f"========== {facture.num_fact} ==========")
    for ligne in ligne_fact:
        print(ligne)