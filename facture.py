from dataclasses import dataclass, field
from datetime import datetime

from ligne_facture import LigneFacture

@dataclass
class Facture:
    invoice_number:str
    invoice_date:str
    invoice_type:str
    tp_type:str
    tp_name:str
    tp_TIN:str
    tp_trade_number:str
    tp_postal_number:str
    tp_phone_number:str
    tp_address_province:str
    tp_address_commune:str
    tp_address_quartier:str
    tp_address_avenue:str
    tp_address_number:str
    vat_taxpayer:str
    ct_taxpayer:str
    tl_taxpayer:str
    tp_fiscal_center:str
    tp_activity_sector:str
    tp_legal_form:str
    payment_type:str
    invoice_currency:str
    customer_name:str
    customer_TIN:str
    customer_address:str
    vat_customer_payer:str
    cancelled_invoice_ref:str
    invoice_ref:str
    invoice_signature:str
    invoice_signature_date:str
    invoice_items:list = field(init=False)

    def __post_init__(self):
        self.invoice_items = []

    def generateObrFact(self, cursor):

        query = """
            SELECT
                TypeCarte.NomCarte AS item_designation,
                LigneFact.quantite AS item_quantity,
                LigneFact.prix AS item_price,
                0 AS item_ct,
                0 AS item_tl,
                LigneFact.prix AS item_price_nvat,
                0 AS vat,
                LigneFact.prix AS item_price_wvat,
                LigneFact.prix AS item_total_amount
            FROM
                LigneFact
            JOIN
                TypeCarte
            ON 
                TypeCarte.TypeCarte = LigneFact.TypeCartes
            WHERE
                LigneFact.numFact = '{}'
        """.format(self.invoice_number)

        cursor.execute(query)
        liste_lignes = cursor.fetchall()
        for ligne in liste_lignes:
            self.invoice_items.append(LigneFacture(*ligne).__dict__)

