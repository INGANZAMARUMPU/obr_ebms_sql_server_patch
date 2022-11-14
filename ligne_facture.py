from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Facture:
    num_lign:int
    num_fact_papier:str
    type_cartes:str
    debut_plage:str
    fin_plage:str
    prix:int
    commission:int
    prix_achat:int
    commission_supplementaire:float
    quantite:int
    prix_vente:float
    operateur:str
    detaillant:float
    representant:float
    nom_carte:str
    lon_nums:int
    commission_motard:float

    def getLigneFact(self):
        pass


