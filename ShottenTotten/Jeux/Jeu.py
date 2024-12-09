from ShottenTotten.Jeux.Plateau import Plateau, displayPlateau
from ShottenTotten.Jeux.Carte import generer_cartes, determiner_combinaison, displayCarte
from ShottenTotten.Jeux.Joueur import Joueur
from ShottenTotten.Jeux.Menu import Menu
import random
from collections import deque


class Jeu:
    """Classe principale pour gérer le déroulement du jeu."""

    Modes = {1: "Classique", 2: "Tactique", 3: "Expert"}

    menu = Menu()

    def __init__(self):
        """Initialise les composants du jeu."""
        self.plateau = Plateau()
        self.pioche = deque()


    def choisir_carte(self, joueur):
        """Demande à un joueur de choisir une carte."""
        return demander_choix(
            f"{joueur.nom}, choisis une carte à jouer (1 à {len(joueur.main)}) :\n",
            lambda x: 1 <= x <= len(joueur.main),
        )

    def choisir_borne(self, joueur):
        """Demande à un joueur de choisir une borne où jouer une carte."""
        return demander_choix(
            f"{joueur.nom}, choisis une borne (1 à 9) :\n",
            lambda x: 1 <= x <= 9 and len(self.plateau.bornes[x].joueur1_cartes) < 3,
        )

    def choisir_borne_revendiquer(self, joueur):
        """Demande à un joueur de choisir une borne à revendiquer."""
        return demander_choix(
            f"{joueur.nom}, choisis une borne à revendiquer (1 à 9) :\n",
            lambda x: 1 <= x <= 9 and self.plateau.bornes[x].controle_par is None,
        )

    def comparaison_cartes(self, numero_borne):
        """Compare les cartes des joueurs pour trouver la meilleure combinaison"""
        j1 = determiner_combinaison(self.plateau.bornes[numero_borne].joueur1_cartes)
        j2 = determiner_combinaison(self.plateau.bornes[numero_borne].joueur2_cartes)
        if j1<j2:
            return self.joueurs[0]
        else:
            return self.joueurs[1]







    def fin_jeu(self):
        """Définit la fin du jeu."""
        gagnant = max(self.joueurs, key=lambda j: j.score)
        print(f"{gagnant.nom} remporte la partie avec {gagnant.score} points.")





def demander_choix(message, condition):
    """Demande un choix valide à l'utilisateur."""
    while True:
        try:
            choix = int(input(message))
            if condition(choix):
                return choix
            print("Choix invalide. Réessayez.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre.")
