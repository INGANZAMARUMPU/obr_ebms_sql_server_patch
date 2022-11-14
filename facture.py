from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Facture:
    num_fact:str
    num_fact_papier:str
    id_util:str
    id_cli:int
    date_fact:datetime
    somme_facture:float
    commission:float
    commission_rembourse:bool
    somme_restante:float
    autorisation:str
    interet:float
    commission_supplementaire:float
    commission_supp_remobourse:bool

    def getLigneFact(self):
        pass


