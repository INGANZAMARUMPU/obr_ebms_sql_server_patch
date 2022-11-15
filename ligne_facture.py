from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class LigneFacture:
    item_designation:str
    item_quantity:str
    item_price:str
    item_ct:str
    item_tl:str
    item_price_nvat:str
    vat:str
    item_price_wvat:str
    item_total_amount:str

    def getLigneFact(self):
        pass


