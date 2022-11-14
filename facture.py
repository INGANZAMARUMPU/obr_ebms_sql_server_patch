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

    nom_cli:str
    prenom_cli:str
    nom_commercial:str
    type_:str
    commission_supplementaire:float
    nif:str

    province:str
    commune:str
    colline:str
    numero:str
    tele_fixe:str
    tele_mobile:str
    type_adresse:str

    def getLigneFact(self):
        pass


