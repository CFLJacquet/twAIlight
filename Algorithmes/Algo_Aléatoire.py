from Client_Joueur import JoueurClient
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Map import Map

class AlgoAleatoire(JoueurClient):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """
class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """
if __name__=="__main__":
    Joueur1=AlgoAleatoireInterne
    Joueur2 =AlgoAleatoireInterne
    Serveur=ServeurInterne(Map(),Joueur1,Joueur2)
    Serveur.start()
