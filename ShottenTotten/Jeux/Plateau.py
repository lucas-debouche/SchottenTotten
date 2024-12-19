import random
from collections import deque

import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import displayCarte, deplacer_carte, generer_cartes


class Borne:
    """Représente une borne sur le plateau avec des cartes et un contrôle."""

    def __init__(self):
        self.joueur1_cartes = []
        self.joueur2_cartes = []
        self.controle_par = None  # Joueur qui contrôle cette borne

class Plateau:
    """Représente le plateau de jeu avec ses bornes et sa défausse."""

    def __init__(self, nombre_bornes=9):
        self.bornes = {i: Borne() for i in range(1, nombre_bornes + 1)}
        self.defausse = []
        self.pioche = deque()
        self.nbr_cartes = None
        self.joueurs = []
        self.nbr_joueurs = None

    def ajouter_carte(self, numero_borne, joueur_index, carte):
        """Ajoute une carte à une borne pour un joueur."""
        if numero_borne not in self.bornes:
            raise ValueError(f"Borne {numero_borne} n'existe pas.")
        borne = self.bornes[numero_borne]
        if joueur_index == 0:
            borne.joueur1_cartes.append(carte)
        elif joueur_index == 1:
            borne.joueur2_cartes.append(carte)
        else:
            raise ValueError("Index du joueur invalide.")

    def initialiser_cartes(self, mode):
        """Initialise les cartes de clans et tactiques, puis mélange la pioche."""
        cartes_clans, cartes_tactiques = generer_cartes()
        if mode == "classic":
            cartes_tactiques = []
        self.pioche = melanger_pioche(cartes_clans, cartes_tactiques)

    def commencer_nouvelle_manche(self, mode, nbr_manche):
        for joueur in self.joueurs:
            joueur.main = []
            joueur.borne_controlee = 0
        self.pioche.clear()


        self.initialiser_cartes(mode)
        self.distribuer_cartes()
        displayPlateau(self, mode, nbr_manche)

    def distribuer_cartes(self):
        """Distribue les cartes aux joueurs au début de la partie."""
        for joueur in self.joueurs:
            for i in range(self.nbr_cartes):
                joueur.piocher(self.pioche)

    def verifier_fin_manche(self):
        """Vérifie les conditions de fin de manche."""
        for joueur in self.joueurs:
            # Vérifier si un joueur contrôle 5 bornes
            if joueur.borne_controlee == 5:
                print(f"{joueur.nom} remporte la manche (5 bornes contrôlées).")
                return False

            # Vérifier si un joueur contrôle 3 bornes consécutives
            consecutives = 0
            for numero_borne, borne in self.bornes.items():
                if borne.controle_par == joueur:
                    consecutives += 1
                    if consecutives == 3:
                        print(f"{joueur.nom} remporte la manche (3 bornes consécutives).")
                        return False
                else:
                    consecutives = 0

        if len(self.pioche) == 0:
            if self.joueurs[0].borne_controlee < self.joueurs[1].borne_controlee:
                print(f"{self.joueurs[0].nom} remporte la manche (plus de bornes contrôlées que {self.joueurs[1].nom}).")
                return False
            elif self.joueurs[0].borne_controlee > self.joueurs[1].borne_controlee:
                print(f"{self.joueurs[1].nom} remporte la manche (plus de bornes contrôlées que {self.joueurs[0].nom}).")
                return False
            else:
                print(f"{self.joueurs[0]} et {self.joueurs[1]} ne marque pas de point (même nombre de bornes contrôlées).")
                return False
        return True

    def fin_jeu(self):
        """Définit la fin du jeu."""
        if self.joueurs[0].score != self.joueurs[1].score:
            gagnant = max(self.joueurs, key=lambda j: j.score)
            print(f"{gagnant.nom} remporte la partie avec {gagnant.score} points.")
        else :
            print("Il y a égalité.")
        pygame.quit()
        sys.exit()

    def verif_borne_revendicable(self):
        # Vérification d'activation du bouton Revendiquer
        liste = []
        for bornes in self.bornes.items():
            if bornes[1].controle_par is None:
                if len(bornes[1].joueur1_cartes) == 3 and len(bornes[1].joueur2_cartes) == 3:
                    liste.append(bornes[0])
        print(liste)
        return liste

    def choix_revendiquer(self, buttons_plateau, revendicable, joueur):
        revendiquer = False
        # mettre en "couleur" les bornes revendicables
        while not revendiquer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Vérifier si une borne revendicable est cliquée
                    for borne_key, borne_rect in buttons_plateau.items():
                        if borne_rect.collidepoint(event.pos):
                            numero_borne = int(borne_key.replace("borne", ""))
                            if numero_borne in revendicable:
                                self.revendiquer_borne(numero_borne, joueur)
                                revendiquer = True
                            else:
                                print("Cette borne n'est pas revendicable.")
            # Ajouter une condition pour éviter de rester bloqué
            if revendiquer:
                break

    def revendiquer_borne(self, numero_borne, joueur):
        """Méthode pour revendiquer une borne."""
        if self.bornes[numero_borne].controle_par is None:
            main_joueur1 = self.evaluer_mains(0, numero_borne)
            main_joueur2 = self.evaluer_mains(1, numero_borne)
            if main_joueur1 > main_joueur2:
                self.bornes[numero_borne].controle_par = self.joueurs[0]
                print(f"Borne {numero_borne} contrôlée par {self.joueurs[0].nom}")
                self.joueurs[0].borne_controlee += 1
            elif main_joueur2 < main_joueur1:
                self.bornes[numero_borne].controle_par = self.joueurs[1]
                print(f"Borne {numero_borne} contrôlée par {self.joueurs[1].nom}")
                self.joueurs[1].borne_controlee += 1
            else:
                somme_joueur1 = 0
                somme_joueur2 = 0
                for carte in self.bornes[numero_borne].joueur1_cartes:
                    somme_joueur1 += carte.force
                for carte in self.bornes[numero_borne].joueur2_cartes:
                    somme_joueur2 += carte.force
                if somme_joueur1 > somme_joueur2:
                    self.bornes[numero_borne].controle_par = self.joueurs[0]
                    print(f"Borne {numero_borne} contrôlée par {self.joueurs[0].nom}")
                    self.joueurs[0].borne_controlee += 1
                elif somme_joueur2 < somme_joueur1:
                    self.bornes[numero_borne].controle_par = self.joueurs[0]
                    print(f"Borne {numero_borne} contrôlée par {self.joueurs[1].nom}")
                    self.joueurs[1].borne_controlee += 1
                else:
                    self.bornes[numero_borne].controle_par = self.joueurs[joueur]
                    print(f"Borne {numero_borne} contrôlée par {self.joueurs[joueur].nom}")
                    self.joueurs[joueur].borne_controlee += 1


    def evaluer_mains(self, joueur, numero_borne):
        """Vérifie la meilleure combinaison possible parmi les cartes fournies."""
        # Trier les cartes par valeur
        if joueur == 0:
            combinaison = sorted(self.bornes[numero_borne].joueur1_cartes, key=lambda x: x.force)
        else:
            combinaison = sorted(self.bornes[numero_borne].joueur2_cartes, key=lambda x: x.force)


        forces = [carte.force for carte in combinaison]
        couleurs = [carte.couleur for carte in combinaison]

        # Vérifier Suite couleur (trois cartes de la même couleur successives)
        if len(set(couleurs)) == 1 and forces == list(range(forces[0], forces[0] + 3)):
            return 5

        # Vérifier Brelan (trois cartes de la même valeur)
        if any(forces.count(force) == 3 for force in forces):
            return 4

        # Vérifier Couleur (trois cartes de la même couleur)
        if len(set(couleurs)) == 1:
            return 3

        # Vérifier Suite (trois valeurs successives de couleurs quelconques)
        if forces == list(range(forces[0], forces[0] + 3)):
            return 2

        # Vérifier Somme (trois cartes quelconques)
        if len(combinaison) == 3:
            return 1

        return 0

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau, plateau, mode, nbr_manche):
        """Gère le déroulement d'une manche de jeu."""


        button_revendiquer = {"revendiquer": pygame.Rect(1050, 600, 200, 50)}
        button_passer = {"passer": pygame.Rect(1050, 660, 200, 50)}

        nombre_manche = 0
        while nombre_manche != nbr_manche:
            running = True
            joueur = 0
            while running:
                revendicable = self.verif_borne_revendicable()

                # Gérer les événements Pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Dessiner les boutons avec leurs images
                for button_key, button_rect in buttons_plateau.items():
                    screen_plateau.blit(buttons_images[button_key], button_rect.topleft)

                shadow_rect = button_revendiquer["revendiquer"].move(4, 4)
                pygame.draw.rect(screen_plateau, (160, 82, 45), shadow_rect, border_radius=10)

                shadow_rect = button_passer["passer"].move(4, 4)
                pygame.draw.rect(screen_plateau, (160, 82, 45), shadow_rect, border_radius=10)

                if revendicable != [] and mode == "expert":
                    button_color = (205, 200, 145)
                else:
                    button_color = (169, 169, 169)  # Grise si non activable

                config_button(screen_plateau, button_color, button_revendiquer["revendiquer"], "Revendiquer")
                config_button(screen_plateau, (169, 169, 169), button_passer["passer"], "Passer")

                buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main)
                pygame.display.flip()

                carte_index = None
                carte_contour = None
                borne_index = None
                borne_liste = None
                passer = False
                carte_rect_list = []

                while borne_index is None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if carte_index is None:
                                    if mode == "expert" and revendicable != []:
                                        if button_revendiquer["revendiquer"].collidepoint(event.pos):
                                            self.choix_revendiquer(buttons_plateau, revendicable, joueur)
                                            running = self.verifier_fin_manche()
                                else:
                                    for borne_key, borne_rect in buttons_plateau.items():
                                        if borne_rect.collidepoint(event.pos):
                                            numero_borne = int(borne_key.replace("borne", ""))
                                            if joueur == 0:
                                                if len(plateau.bornes[numero_borne].joueur1_cartes) < 3 and plateau.bornes[
                                                    numero_borne].controle_par is None:
                                                    borne_index = numero_borne
                                                    borne_liste = plateau.bornes[numero_borne].joueur1_cartes
                                                else:
                                                    print("Tu ne peux pas jouer sur cette borne.")
                                            elif joueur == 1:
                                                if len(plateau.bornes[numero_borne].joueur2_cartes) < 3 and plateau.bornes[
                                                    numero_borne].controle_par is None:
                                                    borne_index = numero_borne
                                                    borne_liste = plateau.bornes[numero_borne].joueur2_cartes
                                                else:
                                                    print("Tu ne peux pas jouer sur cette borne.")
                                for carte_key, carte_rect in buttons.items():
                                    carte_rect_list.append(carte_rect)
                                    if carte_rect.collidepoint(event.pos):
                                        config_button(screen_plateau, (169, 169, 169), button_revendiquer["revendiquer"], "Revendiquer")
                                        if carte_contour is not None:
                                            pygame.draw.rect(screen_plateau, (255, 255, 255), carte_contour, width=2)
                                            pygame.display.update(carte_contour)
                                        pygame.draw.rect(screen_plateau, (255, 0, 0), carte_rect, width=2)
                                        pygame.display.update(carte_rect)
                                        carte_index = carte_key
                                        carte_contour = carte_rect


                if borne_index is not None:
                    deplacer_carte(screen_plateau, joueur, self.joueurs[joueur].main[carte_index], borne_index, borne_liste)
                    pygame.draw.rect(screen_plateau, (205, 200, 145), carte_rect_list[carte_index], width=0)
                    pygame.display.update(carte_rect_list[carte_index])

                self.joueurs[joueur].jouer_carte(plateau, borne_index, self.joueurs[joueur].main[carte_index])
                self.joueurs[joueur].piocher(self.pioche)

                joueur = 1 - joueur
                pygame.display.update()

                revendicable = self.verif_borne_revendicable()

                while not passer:
                    config_button(screen_plateau, (205, 200, 145), button_passer["passer"], "Passer")
                    if revendicable:
                        config_button(screen_plateau, (205, 200, 145), button_revendiquer["revendiquer"], "Revendiquer")
                    else:
                        config_button(screen_plateau, (169, 169, 169), button_revendiquer["revendiquer"], "Revendiquer")
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if button_passer["passer"].collidepoint(event.pos):
                                passer = True
                            elif mode != "expert" and revendicable:
                                if button_revendiquer["revendiquer"].collidepoint(event.pos):
                                    self.choix_revendiquer(buttons_plateau, revendicable, joueur)
                                    revendicable = self.verif_borne_revendicable()
                                    running = self.verifier_fin_manche()
                                    if not running:
                                        passer = True
                                        break
                afficher_pioche(screen_plateau, self.pioche)
            nombre_manche += 1
            self.commencer_nouvelle_manche(mode, nbr_manche)
        self.fin_jeu()



