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
cursor.execute("SELECT * FROM Facture WHERE DateFact >= '2019-30-04 00:00:00'")

for i in cursor:
    print(i)