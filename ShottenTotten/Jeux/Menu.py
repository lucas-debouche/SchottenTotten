import pygame
import math
import sys
import os


class Menu :

    def __init__(self):
        self.classic_mode = False
        self.tactic_mode = False
        self.expert_mode = False

    def displayAcceuil(self):
        """Fonction qui affiche l'acceuil de bienvenue"""
        pygame.init()

        pygame.display.set_caption("Schotten Totten")
        screen_acceuil = pygame.display.set_mode((600,750))

        current_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        background_path = os.path.join(base_dir, "Ressources", "Acceuil.png")
        background = pygame.image.load(background_path)

        """Création des boutons"""
        smallfont = pygame.font.SysFont('Forte', 35)
        buttons = {"Jouer": pygame.Rect(225, 600, 120, 50)}

        menu_running = True

        while menu_running:
            screen_acceuil.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    pygame.quit()
                    sys.exit() #Arret du programme
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons["Jouer"].collidepoint(event.pos):
                        """Lancer le menu quand le bouton jouer est présser"""
                        self.displayMenu()

            """Dessiner les boutons"""
            pygame.draw.rect(screen_acceuil, (205, 200, 145), buttons["Jouer"])
            text_jouer = smallfont.render("Jouer", True, (255, 45, 0))
            screen_acceuil.blit(text_jouer, (buttons["Jouer"].x + 20, buttons["Jouer"].y + 5))

            pygame.display.flip()

    def displayMenu(self):
        """Fonction qui affiche le menu et permet de récuperer les infos pour initialiser la partie souhaité"""
        os.environ['SDL_VIDEO_CENTERED'] = '1' #Centrer la fenetre sur l'ecran

        """Initialisation de de la fenetre"""
        window_height = 750
        window_width = 1280

        pygame.display.set_caption("Schotten Totten : Menu")
        screen_menu = pygame.display.set_mode((window_width, window_height))

        current_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        background_path = os.path.join(base_dir, "Ressources", "Menu.png")
        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (window_width, window_height))

        """Création des boutons"""
        smallfont = pygame.font.SysFont('Forte', 35)
        button_height = 50
        button_width = 200

        buttons = {"classic": pygame.Rect(200, 200, button_width, button_height),
                "tactic": pygame.Rect(500, 200, button_width, button_height),
                "expert": pygame.Rect(800, 200, button_width, button_height),
               }

        title_font = pygame.font.SysFont('Forte', 75)
        text_Menu = title_font.render("Menu", True, (55, 100, 255))

        menu_running = True

        while menu_running:
            screen_menu.blit(background, (0, 0))

            # Afficher le texte "Menu" à la position (500, 200)
            screen_menu.blit(text_Menu, (550, 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    pygame.quit()
                    sys.exit() #Arret du programme
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons["classic"].collidepoint(event.pos):
                        """Activer le mode classique et désactiver les autres"""
                        self.classic_mode = True
                        self.tactic_mode = False
                        self.expert_mode = False
                    elif buttons["tactic"].collidepoint(event.pos):
                        """Activer le mode tactique et désactiver les autres"""
                        self.classic_mode = False
                        self.tactic_mode = True
                        self.expert_mode = False
                    elif buttons["expert"].collidepoint(event.pos):
                        """Activer le mode expert et désactiver les autres"""
                        self.classic_mode = False
                        self.tactic_mode = False
                        self.expert_mode = True

            """Dessiner les boutons"""
            shadow_rect = buttons["classic"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.classic_mode else (160, 82, 45), shadow_rect, border_radius=10)

            pygame.draw.rect(screen_menu,(205, 200, 145), buttons["classic"],border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.classic_mode else (139, 69, 19), buttons["classic"],width=2,border_radius=10)
            text_classic = smallfont.render("Classique", True, (139, 69, 19))
            text_rect_classique = text_classic.get_rect(center=buttons["classic"].center)
            screen_menu.blit(text_classic, text_rect_classique)

            shadow_rect = buttons["tactic"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.tactic_mode else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["tactic"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.tactic_mode else (139, 69, 19), buttons["tactic"],width=2,border_radius=10)
            text_tactic = smallfont.render("Tactique", True, (139, 69, 19))
            text_rect_tactic = text_tactic.get_rect(center=buttons["tactic"].center)
            screen_menu.blit(text_tactic, text_rect_tactic)

            shadow_rect = buttons["expert"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.expert_mode else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["expert"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.expert_mode else (139, 69, 19), buttons["expert"],width=2,border_radius=10)
            text_expert = smallfont.render("Expert", True, (139, 69, 19))
            text_rect_expert = text_expert.get_rect(center=buttons["expert"].center)
            screen_menu.blit(text_expert, text_rect_expert)


            pygame.display.flip()