def displayPlateau(plateau, mode, nbr_manche):
    """Fonction qui affiche le plateau."""
    pygame.init()

    # Initialisation de la fenêtre
    window_height = 750
    window_width = 1280
    pygame.display.set_caption("Schotten Totten : Jeux")
    screen_plateau = pygame.display.set_mode((window_width, window_height))

    # Récupération des chemins d'images
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    pioche_path = os.path.join(base_dir, "Ressources")
    borne_path = os.path.join(base_dir, "Ressources", "Bornes")
    images_paths = {
        "pioche": os.path.join(pioche_path, "Pioche.png"),
        "borne1": os.path.join(borne_path, "borne_0.jpg"),
        "borne2": os.path.join(borne_path, "borne_1.jpg"),
        "borne3": os.path.join(borne_path, "borne_2.jpg"),
        "borne4": os.path.join(borne_path, "borne_3.jpg"),
        "borne5": os.path.join(borne_path, "borne_4.jpg"),
        "borne6": os.path.join(borne_path, "borne_5.jpg"),
        "borne7": os.path.join(borne_path, "borne_6.jpg"),
        "borne8": os.path.join(borne_path, "borne_7.jpg"),
        "borne9": os.path.join(borne_path, "borne_8.jpg"),
    }

    # Boutons et leurs positions
    buttons = {
        "pioche": pygame.Rect(50, 300, 85, 150),
        **{f"borne{i}": pygame.Rect(210 + (i - 1) * 110, 350, 100, 50) for i in range(1, 10)},
    }

    # Chargement des images des boutons
    buttons_images = {}
    for i in range(1, 10):
        image_key = f"borne{i}"
        buttons_images[f"borne{i}"] = load_and_scale_image(
            images_paths[image_key],
            buttons[f"borne{i}"].width,
            buttons[f"borne{i}"].height,
        )
    buttons_images["pioche"] = load_and_scale_image(
        images_paths["pioche"], buttons["pioche"].width, buttons["pioche"].height
    )

    menu_running = True

    while menu_running:
        screen_plateau.fill((205, 200, 145))  # Fond de la fenêtre

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                sys.exit()  # Arrêt du programme

        afficher_pioche(screen_plateau, plateau.pioche)
        plateau.tour_de_jeu(screen_plateau, buttons_images, buttons, plateau, mode, nbr_manche)

        pygame.display.flip()


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def afficher_pioche(screen, pioche):
    rect_pioche = pygame.Rect(50, 455, 100, 40)  # Définir les dimensions du rectangle
    pygame.draw.rect(screen, (205, 200, 145), rect_pioche)

    smallfont = pygame.font.SysFont('Forte', 35)
    text_pioche = smallfont.render(str(len(pioche)), True, (139, 69, 19))
    rect_text = text_pioche.get_rect(center=rect_pioche.center)
    screen.blit(text_pioche, rect_text.topleft)

def load_and_scale_image(path, width, height):
    """Charge et redimensionne une image."""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image: {path}")
        raise e

def config_button(screen_plateau, button_color, button, text):
    smallfont = pygame.font.SysFont('Forte', 35)
    pygame.draw.rect(screen_plateau, button_color, button, border_radius=10)
    pygame.draw.rect(screen_plateau, (139, 69, 19), button, width=2, border_radius=10)
    text_jouer = smallfont.render(text, True, (139, 69, 19))
    text_rect_jouer = text_jouer.get_rect(center=button.center)
    screen_plateau.blit(text_jouer, text_rect_jouer)
    pygame.display.update(button)



