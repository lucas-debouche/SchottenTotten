import random
from collections import deque

import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import displayCarte, deplacer_carte
from ShottenTotten.Jeux.Joueur import Joueur



class Borne:
    """Représente une borne sur le plateau avec des cartes et un contrôle."""

    def __init__(self):
        self.joueur1_cartes = []
        self.joueur2_cartes = []
        self.controle_par = None  # Joueur qui contrôle cette borne


def choisir_borne(buttons, joueur_id, plateau):
    """Permet au joueur de sélectionner la borne où il veut jouer."""
    while True:  # Boucle jusqu'à ce qu'une borne valide soit sélectionnée
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for borne_key, borne_rect in buttons.items():
                    if borne_rect.collidepoint(event.pos):
                        numero_borne = int(borne_key.replace("borne", ""))
                        if joueur_id == 0:
                            if len(plateau.bornes[numero_borne].joueur1_cartes) < 3 and plateau.bornes[numero_borne].controle_par is None:
                                try:
                                    # Extraire le numéro de la borne
                                    return numero_borne, plateau.bornes[numero_borne].joueur1_cartes
                                except ValueError:
                                    # Si ce n'est pas une borne valide, continuer
                                    pass
                            else:
                                print(f"La borne {borne_key} est déjà controllée.")
                        elif joueur_id == 1:
                            if len(plateau.bornes[numero_borne].joueur2_cartes) < 3 and plateau.bornes[numero_borne].controle_par is None:
                                try:
                                    # Extraire le numéro de la borne
                                    return numero_borne, plateau.bornes[numero_borne].joueur2_cartes
                                except ValueError:
                                    # Si ce n'est pas une borne valide, continuer
                                    pass
                            else:
                                print(f"La borne {borne_key} est déjà controllée.")

def choisir_carte(screen, buttons):
    """Permet au joueur de sélectionner la carte qu'il veut jouer"""
    while True:  # Boucle jusqu'à ce qu'une borne valide soit sélectionnée
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for borne_key, borne_rect in buttons.items():
                    if borne_rect.collidepoint(event.pos):
                        try:
                            pygame.draw.rect(screen, (255, 0, 0), borne_rect, width=3)
                            pygame.display.update(borne_rect)
                            # Extraire le numéro de la carte
                            return borne_key
                        except ValueError:
                            # Si ce n'est pas une borne valide, continuer
                            pass

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

    def fin_jeu(self):
        """Définit la fin du jeu."""
        gagnant = max(self.joueurs, key=lambda j: j.score)
        print(f"{gagnant.nom} remporte la partie avec {gagnant.score} points.")

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau, plateau):
        """Gère le déroulement d'une manche de jeu."""
        running = True
        joueur = 0

        while running:
            # Vérifier les conditions de fin de partie
            gagnant, condition = self.verifier_fin_manche()
            if gagnant:
                print(f"{gagnant.nom} remporte la manche ({condition}).")
                break
            elif len(self.pioche) == 0:
                self.fin_jeu()
                break

            # Gérer les événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Dessiner les boutons avec leurs images
            for button_key, button_rect in buttons_plateau.items():
                screen_plateau.blit(buttons_images[button_key], button_rect.topleft)

            buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main)
            pygame.display.flip()

            carte_index = None
            borne_index = None

            while carte_index is None or borne_index is None:
                # Sélection de la carte
                if carte_index is None:
                    carte_index = choisir_carte(screen_plateau, buttons)
                    if carte_index is not None:
                        print(f"Carte choisie : {carte_index}")

                # Sélection de la borne
                if carte_index is not None and borne_index is None:
                    borne_index, borne_liste = choisir_borne(buttons_plateau, joueur, plateau)
                    if borne_index is not None:
                        print(f"Borne choisie : {borne_index}")
                        deplacer_carte(screen_plateau, joueur, self.joueurs[joueur].main[carte_index], borne_index, borne_liste)


            #Enlever la carte de la main
            self.joueurs[joueur].jouer_carte(plateau, borne_index, self.joueurs[joueur].main[carte_index])

            #Revendiquer une borne
            for borne in self.bornes.values():
                if borne.controle_par is None:
                    if len(borne.joueur1_cartes) == 3 and len(borne.joueur2_cartes) == 3:
                        #Créer le bouton pour revendiquer et l'afficher
                        pass
                                    
            #Piocher une carte
            self.joueurs[joueur].piocher(self.pioche)

            joueur = 1 - joueur

            rect_pioche = pygame.Rect(50, 455, 100, 40)  # Définir les dimensions du rectangle
            pygame.draw.rect(screen_plateau, (205, 200, 145), rect_pioche)

            smallfont = pygame.font.SysFont('Forte', 35)
            text_pioche = smallfont.render(str(len(self.pioche)), True, (139, 69, 19))
            rect_text = text_pioche.get_rect(center=rect_pioche.center)
            screen_plateau.blit(text_pioche, rect_text.topleft)

            # Rafraîchir l'écran après chaque tour
            pygame.display.update()



            '''
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

        plateau.tour_de_jeu(screen_plateau, buttons_images, buttons, plateau)

        pygame.display.flip()


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def afficher_pioche(screen, pioche):
    smallfont = pygame.font.SysFont('Forte', 35)
    text_pioche = smallfont.render(str(len(pioche)), True, (139, 69, 19))
    screen.blit(text_pioche, (160, 250))

def load_and_scale_image(path, width, height):
    """Charge et redimensionne une image."""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image: {path}")
        raise e
