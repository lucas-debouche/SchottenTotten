import random
from collections import deque

import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import displayCarte, deplacer_carte


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
        if self.joueurs[0].score != self.joueurs[1].score:
            gagnant = max(self.joueurs, key=lambda j: j.score)
            print(f"{gagnant.nom} remporte la partie avec {gagnant.score} points.")
        else :
            print("Il y a égalité.")
        pygame.quit()
        sys.exit()

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau, plateau, mode):
        """Gère le déroulement d'une manche de jeu."""
        running = True
        joueur = 0

        button_revendiquer = {"revendiquer": pygame.Rect(1050, 600, 200, 50)}
        button_passer = {"passer": pygame.Rect(1050, 660, 200, 50)}

        while running:
            # Vérifier les conditions de fin de partie
            gagnant, condition = self.verifier_fin_manche()
            if gagnant:
                print(f"{gagnant.nom} remporte la manche ({condition}).")
                break
            elif len(self.pioche) == 0:
                self.fin_jeu()
                break

            revendicable = False

            # Vérification d'activation du bouton Revendiquer
            for borne in self.bornes.values():
                if borne.controle_par is None:
                    if len(borne.joueur1_cartes) == 3 and len(borne.joueur2_cartes) == 3:
                        revendicable = True

            # Gérer les événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Dessiner les boutons avec leurs images
            for button_key, button_rect in buttons_plateau.items():
                screen_plateau.blit(buttons_images[button_key], button_rect.topleft)

            shadow_rect = button_revendiquer["revendiquer"].move(4, 4)
            pygame.draw.rect(screen_plateau, (160, 82, 45), shadow_rect, border_radius=10)

            shadow_rect = button_passer["passer"].move(4, 4)
            pygame.draw.rect(screen_plateau, (160, 82, 45), shadow_rect, border_radius=10)

            if revendicable and mode == "expert":
                button_color = (205, 200, 145)
            else:
                button_color = (169, 169, 169)  # Grise si non activable

            config_button(screen_plateau, button_color, button_revendiquer["revendiquer"], "Revendiquer")
            config_button(screen_plateau, (169, 169, 169), button_passer["passer"], "Passer")

            buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main)
            pygame.display.flip()

            carte_index = None
            carte_contour = None
            borne_contour = None
            borne_index = None
            borne_liste = None
            passer = False

            while not passer:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if carte_index is None:
                                if mode == "expert" and revendicable:
                                    if button_revendiquer["revendiquer"].collidepoint(event.pos):
                                        print("Borne revendiquée!")
                            else:
                                for borne_key, borne_rect in buttons_plateau.items():
                                    if borne_rect.collidepoint(event.pos):
                                        numero_borne = int(borne_key.replace("borne", ""))
                                        if joueur == 0:
                                            if len(plateau.bornes[numero_borne].joueur1_cartes) < 3 and plateau.bornes[
                                                numero_borne].controle_par is None:
                                                config_contour(borne_contour, screen_plateau, borne_rect, (205, 200, 145))
                                                borne_index = numero_borne
                                                borne_liste = plateau.bornes[numero_borne].joueur1_cartes
                                                borne_contour = borne_rect
                                            else:
                                                print("Tu ne peux pas jouer sur cette borne.")
                                        elif joueur == 1:
                                            if len(plateau.bornes[numero_borne].joueur2_cartes) < 3 and plateau.bornes[
                                                numero_borne].controle_par is None:
                                                config_contour(borne_contour, screen_plateau, borne_rect, (205, 200, 145))
                                                borne_index = numero_borne
                                                borne_liste = plateau.bornes[numero_borne].joueur2_cartes
                                                borne_contour = borne_rect
                                            else:
                                                print("Tu ne peux pas jouer sur cette borne.")
                            for carte_key, carte_rect in buttons.items():
                                if carte_rect.collidepoint(event.pos):
                                    config_button(screen_plateau, (169, 169, 169), button_revendiquer["revendiquer"], "Revendiquer")
                                    config_contour(carte_contour, screen_plateau, carte_rect, (255, 255, 255))
                                    carte_index = carte_key
                                    carte_contour = carte_rect

                            if carte_index is not None and borne_index is not None:
                                config_button(screen_plateau, (205, 200, 145), button_passer["passer"], "Passer")
                                if button_passer["passer"].collidepoint(event.pos):
                                    passer = True

            if borne_index is not None:
                deplacer_carte(screen_plateau, joueur, self.joueurs[joueur].main[carte_index], borne_index,
                               borne_liste)

            self.joueurs[joueur].jouer_carte(plateau, borne_index, self.joueurs[joueur].main[carte_index])
            self.joueurs[joueur].piocher(self.pioche)

            if revendicable and mode != "expert":
                button_color = (205, 200, 145)
            else:
                button_color = (169, 169, 169)  # Grise si non activable

            #config_button_revendiquer(screen_plateau, button_color, button_revendiquer["revendiquer"])
            pygame.display.flip()

            if mode != "expert":
                pass

            joueur = 1 - joueur
            afficher_pioche(screen_plateau, self.pioche)
            pygame.display.update()


