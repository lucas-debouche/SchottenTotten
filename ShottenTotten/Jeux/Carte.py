import sys
from collections import deque

import pygame
import os

# Configurations globales pour les cartes
Couleurs = {1: "blue", 2: "green", 3: "yellow", 4: "orange", 5: "red", 6: "purple"}
Capacites = {1: "Troupes d'élites", 2: "Modes de combat", 3: "Ruses"}
NomsCartesTactiques = {
    1: ["Joker1", "Joker2", "Espion", "Porte-Bouclier"],
    2: ["Colin-Maillard", "Combat de Boue"],
    3: ["Chasseur de Tête", "Stratège", "Banshee", "Traître"]
}

class CarteClan:
    """Représente une carte de clan avec une couleur et une force."""

    def __init__(self, couleur, force):
        self.couleur = couleur
        self.force = force

class CarteTactique:
    """Représente une carte tactique avec une capacité et un nom."""

    def __init__(self, capacite, nom):
        self.capacite = capacite
        self.nom = nom


def generer_cartes():
    """Génère toutes les cartes de clans et tactiques."""
    cartes_clans = deque([
        CarteClan(couleur, force)
        for couleur in Couleurs.values()
        for force in range(1, 10)
    ])

    cartes_tactiques = deque([
        CarteTactique(Capacites[capacite], nom)
        for capacite, list_nom in NomsCartesTactiques.items()
        if capacite in Capacites
        for nom in list_nom
    ])
    return cartes_clans, cartes_tactiques


def displayCarte(fenetre, joueur, main):
    # Création rectangle affichage carte joueur 1 et joueur 2
    x_conteneur = 450
    y1_conteneur = 0
    y2_conteneur = 600

    # Récupération chemin images cartes
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    carte_clan_path = os.path.join(base_dir, "Ressources", "Cartes_Clan")
    carte_tactique_path = os.path.join(base_dir, "Ressources", "Cartes_Tactiques")
    back_card_path = os.path.join(base_dir, "Ressources", "Back_Card.jpg")

    # Création cartes
    largeur_carte = 85
    hauteur_carte = 130

    positions_cartes = {
        1: x_conteneur + 25,
        2: x_conteneur + 120,
        3: x_conteneur + 215,
        4: x_conteneur + 310,
        5: x_conteneur + 405,
        6: x_conteneur + 500,
        7: x_conteneur + 595,
    }

    positions_joueurs = {
        1: y1_conteneur + 10,
        0: y2_conteneur + 10,
    }

    buttons = {}
    for i in range(len(main)):
        x_carte = positions_cartes[i + 1]
        y_joueur = positions_joueurs[joueur]

        adversaire = 1 if joueur == 0 else 0
        y_adversaire = positions_joueurs[adversaire]

        if isinstance(main[i], CarteClan):
            carte = os.path.join(carte_clan_path, f"{main[i].couleur}-{main[i].force}.jpg")
        else:
            carte = os.path.join(carte_tactique_path, f"{main[i].nom}.jpg")

        # Vérification et chargement des images
        if not os.path.exists(carte):
            print(f"Image introuvable : {carte}")
            continue

        try:
            carte_button_img = pygame.image.load(carte)
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image : {carte}\n{e}")
            continue

        back_card_img = pygame.image.load(back_card_path)
        back_card_img = pygame.transform.scale(back_card_img, (largeur_carte, hauteur_carte))
        back_card = pygame.Rect(x_carte, y_adversaire, largeur_carte, hauteur_carte)
        carte_button_img = pygame.transform.scale(carte_button_img, (largeur_carte, hauteur_carte))
        carte_button = pygame.Rect(x_carte, y_joueur, largeur_carte, hauteur_carte)
        fenetre.blit(carte_button_img, (carte_button.x, carte_button.y))
        fenetre.blit(back_card_img, (back_card.x, back_card.y))

        buttons[i] = carte_button
    return buttons

