import random
from collections import deque

import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import displayCarte
from ShottenTotten.Jeux.Joueur import Joueur


class Borne:
    """Représente une borne sur le plateau avec des cartes et un contrôle."""

    def __init__(self):
        self.joueur1_cartes = []
        self.joueur2_cartes = []
        self.controle_par = None  # Joueur qui contrôle cette borne


class Plateau:
    """Représente le plateau de jeu avec ses bornes et sa défausse."""

    def __init__(self, nombre_bornes=9):
        self.bornes = {i: Borne() for i in range(1, nombre_bornes + 1)}
        self.defausse = []
        self.pioche = deque()
        self.nbr_cartes = None
        self.joueurs = []
        self.nbr_joueurs = None

    def ajouter_carte(self, numero_borne, joueur_index, carte):
        """Ajoute une carte à une borne pour un joueur."""
        if numero_borne not in self.bornes:
            raise ValueError(f"Borne {numero_borne} n'existe pas.")
        borne = self.bornes[numero_borne]
        if joueur_index == 0:
            borne.joueur1_cartes.append(carte)
        elif joueur_index == 1:
            borne.joueur2_cartes.append(carte)
        else:
            raise ValueError("Index du joueur invalide.")





    def configurer_joueurs(self):
        """Configure les joueurs et ajoute des IA si nécessaire."""
        if self.nbr_joueurs == 0:
            self.joueurs.append(Joueur(0, f"IA{1}"))
            self.joueurs.append(Joueur(1, f"IA{2}"))
        #A changer avec la fonction pour demander le nom
        elif self.nbr_joueurs == 1:
            self.joueurs.append(Joueur(0, f"IA{1}"))
            self.joueurs.append(Joueur(1, f"IA{2}"))
        elif self.nbr_joueurs == 2:
            self.joueurs.append(Joueur(0, f"IA{1}"))
            self.joueurs.append(Joueur(1, f"IA{2}"))

    def distribuer_cartes(self):
        """Distribue les cartes aux joueurs au début de la partie."""
        for joueur in self.joueurs:
            for i in range(self.nbr_cartes):
                joueur.piocher(self.pioche)

    def verifier_fin_manche(self):
        """Vérifie les conditions de fin de manche."""
        for joueur in self.joueurs:
            # Vérifier si un joueur contrôle 5 bornes
            if joueur.borne_controlee == 5:
                return joueur, "5 bornes contrôlées"

            # Vérifier si un joueur contrôle 3 bornes consécutives
            consecutives = 0
            for numero_borne, borne in self.bornes.items():
                if borne.controle_par == joueur:
                    consecutives += 1
                    if consecutives == 3:
                        return joueur, "3 bornes consécutives"
                else:
                    consecutives = 0

        return None, None

    def choisir_carte(self, buttons):
        """Permet au joueur de sélectionner la carte qu'il veut jouer"""
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].collidepoint(event.pos):
                    # Prendre l'index de la carte 0 dans la main
                    return 0
                if buttons[1].collidepoint(event.pos):
                    # Prendre l'index de la carte 1 dans la main
                    return 1
                if buttons[2].collidepoint(event.pos):
                    # Prendre l'index de la carte 2 dans la main
                    return 2
                if buttons[3].collidepoint(event.pos):
                    # Prendre l'index de la carte 3 dans la main
                    return 3
                if buttons[4].collidepoint(event.pos):
                    # Prendre l'index de la carte 4 dans la main
                    return 4
                if buttons[5].collidepoint(event.pos):
                    # Prendre l'index de la carte 5 dans la main
                    return 5
                if self.nbr_cartes == 7:
                    if buttons[6].collidepoint(event.pos):
                        # Prendre l'index de la carte 6 dans la main
                        return 6

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau):
        """Gère le déroulement d'une manche de jeu."""
        running = True

        joueur = 0

        while running:
            # Vérifier les conditions de fin de partie
            gagnant, condition = self.verifier_fin_manche()
            if gagnant:
                print(f"{gagnant.nom} remporte la manche ({condition}).")
                running = False
                break
            elif len(self.pioche) == 0:
                break

            # Gérer les événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Afficher le plateau de jeu
            screen_plateau.fill((205, 200, 145))  # Fond de la fenêtre
            # Dessiner les boutons avec leurs images
            for button_key, button_rect in buttons_plateau.items():
                screen_plateau.blit(buttons_images[button_key], button_rect.topleft)

            buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main)
            pygame.display.flip()

            # Sélection de la carte
            carte_index = self.choisir_carte(buttons)
            if carte_index is None:
                continue  # Attendre une sélection valide
            print(f"Carte choisie : {self.joueurs[joueur].main[carte_index]}, Joueur : {self.joueurs[joueur].nom}")



            if joueur == 0:
                joueur += 1
            else:
                joueur -= 1
            print(joueur)

            # Rafraîchir l'écran après chaque tour
            pygame.display.update()



            '''borne_index = self.choisir_borne(joueur)
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
                joueur.piocher(self.pioche)'''


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def load_and_scale_image(path, width, height):
    """Charge et redimensionne une image."""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image: {path}")
        raise e


def displayPlateau(plateau):
    """Fonction qui affiche le plateau."""
    pygame.init()

    # Initialisation de la fenêtre
    window_height = 750
    window_width = 1280
    pygame.display.set_caption("Schotten Totten : Jeux")
    screen_plateau = pygame.display.set_mode((window_width, window_height))

    # Récupération des chemins d'images
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    resources_dir = os.path.join(base_dir, "Ressources")
    images_paths = {
        "pioche": os.path.join(resources_dir, "Pioche.png"),
        "borne1": os.path.join(resources_dir, "Frontiere1.png"),
        "borne2": os.path.join(resources_dir, "Frontiere2.png"),
        "borne3": os.path.join(resources_dir, "Frontiere3.png"),
    }

    # Boutons et leurs positions
    buttons = {
        "pioche": pygame.Rect(50, 300, 85, 150),
        **{f"borne{i}": pygame.Rect(210 + (i - 1) * 110, 325, 100, 100) for i in range(1, 10)},
    }

    # Chargement des images des boutons
    buttons_images = {}
    for i in range(1, 10):
        image_key = f"borne{((i - 1) % 3) + 1}"  # Utilise un cycle des trois images
        buttons_images[f"borne{i}"] = load_and_scale_image(
            images_paths[image_key],
            buttons[f"borne{i}"].width,
            buttons[f"borne{i}"].height,
        )
    buttons_images["pioche"] = load_and_scale_image(
        images_paths["pioche"], buttons["pioche"].width, buttons["pioche"].height
    )

    menu_running = True

    while menu_running:
        screen_plateau.fill((205, 200, 145))  # Fond de la fenêtre

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                sys.exit()  # Arrêt du programme

        plateau.tour_de_jeu(screen_plateau, buttons_images, buttons)

        pygame.display.flip()


