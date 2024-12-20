import sys

import pygame


class Joueur:
    """Représente un joueur avec un nom, une main et un score."""

    def __init__(self, id_, nom):
        self.id = id_
        self.nom = nom
        self.main = []
        self.score = 0
        self.borne_controlee = 0
        self.nbr_joker = 0
        self.nbr_carte_tactique = 0

    def jouer_carte(self, plateau, numero_borne, carte):
        """Méthode pour jouer une carte."""
        plateau.ajouter_carte(numero_borne, self.id, carte)
        self.main.remove(carte)

    def distribuer(self, pioche):
        """Méthode pour piocher une carte."""
        if pioche:
            self.main.append(pioche.popleft())  # Utilisation optimisée avec deque

    def piocher(self, pioche_clan, pioche_tactique, buttons):
        piocher = False
        while not piocher:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for pioche_key, pioche_rect in buttons.items():
                        if pioche_rect.collidepoint(event.pos):
                            if pioche_key == "pioche_clan":
                                # ajouter carte_clan dans la main
                                # retirer la carte du dessus de la pioche clan
                                piocher = True
                            elif pioche_key == "pioche_tactique":
                                #ajouter carte_tactique dans la main
                                #retirer la carte du dessus de la pioche tactique
                                piocher = True

