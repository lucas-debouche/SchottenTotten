import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import generer_cartes
from ShottenTotten.Jeux.Joueur import Joueur
from ShottenTotten.Jeux.Plateau import displayPlateau, Plateau, melanger_pioche

plateau = Plateau()


def displayNom(plateau_, mode):
    """Fonction qui permet d'ajouter des noms de joueur"""
    nbr_joueur = plateau.nbr_joueurs
    pygame.display.set_caption("Schotten Totten : Nom")
    screen_nom = pygame.display.set_mode((1000, 400))

    # Création des boutons
    smallfont = pygame.font.SysFont('Forte', 35)
    textfont = pygame.font.SysFont('Congenial Black', 35)
    text_joueur1 = smallfont.render("Joueur 1 :", True, (139, 69, 19))
    text_joueur2 = smallfont.render("Joueur 2 : ", True, (139, 69, 19))
    buttons = {"jouer": pygame.Rect(750, 300, 200, 50)}

    # Initialisation de la zone de texte
    input_rect1 = pygame.Rect(400, 100, 300, 50)
    input_rect2 = pygame.Rect(400, 200, 300, 50)
    input_color_active = (255, 255, 255)  # Couleur de fond active
    input_color_inactive = (200, 200, 200)  # Couleur de fond inactif
    input_color1 = input_color_inactive
    input_color2 = input_color_inactive
    active1 = False  # Indique si la zone de texte est active
    active2 = False  # Indique si la zone de texte est active
    nom_joueur1 = ""  # Contient le texte saisi
    nom_joueur2 = ""  # Contient le texte saisi

    menu_running = True

    while menu_running:
        screen_nom.fill((205, 200, 145))  # Fond de la fenêtre
        screen_nom.blit(text_joueur1, (200, 100))
        if nbr_joueur == 2:
            screen_nom.blit(text_joueur2, (200, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                sys.exit()  # Arret du programme
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if input_rect1.collidepoint(event.pos):
                    active1 = True  # Activation de la zone de texte
                    input_color1 = input_color_active
                else:
                    active1 = False # Désactivation de la zone de texte
                    input_color1 = input_color_inactive

                if input_rect2.collidepoint(event.pos):
                    active1 = False
                    active2 = True  # Activation de la zone de texte
                    input_color2 = input_color_active
                else:
                    active2 = False
                    input_color2 = input_color_inactive

                if buttons["jouer"].collidepoint(event.pos):
                    # Lancer le plateau quand le bouton jouer est présser
                    displayPlateau(plateau)

            elif event.type == pygame.KEYDOWN and active1:
                if event.key == pygame.K_BACKSPACE:
                    nom_joueur1 = nom_joueur1[:-1]  # Supprimer le dernier caractère
                else:
                    nom_joueur1 += event.unicode  # Ajouter le caractère saisi
            elif event.type == pygame.KEYDOWN and active2:
                if event.key == pygame.K_BACKSPACE:
                    nom_joueur2 = nom_joueur2[:-1]  # Supprimer le dernier caractère
                else:
                    nom_joueur2 += event.unicode  # Ajouter le caractère saisi

        # Dessiner les boutons

        shadow_rect = buttons["jouer"].move(4, 4)  # Décalage pour l'ombre
        pygame.draw.rect(screen_nom, (160, 82, 45), shadow_rect, border_radius=10)

        pygame.draw.rect(screen_nom, (205, 200, 145), buttons["jouer"], border_radius=10)
        pygame.draw.rect(screen_nom, (139, 69, 19), buttons["jouer"], width=2, border_radius=10)
        text_jouer = smallfont.render("Jouer", True, (139, 69, 19))
        text_rect_jouer = text_jouer.get_rect(center=buttons["jouer"].center)
        screen_nom.blit(text_jouer, text_rect_jouer)

        # Dessiner la zone de texte
        pygame.draw.rect(screen_nom, input_color1, input_rect1, border_radius=10)
        pygame.draw.rect(screen_nom, (139, 69, 19), input_rect1, 2, border_radius=10)  # Bordure

        # Afficher le texte saisi
        text_surface = textfont.render(nom_joueur1, True, (0, 0, 0))
        screen_nom.blit(text_surface, (input_rect1.x + 10, input_rect1.y + 10))

        # Empêcher le texte de dépasser la largeur de la zone de texte
        input_rect1.w = max(300, text_surface.get_width() + 20)

        if nbr_joueur == 0:
            plateau.joueurs.append(Joueur(0, f"IA{1}"))
            plateau.joueurs.append(Joueur(1, f"IA{2}"))
            plateau.distribuer_cartes()
            displayPlateau(plateau_, mode)
        elif nbr_joueur == 1:
            nom_joueur2 = "IA"
        elif nbr_joueur == 2:
            # Dessiner la zone de texte
            pygame.draw.rect(screen_nom, input_color2, input_rect2, border_radius=10)
            pygame.draw.rect(screen_nom, (139, 69, 19), input_rect2, 2, border_radius=10)  # Bordure

            # Afficher le texte saisi
            text_surface = textfont.render(nom_joueur2, True, (0, 0, 0))
            screen_nom.blit(text_surface, (input_rect2.x + 10, input_rect2.y + 10))

            # Empêcher le texte de dépasser la largeur de la zone de texte
            input_rect2.w = max(300, text_surface.get_width() + 20)

        if nom_joueur1 != "" and nom_joueur2 != "":
            plateau.joueurs.append(Joueur(0, nom_joueur1))
            plateau.joueurs.append(Joueur(1, nom_joueur2))
            plateau.distribuer_cartes()
            displayPlateau(plateau_, mode)

        pygame.display.flip()


class Menu :

    def __init__(self):
        self.mode = False
        self.nbr_manche = None

    def initialiser_cartes(self):
        """Initialise les cartes de clans et tactiques, puis mélange la pioche."""
        cartes_clans, cartes_tactiques = generer_cartes()
        if self.mode == "classic":
            cartes_tactiques = []
        plateau.pioche = melanger_pioche(cartes_clans, cartes_tactiques)

    def displayAcceuil(self):
        """Fonction qui affiche l'acceuil de bienvenue"""
        pygame.init()

        pygame.display.set_caption("Schotten Totten")
        screen_acceuil = pygame.display.set_mode((600,750))

        current_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        background_path = os.path.join(base_dir, "Ressources", "Acceuil.png")
        background = pygame.image.load(background_path)

        #Création des boutons
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
                        #Lancer le menu quand le bouton jouer est présser
                        self.displayMenu()

            #Dessiner les boutons
            pygame.draw.rect(screen_acceuil, (205, 200, 145), buttons["Jouer"])
            text_jouer = smallfont.render("Jouer", True, (255, 45, 0))
            screen_acceuil.blit(text_jouer, (buttons["Jouer"].x + 20, buttons["Jouer"].y + 5))

            pygame.display.flip()

    def displayMenu(self):
        """Fonction qui affiche le menu et permet de récuperer les infos pour initialiser la partie souhaité"""
        os.environ['SDL_VIDEO_CENTERED'] = '1' #Centrer la fenetre sur l'ecran

        #Initialisation de de la fenetre
        window_height = 750
        window_width = 1280

        pygame.display.set_caption("Schotten Totten : Menu")
        screen_menu = pygame.display.set_mode((window_width, window_height))

        current_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        background_path = os.path.join(base_dir, "Ressources", "Menu.png")
        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (window_width, window_height))

        #Création des boutons
        smallfont = pygame.font.SysFont('Forte', 35)
        button_height = 50
        button_width = 200

        buttons = {"classic": pygame.Rect(200, 150, button_width, button_height),
                   "tactic": pygame.Rect(500, 150, button_width, button_height),
                   "expert": pygame.Rect(800, 150, button_width, button_height),
                   "jvsj": pygame.Rect(200, 350, button_width, button_height),
                   "jvsia":  pygame.Rect(500, 350, button_width, button_height),
                   "iavsia": pygame.Rect(800, 350, button_width, button_height),
                   "manche1": pygame.Rect(200, 550, button_width, button_height),
                   "manche3": pygame.Rect(500, 550, button_width, button_height),
                   "manche5": pygame.Rect(800, 550, button_width, button_height),
                   "jouer": pygame.Rect(1050, 650, button_width, button_height),
               }

        title_font = pygame.font.SysFont('Forte', 75)
        text_mode = title_font.render("Mode", True, (255, 255, 255))
        text_joueurs = title_font.render("Joueurs", True, (255, 255, 255))
        text_manches = title_font.render("Manches", True, (255, 255, 255))

        menu_running = True

        while menu_running:
            screen_menu.blit(background, (0, 0))

            # Afficher les textes "Mode, Joueurs, Manches"
            screen_menu.blit(text_mode, (500, 50))
            screen_menu.blit(text_joueurs, (475, 250))
            screen_menu.blit(text_manches, (450, 450))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    pygame.quit()
                    sys.exit() #Arret du programme
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons["classic"].collidepoint(event.pos):
                        #Activer le mode classique et désactiver les autres
                        self.mode = "classic"
                        plateau.nbr_cartes = 6
                    elif buttons["tactic"].collidepoint(event.pos):
                        #Activer le mode tactique et désactiver les autres
                        self.mode = "tactic"
                        plateau.nbr_cartes = 7
                    elif buttons["expert"].collidepoint(event.pos):
                        #Activer le mode expert et désactiver les autres
                        self.mode = "expert"
                        plateau.nbr_cartes = 7
                    if buttons["jvsj"].collidepoint(event.pos):
                        #Selction joueur contre joueur
                        plateau.nbr_joueurs = 2
                    elif buttons["jvsia"].collidepoint(event.pos):
                        #Selction joueur contre ia
                        plateau.nbr_joueurs = 1
                    elif buttons["iavsia"].collidepoint(event.pos):
                        #Selction joueur contre ia
                        plateau.nbr_joueurs = 0
                    if buttons["manche1"].collidepoint(event.pos):
                        #Selction 1 manche
                        self.nbr_manche = 1
                    elif buttons["manche3"].collidepoint(event.pos):
                        # Selction 3 manches
                        self.nbr_manche = 3
                    elif buttons["manche5"].collidepoint(event.pos):
                        #Selction 5 manches
                        self.nbr_manche = 5
                    if buttons["jouer"].collidepoint(event.pos) and self.mode != False and plateau.nbr_joueurs is not None and self.nbr_manche:
                        #retourne les valeurs Mode, Joueurs, Manches pour initialiser le jeu
                        self.initialiser_cartes()
                        displayNom(plateau, self.mode)



            #Dessiner les boutons
            shadow_rect = buttons["classic"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "classic" else (160, 82, 45), shadow_rect, border_radius=10)

            pygame.draw.rect(screen_menu,(205, 200, 145), buttons["classic"],border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "classic" else (139, 69, 19), buttons["classic"],width=2,border_radius=10)
            text_classic = smallfont.render("Classique", True, (139, 69, 19))
            text_rect_classique = text_classic.get_rect(center=buttons["classic"].center)
            screen_menu.blit(text_classic, text_rect_classique)

            shadow_rect = buttons["tactic"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "tactic" else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["tactic"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "tactic" else (139, 69, 19), buttons["tactic"],width=2,border_radius=10)
            text_tactic = smallfont.render("Tactique", True, (139, 69, 19))
            text_rect_tactic = text_tactic.get_rect(center=buttons["tactic"].center)
            screen_menu.blit(text_tactic, text_rect_tactic)

            shadow_rect = buttons["expert"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "expert" else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["expert"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.mode == "expert" else (139, 69, 19), buttons["expert"],width=2,border_radius=10)
            text_expert = smallfont.render("Expert", True, (139, 69, 19))
            text_rect_expert = text_expert.get_rect(center=buttons["expert"].center)
            screen_menu.blit(text_expert, text_rect_expert)

            shadow_rect = buttons["jvsj"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 2 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["jvsj"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 2 else (139, 69, 19), buttons["jvsj"],width=2, border_radius=10)
            text_jvsj = smallfont.render("J vs J", True, (139, 69, 19))
            text_rect_jvsj = text_jvsj.get_rect(center=buttons["jvsj"].center)
            screen_menu.blit(text_jvsj, text_rect_jvsj)

            shadow_rect = buttons["jvsia"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 1 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["jvsia"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 1 else (139, 69, 19), buttons["jvsia"],width=2, border_radius=10)
            text_jvsia = smallfont.render("J vs ia", True, (139, 69, 19))
            text_rect_jvsia = text_jvsia.get_rect(center=buttons["jvsia"].center)
            screen_menu.blit(text_jvsia, text_rect_jvsia)

            shadow_rect = buttons["iavsia"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 0 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["iavsia"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if plateau.nbr_joueurs == 0 else (139, 69, 19), buttons["iavsia"],width=2, border_radius=10)
            text_iavsia = smallfont.render("ia vs ia", True, (139, 69, 19))
            text_rect_iavsia = text_iavsia.get_rect(center=buttons["iavsia"].center)
            screen_menu.blit(text_iavsia, text_rect_iavsia)

            shadow_rect = buttons["manche1"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 1 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["manche1"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 1 else (139, 69, 19), buttons["manche1"],width=2, border_radius=10)
            text_manche1 = smallfont.render("1 Manche", True, (139, 69, 19))
            text_rect_manche1 = text_manche1.get_rect(center=buttons["manche1"].center)
            screen_menu.blit(text_manche1, text_rect_manche1)

            shadow_rect = buttons["manche3"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 3 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["manche3"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 3 else (139, 69, 19), buttons["manche3"],width=2, border_radius=10)
            text_manche3 = smallfont.render("3 Manches", True, (139, 69, 19))
            text_rect_manche3 = text_manche3.get_rect(center=buttons["manche3"].center)
            screen_menu.blit(text_manche3, text_rect_manche3)

            shadow_rect = buttons["manche5"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 5 else (160, 82, 45), shadow_rect,border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["manche5"], border_radius=10)
            pygame.draw.rect(screen_menu, (255, 0, 0) if self.nbr_manche == 5 else (139, 69, 19), buttons["manche5"],width=2, border_radius=10)
            text_manche5 = smallfont.render("5 Manches", True, (139, 69, 19))
            text_rect_manche5 = text_manche5.get_rect(center=buttons["manche5"].center)
            screen_menu.blit(text_manche5, text_rect_manche5)

            shadow_rect = buttons["jouer"].move(4, 4)  # Décalage pour l'ombre
            pygame.draw.rect(screen_menu, (160, 82, 45), shadow_rect, border_radius=10)

            pygame.draw.rect(screen_menu, (205, 200, 145), buttons["jouer"], border_radius=10)
            pygame.draw.rect(screen_menu, (139, 69, 19), buttons["jouer"], width=2, border_radius=10)
            text_jouer = smallfont.render("Jouer", True, (139, 69, 19))
            text_rect_jouer = text_jouer.get_rect(center=buttons["jouer"].center)
            screen_menu.blit(text_jouer, text_rect_jouer)

            pygame.display.flip()
