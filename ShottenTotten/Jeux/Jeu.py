from Jeux.Plateau import Plateau
from Jeux.Carte import generer_cartes
from Jeux.Joueur import Joueur


from ShottenTotten.Jeux.Joueur import Joueur


class Jeu:
    """Classe principale pour gérer le déroulement du jeu."""
    Modes = {1: "Classique", 2: "Tactique", 3: "Expert"}

    def __init__(self):
        self.mode = None
        self.nbr_joueurs = None
        self.plateau = Plateau()
        self.pioche = []
        self.joueurs = []

    def initialiser_cartes(self):
        """Initialise les cartes et mélange la pioche."""
        cartes_clans, cartes_tactiques = generer_cartes()
        self.pioche = cartes_clans + cartes_tactiques

    def choisir_mode(self):
        """Demande à l'utilisateur de choisir un mode de jeu."""
        while True:
            try:
                choix = int(input("Choisis un mode de jeu :\n1) Classique\n2) Tactique\n3) Expert\n"))
                if choix in self.Modes:
                    self.mode = self.Modes[choix]
                    break
                else:
                    print("Choix invalide. Réessayez.")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un nombre.")

    def nombre_joueurs(self):
        """Demande à l'utilisateur de choisir le nombre de joueurs."""
        i = 0
        while i == 0:
            try:
                choix = int(input("Choisis un nombre de joueur :\n1) Joueur vs Joueur\n2) Joueur vs IA\n3) IA vs IA\n"))
                if choix == 1:
                    self.nbr_joueurs = 2
                    break
                elif choix == 2:
                    self.nbr_joueurs = 1
                    break
                elif choix == 3:
                    self.nbr_joueurs = 0
                    break
                else:
                    print("Choix invalide. Réessayez.")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un nombre.")

    def configurer_joueurs(self):
        """Configure les joueurs selon le type de partie."""
        for i in range(1, self.nbr_joueurs + 1):
            nom = input(f"Nom du joueur {i} : ")
            self.joueurs.append(Joueur(nom))

        # Ajouter des IA si nécessaire
        i = 0
        while len(self.joueurs) < 2:
            self.joueurs.append(Joueur("IA" + str(i)))
            i += 1

    def tour_de_jeu(self):
        """Méthode pour décrire un tour de jeu."""

    def fin_manche(self):
        """Méthode pour définir la fin d'une manche."""

        # Vérification si un joueur contrôle 5 bornes
        for joueur in self.joueurs:
            if joueur.borne_controlee == 5:
                print(str(joueur.nom) + " remporte la manche.")
                for j in self.joueurs:
                    print(f"{j.nom} marque {j.borne_controlee} points.")
                    j.score += j.borne_controlee
                return

        # Vérification si un joueur contrôle 3 bornes consécutives
        for joueur in self.joueurs:
            if joueur.borne_controlee >= 3:
                consecutif = 0
                for numero_borne, borne in self.plateau.bornes.items():
                    if borne[1] == joueur:
                        consecutif += 1
                        if consecutif == 3:
                            print(f"{joueur.nom} remporte la manche et marque 5 points.")
                            joueur.score += joueur.borne_controlee
                            for j in filter(lambda x: x != joueur, self.joueurs):
                                print(f"{j.nom} marque {j.borne_controlee} points.")
                                j.score += j.borne_controlee
                            return
                    else:
                        consecutif = 0
        # Si aucune condition de victoire n'est remplie
        print("La manche continue. Aucun vainqueur pour l'instant.")





    def fin_jeu(self):
        """Méthode pour définir la fin du jeu."""
        if self.joueurs[0].score >= self.joueurs[1].score:
            print(str(self.joueurs[0].nom) + " a gagné !")
        else :
            print(str(self.joueurs[1].nom) + " a gagné !")

    # Ajoutez ici d'autres méthodes pour gérer le jeu (tour de jeu, règles, etc.)
