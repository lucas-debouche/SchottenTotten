import os
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
        return carte

    def distribuer(self, pioche):
        """Méthode pour piocher une carte."""
        if pioche:
            self.main.append(pioche.popleft())  # Utilisation optimisée avec deque

    def piocher(self, pioche_clan, pioche_tactique, buttons, screen):
        piocher = False

        while not piocher:
            # Afficher la flèche uniquement si l'indicateur est True
            afficher_indication_pioche(screen)

            # Rafraîchir l'écran après chaque mise à jour
            pygame.display.update()

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for pioche_key, pioche_rect in buttons.items():
                        if pioche_rect.collidepoint(event.pos):
                            if pioche_key == "pioche_clan" and len(pioche_clan) > 0:
                                self.main.append(pioche_clan.popleft())
                                piocher = True
                            elif pioche_key == "pioche_tactique" and len(pioche_tactique) > 0:
                                self.main.append(pioche_tactique.popleft())
                                piocher = True

        desactiver_indication_fleche(screen)
        pygame.display.update()


def afficher_indication_pioche(screen):
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    image_path = os.path.join(os.path.join(base_dir, "Ressources"), "fleche.png")
    fleche_rect = pygame.Rect(100, 530, 120, 120)  # Rectangle pour position et dimensions.

    # Charger et redimensionner l'image
    image_fleche = load_and_scale_image(image_path, fleche_rect.width, fleche_rect.height)

    # Afficher l'image à l'écran
    screen.blit(image_fleche, (fleche_rect.x, fleche_rect.y))

def load_and_scale_image(path, width, height):
    """Charge et redimensionne une image."""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image: {path}")
        raise e

def desactiver_indication_fleche(screen):
    fleche_rect = pygame.Rect(100, 530, 120, 120)  # Rectangle pour position et dimensions.

    # Remplir la zone avec la couleur de fond (205, 200, 145)
    pygame.draw.rect(screen, (205, 200, 145), fleche_rect)

    # Mettre à jour l'affichage pour appliquer les changements
    pygame.display.update()

