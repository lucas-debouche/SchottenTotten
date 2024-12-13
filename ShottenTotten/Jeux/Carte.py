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

    def __repr__(self):
        return f"{self.couleur} (Force: {self.force})"


class CarteTactique:
    """Représente une carte tactique avec une capacité et un nom."""

    def __init__(self, capacite, nom):
        self.capacite = capacite
        self.nom = nom


def generer_cartes():
    """Génère toutes les cartes de clans et tactiques."""
    cartes_clans = [
        CarteClan(couleur, force)
        for couleur in Couleurs.values()
        for force in range(1, 10)
    ]

    cartes_tactiques = [
        CarteTactique(Capacites[capacite], nom)
        for capacite, list_nom in NomsCartesTactiques.items()
        if capacite in Capacites
        for nom in list_nom
    ]
    return cartes_clans, cartes_tactiques


def displayCarte(fenetre, joueur, main):
    # Création rectangle affichage carte joueur 1 et joueur 2
    x_conteneur = 350
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
    """
    Déplace une carte à une position donnée.

    :param fenetre: Surface pygame sur laquelle dessiner la carte.
    :param carte: Instance de Carte contenant les informations de la carte.
    :param position: Tuple contenant les coordonnées (x, y) de la nouvelle position.
    """
    positions_cartes = {
        1: 215,
        2: 325,
        3: 435,
        4: 545,
        5: 655,
        6: 765,
        7: 875,
        8: 985,
        9: 1095,
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
