# -*- coding: utf-8 -*-

from Joueur import Joueur
from Joueur_Interne import JoueurInterne
from Serveur_Interne import ServeurInterne
from Map import Map

class AlgoAleatoire(Joueur):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """
class AlgoAleatoireInterne(JoueurInterne):
    """
    Joueur avec la fonction de décision aléatoire de Charles
    """
    __vertices_created = 0

    @classmethod
    def nb_vertices_created(cls):
        return cls.__vertices_created

if __name__=="__main__":
    Joueur1=AlgoAleatoireInterne
    Joueur2 =AlgoAleatoireInterne
    Serveur=ServeurInterne(Map,Joueur1,Joueur2)
    Serveur.start()
