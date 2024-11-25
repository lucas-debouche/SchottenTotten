class Joueur:
    """Représente un joueur avec un nom, une main et un score."""

    def __init__(self, id, nom):
        self.id = id
        self.nom = nom
        self.main = []
        self.score = 0
        self.borne_controlee = 0

    def jouer_carte(self, plateau, numero_borne, carte):
        """Méthode pour jouer une carte."""
        plateau.ajouter_carte(numero_borne, self.id, carte)
        self.main.remove(carte)

    def piocher(self, pioche):
        """Méthode pour piocher une carte."""
        if pioche:
            self.main.append(pioche.popleft())  # Utilisation optimisée avec deque

    def revendiquer_borne(self, plateau, numero_borne):
        """Méthode pour revendiquer une borne."""
        if plateau.bornes[numero_borne].controle_par is None:
            plateau.bornes[numero_borne].controle_par = self
            self.borne_controlee += 1

    def __repr__(self):
        return f"{self.nom} (Score: {self.score}, Bornes contrôlées: {self.borne_controlee})"
