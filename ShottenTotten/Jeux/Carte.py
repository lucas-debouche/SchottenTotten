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

# Exemple d'utilisation
cartes = [("Bleu", 3), ("Bleu", 4), ("Bleu", 5)]  # Suite couleur
combinaison = determiner_combinaison(cartes)