def displayPlateau(plateau, mode):
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
    pioche_path = os.path.join(base_dir, "Ressources")
    borne_path = os.path.join(base_dir, "Ressources", "Bornes")
    images_paths = {
        "pioche": os.path.join(pioche_path, "Pioche.png"),
        "borne1": os.path.join(borne_path, "borne_0.jpg"),
        "borne2": os.path.join(borne_path, "borne_1.jpg"),
        "borne3": os.path.join(borne_path, "borne_2.jpg"),
        "borne4": os.path.join(borne_path, "borne_3.jpg"),
        "borne5": os.path.join(borne_path, "borne_4.jpg"),
        "borne6": os.path.join(borne_path, "borne_5.jpg"),
        "borne7": os.path.join(borne_path, "borne_6.jpg"),
        "borne8": os.path.join(borne_path, "borne_7.jpg"),
        "borne9": os.path.join(borne_path, "borne_8.jpg"),
    }

    # Boutons et leurs positions
    buttons = {
        "pioche": pygame.Rect(50, 300, 85, 150),
        **{f"borne{i}": pygame.Rect(210 + (i - 1) * 110, 350, 100, 50) for i in range(1, 10)},
    }

    # Chargement des images des boutons
    buttons_images = {}
    for i in range(1, 10):
        image_key = f"borne{i}"
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

        afficher_pioche(screen_plateau, plateau.pioche)
        plateau.tour_de_jeu(screen_plateau, buttons_images, buttons, plateau, mode)

        pygame.display.flip()


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def afficher_pioche(screen, pioche):
    rect_pioche = pygame.Rect(50, 455, 100, 40)  # Définir les dimensions du rectangle
    pygame.draw.rect(screen, (205, 200, 145), rect_pioche)

    smallfont = pygame.font.SysFont('Forte', 35)
    text_pioche = smallfont.render(str(len(pioche)), True, (139, 69, 19))
    rect_text = text_pioche.get_rect(center=rect_pioche.center)
    screen.blit(text_pioche, rect_text.topleft)

def load_and_scale_image(path, width, height):
    """Charge et redimensionne une image."""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image: {path}")
        raise e

def config_button(screen_plateau, button_color, button, text):
    smallfont = pygame.font.SysFont('Forte', 35)
    pygame.draw.rect(screen_plateau, button_color, button, border_radius=10)
    pygame.draw.rect(screen_plateau, (139, 69, 19), button, width=2, border_radius=10)
    text_jouer = smallfont.render(text, True, (139, 69, 19))
    text_rect_jouer = text_jouer.get_rect(center=button.center)
    screen_plateau.blit(text_jouer, text_rect_jouer)
    pygame.display.update(button)

def config_contour(contour, screen_plateau , rect, color):
    if contour is not None:
        pygame.draw.rect(screen_plateau, color, contour, width=2)
        pygame.display.update(contour)
    pygame.draw.rect(screen_plateau, (255, 0, 0), rect, width=2)
    pygame.display.update(rect)