def deplacer_carte(fenetre, joueur, carte, borne_index, borne):
    """Déplace une carte à une position donnée."""
    positions_cartes = {
        1: 417.5,
        2: 527.5,
        3: 637.5,
        4: 747.5,
        5: 857.5,
        6: 967.5,
        7: 1077.5,
        8: 1187.5,
        9: 1297.5,
    }

    nb_carte_borne = len(borne)

    positions_joueurs = {
        1: 210 - (nb_carte_borne * 30),
        0: 410 + (nb_carte_borne * 30)
    }

    x = positions_cartes[borne_index]
    y = positions_joueurs[joueur]

    largeur_carte = 85
    hauteur_carte = 130

    # Récupération du chemin de l'image de la carte
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    carte_clan_path = os.path.join(base_dir, "Ressources", "Cartes_Clan")
    carte_tactique_path = os.path.join(base_dir, "Ressources", "Cartes_Tactiques")

    if isinstance(carte, CarteClan):
        carte_image_path = os.path.join(carte_clan_path, f"{carte.couleur}-{carte.force}.jpg")
    else:
        carte_image_path = os.path.join(carte_tactique_path, f"{carte.nom}.jpg")

    # Vérification et chargement de l'image
    if not os.path.exists(carte_image_path):
        print(f"Image introuvable : {carte_image_path}")
        return

    try:
        carte_img = pygame.image.load(carte_image_path)
        carte_img = pygame.transform.scale(carte_img, (largeur_carte, hauteur_carte))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image : {carte_image_path}\n{e}")
        return

    # Dessiner la carte à la nouvelle position
    fenetre.blit(carte_img, (x,y))


def displayChoixValeurs(screen, screen_width, screen_height):


    couleurs = ["Rouge", "Vert", "Jaune", "Violet", "Bleu", "Marron"]
    force = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    menu1_open = False
    menu2_open = False

    # Centre la popup
    popup_x = screen_width // 2
    popup_y = screen_height // 2

    # Boutons et menus relatifs à la popup
    menu1_rect = {"couleur": pygame.Rect(popup_x - 175, popup_y - 200, 150, 50)}
    menu2_rect = {"force": pygame.Rect(popup_x + 125, popup_y - 200, 150, 50)}

    options1_rects = {i : pygame.Rect(menu1_rect["couleur"].x, menu1_rect["couleur"].y + (i + 1) * menu1_rect["couleur"].height, menu1_rect["couleur"].width, menu1_rect["couleur"].height) for i in range(len(couleurs))}
    options2_rects = {i : pygame.Rect(menu2_rect["force"].x, menu2_rect["force"].y + (i + 1) * menu2_rect["force"].height, menu2_rect["force"].width, menu2_rect["force"].height) for i in range(len(force))}

    choix_couleur = None
    choix_force = None
    button_valider = {"valider": pygame.Rect(popup_x, popup_y + 240, 150, 50)}

    # Boucle principale
    valider = False
    while not valider:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Vérifie si le bouton "Valider" est cliqué
                if button_valider["valider"].collidepoint(event.pos) and choix_couleur and choix_force:
                    valider = True
                # Gestion des menus déroulants
                elif menu1_rect["couleur"].collidepoint(event.pos):
                    menu1_open = not menu1_open
                elif menu1_open:
                    for i, rect in options1_rects.items():
                        if rect.collidepoint(event.pos):
                            choix_couleur = couleurs[i]
                            menu1_open = False
                elif menu2_rect["force"].collidepoint(event.pos):
                    menu2_open = not menu2_open
                elif menu2_open:
                    for i, rect in options2_rects.items():
                        if rect.collidepoint(event.pos):
                            choix_force = force[i]
                            menu2_open = False

        # Affichage
        screen.fill((165, 140, 100))  # Efface l'écran principal

        # Affiche les menus
        pygame.draw.rect(screen, (205, 200, 145), menu1_rect["couleur"])  # Fond clair
        pygame.draw.rect(screen, (0, 0, 0), menu1_rect["couleur"], width=2)  # Bordure noire
        if not choix_couleur:
            menu1_text = pygame.font.Font(None, 36).render("Couleur", True, (0, 0, 0))
        else:
            menu1_text = pygame.font.Font(None, 36).render(str(choix_couleur), True, (0, 0, 0))
        screen.blit(menu1_text, menu1_text.get_rect(center=menu1_rect["couleur"].center))

        pygame.draw.rect(screen, (205, 200, 145), menu2_rect["force"])  # Fond clair
        pygame.draw.rect(screen, (0, 0, 0), menu2_rect["force"], width=2)  # Bordure noire
        if not choix_force:
            menu2_text = pygame.font.Font(None, 36).render("Force", True, (0, 0, 0))
        else:
            menu2_text = pygame.font.Font(None, 36).render(str(choix_force), True, (0, 0, 0))
        screen.blit(menu2_text, menu2_text.get_rect(center=menu2_rect["force"].center))


        # Bouton Valider
        pygame.draw.rect(screen, (205, 200, 145), button_valider["valider"])  # Fond clair
        pygame.draw.rect(screen, (0, 0, 0), button_valider["valider"], width=2)  # Bordure noire
        text_surface = pygame.font.Font(None, 36).render("Valider", True, (0, 0, 0))
        screen.blit(text_surface, text_surface.get_rect(center = button_valider["valider"].center))

        if menu1_open:
            menuX_open(options1_rects, screen, couleurs, None)
        if menu2_open:
            menuX_open(options2_rects, screen, force, None)

        pygame.display.flip()

    return choix_couleur, choix_force


