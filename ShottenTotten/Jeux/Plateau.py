class Plateau:
    """Représente le plateau de jeu avec ses bornes et sa défausse."""
    def __init__(self, nombre_bornes=9):
        # Chaque borne contient une liste pour les joueurs et une pour les cartes tactiques
        self.bornes = {i: [[], [], []] for i in range(1, nombre_bornes + 1)}
        self.defausse = []

    def revendiquer_borne(self, numero_borne):
        """Supprime une borne et retourne son contenu."""
        return self.bornes.pop(numero_borne, None)

    def ajouter_carte(self, numero_borne, joueur_index, carte):
        """Ajoute une carte à une borne pour un joueur."""
        if numero_borne in self.bornes:
            self.bornes[numero_borne][joueur_index].append(carte)

    def ajouter_defausse(self, carte):
        """Ajoute une carte à la défausse."""
        self.defausse.append(carte)
