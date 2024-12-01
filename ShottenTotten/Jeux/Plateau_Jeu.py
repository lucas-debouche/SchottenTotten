import pygame
import sys
import os

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

    def ajouter_carte(self, numero_borne, joueur_index, carte):
        """Ajoute une carte à une borne pour un joueur."""
        borne = self.bornes[numero_borne]
        if joueur_index == 0:
            borne.joueur1_cartes.append(carte)
        elif joueur_index == 1:
            borne.joueur2_cartes.append(carte)
        else:
            raise ValueError("Index du joueur invalide.")

class Display:
    def displayPlateau(self):
        """Fonction qui affiche le plateau"""
        pygame.init()

        """Initialisation de de la fenetre"""
        window_height = 750
        window_width = 1280
        pygame.display.set_caption("Schotten Totten : Jeux")
        screen_plateau = pygame.display.set_mode((window_width, window_height))

        current_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        pioche_path = os.path.join(base_dir, "Ressources", "Pioche.png")
        borne1_path = os.path.join(base_dir, "Ressources", "Frontiere1.png")
        borne2_path = os.path.join(base_dir, "Ressources", "Frontiere2.png")
        borne3_path = os.path.join(base_dir, "Ressources", "Frontiere3.png")

        buttons = {"pioche": pygame.Rect(50, 275, 85, 150),
                   "borne1": pygame.Rect(210, 300, 100, 100),
                   "borne2": pygame.Rect(320, 300, 100, 100),
                   "borne3": pygame.Rect(430, 300, 100, 100),
                   "borne4": pygame.Rect(540, 300, 100, 100),
                   "borne5": pygame.Rect(650, 300, 100, 100),
                   "borne6": pygame.Rect(760, 300, 100, 100),
                   "borne7": pygame.Rect(870, 300, 100, 100),
                   "borne8": pygame.Rect(980, 300, 100, 100),
                   "borne9": pygame.Rect(1090, 300, 100, 100),
                  }
        buttons_images = {"pioche": pioche_path,
                          "borne1": borne1_path,
                          "borne2": borne2_path,
                          "borne3": borne3_path,
                         }

        # Charger et redimensionner les images des boutons
        pioche_button_image = pygame.image.load(buttons_images["pioche"])
        pioche_button_image = pygame.transform.scale(pioche_button_image,(buttons["pioche"].width, buttons["pioche"].height))

        borne1_button_image = pygame.image.load(buttons_images["borne1"])
        borne1_button_image = pygame.transform.scale(borne1_button_image,(buttons["borne1"].width, buttons["borne1"].height))

        borne2_button_image = pygame.image.load(buttons_images["borne2"])
        borne2_button_image = pygame.transform.scale(borne2_button_image,(buttons["borne2"].width, buttons["borne2"].height))

        borne3_button_image = pygame.image.load(buttons_images["borne3"])
        borne3_button_image = pygame.transform.scale(borne3_button_image,(buttons["borne3"].width, buttons["borne3"].height))

        borne4_button_image = pygame.image.load(buttons_images["borne1"])
        borne4_button_image = pygame.transform.scale(borne4_button_image,(buttons["borne1"].width, buttons["borne1"].height))

        borne5_button_image = pygame.image.load(buttons_images["borne2"])
        borne5_button_image = pygame.transform.scale(borne5_button_image,(buttons["borne2"].width, buttons["borne2"].height))

        borne6_button_image = pygame.image.load(buttons_images["borne3"])
        borne6_button_image = pygame.transform.scale(borne6_button_image,(buttons["borne3"].width, buttons["borne3"].height))

        borne7_button_image = pygame.image.load(buttons_images["borne1"])
        borne7_button_image = pygame.transform.scale(borne7_button_image,(buttons["borne1"].width, buttons["borne1"].height))

        borne8_button_image = pygame.image.load(buttons_images["borne2"])
        borne8_button_image = pygame.transform.scale(borne8_button_image,(buttons["borne2"].width, buttons["borne2"].height))

        borne9_button_image = pygame.image.load(buttons_images["borne3"])
        borne9_button_image = pygame.transform.scale(borne9_button_image,(buttons["borne3"].width, buttons["borne3"].height))


        menu_running = True

        while menu_running:
            screen_plateau.fill((205, 200, 145))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    pygame.quit()
                    sys.exit()  # Arret du programme

            # Dessiner les boutons avec images
            screen_plateau.blit(pioche_button_image, buttons["pioche"].topleft)
            screen_plateau.blit(borne1_button_image, buttons["borne1"].topleft)
            screen_plateau.blit(borne2_button_image, buttons["borne2"].topleft)
            screen_plateau.blit(borne3_button_image, buttons["borne3"].topleft)
            screen_plateau.blit(borne4_button_image, buttons["borne4"].topleft)
            screen_plateau.blit(borne5_button_image, buttons["borne5"].topleft)
            screen_plateau.blit(borne6_button_image, buttons["borne6"].topleft)
            screen_plateau.blit(borne7_button_image, buttons["borne7"].topleft)
            screen_plateau.blit(borne8_button_image, buttons["borne8"].topleft)
            screen_plateau.blit(borne9_button_image, buttons["borne9"].topleft)
            pygame.display.flip()