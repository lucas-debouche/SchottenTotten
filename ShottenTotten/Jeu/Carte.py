Couleurs = {1 : "bleu", 2 : "vert", 3 : "jaune", 4 : "marron", 5 : "rouge", 6 : "violet"}
Capacites = {1 : "Troupes d'élites", 2 : "Modes de combat", 3 : "Ruses"}
NomsCartesTactiques = {1 : "Joker", 2 : "Espion", 3 : "Porte-Bouclier",
                       4 : "Colin-Maillard", 5 : " Combat de Boue", 6 : "Chasseur de Tête",
                       7 : "Stratège", 8 : "Banshee", 9 : "Traître"}

class CarteClan:
    def __init__(self, force, couleur):
        self.force = force
        self.couleur = couleur

class CarteTactique:
    def __init__(self, capacite, nom):
        self.capacite = capacite
        self.nom = nom

