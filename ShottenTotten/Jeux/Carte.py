from collections import deque

import pygame
import os

from ShottenTotten.Jeux.Popup import Popup

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
    if joueur == 2:
        x_conteneur = 100
    else:
        x_conteneur = 450
    y1_conteneur = 0
    y2_conteneur = 600

    current_dir, base_dir, carte_clan_path, carte_tactique_path, back_card_path = chemin()

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
        8: x_conteneur + 680,
        9: x_conteneur + 775,
        10: x_conteneur + 870,
    }

    positions_joueurs = {
        1: y1_conteneur + 10,
        0: y2_conteneur + 10,
        2: y2_conteneur,
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
    nb_carte_borne = 0
    for bornes in borne:
        if carte != bornes:
            nb_carte_borne += 1

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

def capacite_elite(screen, screen_width, screen_height, troupe):
    popup = Popup(screen, screen_width, screen_height, troupe)
    choix_couleur, choix_force = popup.show("Troupes d'élites")
    return choix_couleur, choix_force

def jouer_carte_troupes_elites(carte, screen, screen_width, screen_height):
    if carte.nom == "Joker1" or carte.nom == "Joker2" :
        choix_couleur, choix_force = capacite_elite(screen, screen_width, screen_height, "joker")
        choix_couleur = trad_couleur(choix_couleur)
        return CarteClan(choix_couleur, choix_force)
    elif carte.nom == "Espion":
        choix_couleur, choix_force = capacite_elite(screen, screen_width, screen_height, "espion")
        choix_couleur = trad_couleur(choix_couleur)
        return CarteClan(choix_couleur, choix_force)
    elif carte.nom == "Porte-Bouclier":
        choix_couleur, choix_force = capacite_elite(screen, screen_width, screen_height, "porte-bouclier")
        choix_couleur = trad_couleur(choix_couleur)
        return CarteClan(choix_couleur, choix_force)

def config_button(screen_plateau, button_color, button, text):
    smallfont = pygame.font.SysFont('Forte', 35)
    pygame.draw.rect(screen_plateau, button_color, button, border_radius=10)
    pygame.draw.rect(screen_plateau, (139, 69, 19), button, width=2, border_radius=10)
    text_jouer = smallfont.render(text, True, (139, 69, 19))
    text_rect_jouer = text_jouer.get_rect(center=button.center)
    screen_plateau.blit(text_jouer, text_rect_jouer)
    pygame.display.update(button)

def trad_couleur(couleur):
    if couleur == "Rouge":
        return "red"
    elif couleur == "Bleu":
        return "blue"
    elif couleur == "Violet":
        return "purple"
    elif couleur == "Jaune":
        return "yellow"
    elif couleur == "Vert":
        return "green"
    elif couleur == "Orange":
        return "orange"

def chemin():
    # Récupération chemin images cartes
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    carte_clan_path = os.path.join(base_dir, "Ressources", "Cartes_Clan")
    carte_tactique_path = os.path.join(base_dir, "Ressources", "Cartes_Tactiques")
    back_card_path = os.path.join(base_dir, "Ressources", "Back_Card.jpg")
    return current_dir, base_dir, carte_clan_path, carte_tactique_path, back_card_path