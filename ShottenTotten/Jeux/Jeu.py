from ShottenTotten.Jeux.Plateau import Plateau
from ShottenTotten.Jeux.Carte import generer_cartes, determiner_combinaison
from ShottenTotten.Jeux.Joueur import Joueur
import random
from collections import deque


class Jeu:
    """Classe principale pour gérer le déroulement du jeu."""

    Modes = {1: "Classique", 2: "Tactique", 3: "Expert"}

    def __init__(self):
        """Initialise les composants du jeu."""
        self.mode = None
        self.nbr_joueurs = None
        self.nbr_manche = None
        self.nbr_cartes = None
        self.plateau = Plateau()
        self.pioche = deque()
        self.joueurs = []

    def initialiser_cartes(self):
        """Initialise les cartes de clans et tactiques, puis mélange la pioche."""
        cartes_clans, cartes_tactiques = generer_cartes()
        self.pioche = melanger_pioche(cartes_clans, cartes_tactiques)

    def choisir_mode(self):
        """Demande à l'utilisateur de choisir un mode de jeu."""
        choix = demander_choix(
            "Choisis un mode de jeu :\n1) Classique\n2) Tactique\n3) Expert\n",
            lambda x: x in self.Modes,
        )
        self.mode = self.Modes[choix]

    def nombre_joueurs(self):
        """Demande à l'utilisateur de choisir le nombre de joueurs."""
        choix = demander_choix(
            "Choisis un type de partie :\n1) Joueur vs Joueur\n2) Joueur vs IA\n3) IA vs IA\n",
            lambda x: x in [1, 2, 3],
        )
        if choix == 1:
            self.nbr_joueurs = 2
        elif choix == 2:
            self.nbr_joueurs = 1
        elif choix == 3:
            self.nbr_joueurs = 0

    def configurer_joueurs(self):
        """Configure les joueurs et ajoute des IA si nécessaire."""
        for i in range(1, self.nbr_joueurs + 1):
            nom = input(f"Nom du joueur {i} : ")
            self.joueurs.append(Joueur(i, nom))

        # Ajouter des IA pour compléter à 2 joueurs
        while len(self.joueurs) < 2:
            self.joueurs.append(Joueur(len(self.joueurs) + 1, f"IA{len(self.joueurs) + 1}"))

    def nombre_manches(self):
        """Demande à l'utilisateur combien de manches vont être jouées."""
        self.nbr_manche = demander_choix(
            "Choisis un nombre de manches à jouer (1 à 5) :\n",
            lambda x: 1 <= x <= 5,
        )

    def distribuer_cartes(self):
        """Distribue les cartes aux joueurs au début de la partie."""
        for joueur in self.joueurs:
            for _ in range(self.nbr_cartes):
                joueur.piocher(self.pioche)

    def mode_classique(self):
        """Définit les caractéristiques du mode classique."""
        self.nbr_cartes = 6

    def mode_tactique(self):
        """Définit les caractéristiques du mode tactique."""
        self.nbr_cartes = 7

    def mode_expert(self):
        """Définit les caractéristiques du mode expert."""
        self.nbr_cartes = 7

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

    def tour_de_jeu(self):
        """Gère le déroulement d'une manche de jeu."""
        # Configuration du mode
        if self.mode == "Classique":
            self.mode_classique()
        elif self.mode == "Tactique":
            self.mode_tactique()
        elif self.mode == "Expert":
            self.mode_expert()

        # Distribution des cartes
        self.distribuer_cartes()

        # Tour de jeu
        while not self.fin_manche() and len(self.pioche) > 0:
            for joueur in self.joueurs:
                carte_index = self.choisir_carte(joueur) - 1
                borne_index = self.choisir_borne(joueur)
                joueur.jouer_carte(self.plateau, borne_index, joueur.main[carte_index])

                # Revendication de borne
                revendiquer = demander_choix(
                    "Veux-tu revendiquer une borne ? 1) Oui 2) Non\n",
                    lambda x: x in [1, 2],
                )
                if revendiquer == 1:
                    borne_index = self.choisir_borne_revendiquer(joueur)
                    self.comparaison_cartes(borne_index)
                    joueur.revendiquer_borne(self.plateau, borne_index)

                # Piocher une carte
                joueur.piocher(self.pioche)

    def verifier_fin_manche(self):
        """Vérifie les conditions de fin de manche."""
        for joueur in self.joueurs:
            # Vérifier si un joueur contrôle 5 bornes
            if joueur.borne_controlee == 5:
                return joueur, "5 bornes contrôlées"

            # Vérifier si un joueur contrôle 3 bornes consécutives
            consecutives = 0
            for numero_borne, borne in self.plateau.bornes.items():
                if borne.controle_par == joueur:
                    consecutives += 1
                    if consecutives == 3:
                        return joueur, "3 bornes consécutives"
                else:
                    consecutives = 0

        return None, None

    def fin_manche(self):
        """Définit la fin d'une manche."""
        gagnant, condition = self.verifier_fin_manche()
        if gagnant:
            print(f"{gagnant.nom} remporte la manche ({condition}).")
            return True
        print("La manche continue.")
        return False

    def fin_jeu(self):
        """Définit la fin du jeu."""
        gagnant = max(self.joueurs, key=lambda j: j.score)
        print(f"{gagnant.nom} remporte la partie avec {gagnant.score} points.")


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)


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
