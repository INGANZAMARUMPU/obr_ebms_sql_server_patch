from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class LigneFacture:
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
    long_nums:int

    def getLigneFact(self):
        pass


