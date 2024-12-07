import pygame
import os

# Configurations globales pour les cartes
Couleurs = {1: "Bleu", 2: "Vert", 3: "Jaune", 4: "Marron", 5: "Rouge", 6: "Violet"}
Capacites = {1: "Troupes d'élites", 2: "Modes de combat", 3: "Ruses"}
NomsCartesTactiques = {
    1: "Joker", 2: "Espion", 3: "Porte-Bouclier",
    4: "Colin-Maillard", 5: "Combat de Boue", 6: "Chasseur de Tête",
    7: "Stratège", 8: "Banshee", 9: "Traître"
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

    def __repr__(self):
        return f"{self.nom} (Capacité: {self.capacite})"




def generer_cartes():
    """Génère toutes les cartes de clans et tactiques."""
    cartes_clans = [
        CarteClan(couleur, force)
        for couleur in Couleurs.values()
        for force in range(1, 10)
    ]

    cartes_tactiques = [
        CarteTactique(Capacites[capacite], nom)
        for capacite, nom in NomsCartesTactiques.items()
        if capacite in Capacites
    ]
    return cartes_clans, cartes_tactiques

def displayCarte(fenetre, joueur, couleur, force):

    #Création rectangle affichage carte joueur 1 et joueur 2
    largeur_conteneur = 625
    hauteur_conteneur = 150
    x_conteneur = 350
    y1_conteneur = 25
    y2_conteneur = 575

    joueur1 = pygame.Rect(x_conteneur, y1_conteneur, largeur_conteneur, hauteur_conteneur)
    joueur2 = pygame.Rect(x_conteneur, y2_conteneur, largeur_conteneur, hauteur_conteneur)

    pygame.draw.rect(fenetre, (255, 0, 0), joueur1)
    pygame.draw.rect(fenetre, (0, 255, 0), joueur2)

    #Recuperation chemin images cartes
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    carte_clan_path = os.path.join(base_dir, "Ressources", "Cartes_Clan")

    #Création cartes
    largeur_carte = 85
    hauteur_carte = 130

    positions_cartes = {
        1: x_conteneur + 25,
        2: x_conteneur + 120,
        3: x_conteneur + 215,
        4: x_conteneur + 310,
        5: x_conteneur + 405,
        6: x_conteneur + 500,
    }

    positions_joueurs = {
        1: y1_conteneur + 10,
        2: y2_conteneur + 10,
    }

    for i in range(len(couleur)) :
        x_carte = positions_cartes[i+1]
        y_joueur = positions_joueurs[joueur]
        carte = os.path.join(carte_clan_path, f"{couleur[i]}-{force[i]}.jpg")

        carte_button_img = pygame.image.load(carte)
        carte_button_img = pygame.transform.scale(carte_button_img,(largeur_carte, hauteur_carte))

        carte_button = pygame.Rect(x_carte, y_joueur, largeur_carte, hauteur_carte)
        fenetre.blit(carte_button_img, (carte_button.x, carte_button.y))

