from dataclasses import dataclass, field
from datetime import datetime

from ligne_facture import LigneFacture
import variables

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
        date = self.invoice_date.strftime("%Y%m%d%H%M%S")
        self.invoice_date = self.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
        # GENERATE NEW SIGNATURE
        self.invoice_signature = f"{variables.obr_nif}/{variables.obr_user}/{date}/{self.invoice_number}"
        self.invoice_signature_date = self.invoice_signature_date.strftime("%Y-%m-%d %H:%M:%S")
        self.invoice_items = []
        self.customer_TIN = self.customer_TIN or ""
        self.customer_address = self.customer_address or ""

    def generateObrFact(self, cursor, cancelled_invoice_ref=None):
        if(cancelled_invoice_ref):
            self.cancelled_invoice_ref = cancelled_invoice_ref

        query = """
            SELECT
                TypeCarte.NomCarte AS item_designation,
                1+CAST(LigneFact.FinPlage AS float)-CAST(LigneFact.DebutPlage AS float) AS item_quantity,
                LigneFact.prix AS item_price,
                0 AS item_ct,
                0 AS item_tl,
                LigneFact.prix*(
                    1+CAST(LigneFact.FinPlage AS float)-CAST(LigneFact.DebutPlage AS float)
                ) AS item_price_nvat,
                0 AS vat,
                LigneFact.prix*(
                    1+CAST(LigneFact.FinPlage AS float)-CAST(LigneFact.DebutPlage AS float)
                ) AS item_price_wvat,
                LigneFact.prix*(
                    1+CAST(LigneFact.FinPlage AS float)-CAST(LigneFact.DebutPlage AS float)
                ) AS item_total_amount
            FROM
                LigneFact
            JOIN
                TypeCarte
            ON 
                TypeCarte.TypeCarte = LigneFact.TypeCartes
            WHERE
                LigneFact.numFact = ?
        """

        cursor.execute(query, self.invoice_number)
        liste_lignes = cursor.fetchall()
        for ligne in liste_lignes:
            self.invoice_items.append(LigneFacture(*ligne).__dict__)

