from dataclasses import dataclass, field
from datetime import datetime

from ligne_facture import LigneFacture

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
    commission_supp_rembourse:bool

    nom_cli:str
    prenom_cli:str
    nom_commercial:str
    type_:str
    comission_supplementaire:float
    nif:str

    province:str
    commune:str
    colline:str
    numero:str
    tele_fixe:str
    tele_mobile:str
    type_adresse:str
    liste_lignes:list = field(init=False)

    def __post_init__(self):
        self.liste_lignes = []

    def generateObrFact(self, cursor):

        query = """
            SELECT
                LigneFact.NumLign,
                LigneFact.NumFact,
                LigneFact.TypeCartes,
                LigneFact.DebutPlage,
                LigneFact.FinPlage,
                LigneFact.prix,
                LigneFact.commission,
                LigneFact.Commission_Supplementaire,
                LigneFact.quantite,

                TypeCarte.Prix_Achat,
                TypeCarte.Prix_Vente,
                TypeCarte.Operateur,
                TypeCarte.Détaillant,
                TypeCarte.Représentant,
                TypeCarte.nomCarte,
                TypeCarte.longNums
            FROM
                LigneFact
            JOIN
                TypeCarte
            ON 
                TypeCarte.TypeCarte = LigneFact.TypeCartes
            WHERE
                LigneFact.numFact = '{}'
        """.format(self.num_fact)

        cursor.execute(query)
        liste_lignes = cursor.fetchall()
        for ligne in liste_lignes:
            self.liste_lignes.append(LigneFacture(*ligne))