def menuX_open(optionsx_rects, screen, liste, nom):
    for i, rect in optionsx_rects.items():
        pygame.draw.rect(screen, (205, 200, 145), rect)  # Fond clair
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2)  # Bordure noire
        if liste :
            option_surface = pygame.font.Font(None, 36).render(liste[i], True, (0, 0, 0))
        else:
            option_surface = pygame.font.Font(None, 36).render(nom, True, (0, 0, 0))
        option_rect = option_surface.get_rect(center=rect.center)
        screen.blit(option_surface, option_rect)


def capacite_joker(joueur, screen, screen_width, screen_height):
    joueur.nbr_carte_tactique += 1
    joueur.nbr_joker += 1
    choix_couleur, choix_force = displayChoixValeurs(screen, screen_width, screen_height)
    return choix_couleur, choix_force


def capacite_espion(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_porte_bouclier(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_colin_maillard(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_combat_de_boue(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_chasseur_de_tete(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_stratege(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_banshee(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_traitre(joueur):
    joueur.nbr_carte_tactique += 1


def capacite_cartes_tactique(nom_carte, joueur, screen, screen_width, screen_height):
    if nom_carte == "Joker1" or nom_carte == "Joker2" :
        choix_couleur, choix_force = capacite_joker(joueur, screen, screen_width, screen_height)
        return choix_couleur, choix_force
    elif nom_carte == "Espion":
        capacite_espion(joueur)
    elif nom_carte == "Porte-Bouclier":
        capacite_porte_bouclier(joueur)
    elif nom_carte == "Colin-Maillard":
        capacite_colin_maillard(joueur)
    elif nom_carte == "Combat de Boue":
        capacite_combat_de_boue(joueur)
    elif nom_carte == "Chasseur de Tête":
        capacite_chasseur_de_tete(joueur)
    elif nom_carte == "Stratège":
        capacite_stratege(joueur)
    elif nom_carte == "Banshee":
        capacite_banshee(joueur)
    elif nom_carte == "Traître":
        capacite_traitre(joueur)


def config_button(screen_plateau, button_color, button, text):
    smallfont = pygame.font.SysFont('Forte', 35)
    pygame.draw.rect(screen_plateau, button_color, button, border_radius=10)
    pygame.draw.rect(screen_plateau, (139, 69, 19), button, width=2, border_radius=10)
    text_jouer = smallfont.render(text, True, (139, 69, 19))
    text_rect_jouer = text_jouer.get_rect(center=button.center)
    screen_plateau.blit(text_jouer, text_rect_jouer)
    pygame.display.update(button)