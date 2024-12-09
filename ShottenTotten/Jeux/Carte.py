import pygame
import os

# Configurations globales pour les cartes
Couleurs = {1: "blue", 2: "green", 3: "yellow", 4: "orange", 5: "red", 6: "purple"}
Capacites = {1: "Troupes d'élites", 2: "Modes de combat", 3: "Ruses"}
NomsCartesTactiques = {
    1: ["Joker", "Joker", "Espion", "Porte-Bouclier"],
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

    for i in range(len(main)) :
        x_carte = positions_cartes[i+1]
        y_joueur = positions_joueurs[joueur]
        carte = os.path.join(carte_clan_path, f"{main[i].couleur}-{main[i].force}.jpg")

        carte_button_img = pygame.image.load(carte)
        carte_button_img = pygame.transform.scale(carte_button_img,(largeur_carte, hauteur_carte))

        carte_button = pygame.Rect(x_carte, y_joueur, largeur_carte, hauteur_carte)
        fenetre.blit(carte_button_img, (carte_button.x, carte_button.y))

def est_suite(carte1, carte2, carte3):
    """Vérifie si trois cartes forment une suite de valeurs successives."""
    valeurs = sorted([carte1[1], carte2[1], carte3[1]])
    return valeurs[1] == valeurs[0] + 1 and valeurs[2] == valeurs[1] + 1

def est_suite_couleur(cartes):
    """Vérifie si trois cartes forment une suite de même couleur et de valeurs successives."""
    couleurs = {carte[0] for carte in cartes}
    return len(couleurs) == 1 and est_suite(*cartes)

def est_brelan(cartes):
    """Vérifie si trois cartes ont la même valeur."""
    valeurs = [carte[1] for carte in cartes]
    return len(set(valeurs)) == 1

def est_couleur(cartes):
    """Vérifie si trois cartes ont la même couleur."""
    couleurs = {carte[0] for carte in cartes}
    return len(couleurs) == 1

def est_somme(cartes):
    """Toute combinaison est valide comme somme."""
    return True,

def determiner_combinaison(cartes):
    """Détermine la meilleure combinaison parmi Suite couleur, Brelan, Couleur, Suite, et Somme."""
    if est_suite_couleur(cartes):
        return 0
    elif est_brelan(cartes):
        return 1
    elif est_couleur(cartes):
        return 2
    elif est_suite(*cartes):
        return 3
    else:
        return 4

