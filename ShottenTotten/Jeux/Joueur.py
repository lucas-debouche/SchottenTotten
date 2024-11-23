class Joueur:
    """Représente un joueur avec un nom, une main et un score."""
    def __init__(self, nom):
        self.nom = nom
        self.main = []
        self.score = 0
        self.borne_controlee = 0

    def jouer_carte(self, plateau, numero_borne, carte):
        """Permet au joueur de jouer une carte."""
        plateau.ajouter_carte(numero_borne, 0, carte)  # Exemple avec joueur_index 0
        self.main.remove(carte)

    def piocher(self, pioche):
        """Permet au joueur de piocher une carte."""
        if pioche:
            carte = pioche.pop(0)
            self.main.append(carte)

    def __repr__(self):
        return f"{self.nom} (Score: {self.score}, Main: {self.main})"
