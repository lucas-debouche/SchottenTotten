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
        for capacite in Capacites
        for i, nom in NomsCartesTactiques.items()
        if i in Capacites and Capacites[i] == Capacites[capacite]
    ]
    return cartes_clans, cartes_tactiques

