import pyodbc

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
    SELECT * FROM
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
        DateFact >= '2019-30-04 00:00:00'
"""

cursor.execute(query)

for i in cursor:
    print(i)