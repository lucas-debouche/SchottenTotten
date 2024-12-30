import time
from collections import deque

import pygame
import sys
import os

from ShottenTotten.Jeux.Carte import displayCarte, deplacer_carte, generer_cartes, config_button, CarteTactique, CarteClan, chemin, jouer_carte_troupes_elites
from ShottenTotten.Jeux.Joueur import load_and_scale_image
from ShottenTotten.Jeux.Popup import Popup
from ShottenTotten.Jeux.IA import *

current_dir, base_dir, carte_clan_path, carte_tactique_path, back_card_path = chemin()

class Borne:
    """Représente une borne sur le plateau avec des cartes et un contrôle."""

    def __init__(self):
        self.joueur1_cartes = []
        self.joueur2_cartes = []
        self.borne = []
        self.controle_par = None  # Joueur qui contrôle cette borne
        self.combat_de_boue = 3

class Plateau:
    """Représente le plateau de jeu avec ses bornes et sa défausse."""

    def __init__(self, nombre_bornes=9):
        self.bornes = {i: Borne() for i in range(1, nombre_bornes + 1)}
        self.defausse = []
        self.pioche_clan = deque()
        self.pioche_tactique = deque()
        self.nbr_cartes = None
        self.joueurs = []
        self.nbr_joueurs = None
        self.joueur_actuel = None

        # Initialisation de l'agent Q-Learning
        self.q_agent = QLearningAgent(actions=[], learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0)

    def to_state_representation(self):
        """
        Retourne une représentation de l'état pour Q-Learning.
        """
        state_repr = []
        for borne in self.bornes.values():
            # Convertir chaque élément de l'état en un tuple immuable
            state_repr.append((tuple(borne.joueur1_cartes), tuple(borne.joueur2_cartes), borne.controle_par))
        return tuple(state_repr)

    def evaluer_action(self, carte, numero_borne, joueur):
        """
        Évalue la qualité d'une action en fonction de son impact sur la formation de combinaisons.
        :param carte: Carte à jouer.
        :param numero_borne: Borne cible.
        :param joueur: Joueur (0 ou 1).
        :return: Score de l'action.
        """
        borne = self.bornes[numero_borne]
        cartes = borne.joueur1_cartes + [carte] if joueur == 0 else borne.joueur2_cartes + [carte]

        # Si plus de 3 cartes, ce n'est pas une action valide
        if len(cartes) > 3:
            return 0

        # Trier les cartes par force
        cartes = sorted(cartes, key=lambda x: x.force)
        forces = [c.force for c in cartes]
        couleurs = [c.couleur for c in cartes]

        # Évaluer la combinaison
        if len(cartes) == 3:
            if len(set(couleurs)) == 1 and forces == list(range(forces[0], forces[0] + 3)):
                return 10  # Suite couleur
            if any(forces.count(force) == 3 for force in forces):
                return 8  # Brelan
            if len(set(couleurs)) == 1:
                return 6  # Couleur
            if forces == list(range(forces[0], forces[0] + 3)):
                return 4  # Suite
            return 2  # Somme

        # Évaluer l'avancement vers une combinaison
        score = 0
        if len(set(couleurs)) == 1:  # Couleur partielle
            score += 2
        if len(forces) > 1 and forces[-1] - forces[0] == len(forces) - 1:  # Suite partielle
            score += 2
        return score

    def evaluer_action_globale(self, carte, numero_borne, joueur):
        """
        Évalue l'impact global de jouer une carte sur une borne spécifique.
        Prend en compte l'état des autres bornes et les cartes adverses.
        """
        score = self.evaluer_action(carte, numero_borne, joueur)

        # Simuler le contrôle de la borne après l'action
        borne = self.bornes[numero_borne]
        if joueur == 0:
            cartes = borne.joueur1_cartes + [carte]
        else:
            cartes = borne.joueur2_cartes + [carte]

        # Si jouer cette carte pourrait mener au contrôle de la borne
        if len(cartes) == 3 and self.gagnant_borne(numero_borne) == joueur:
            score += 10  # Bonus pour le contrôle potentiel de la borne

        # Ajouter le score global (proximité des conditions de victoire)
        score += self.evaluer_etat_global(joueur)

        return score

    def evaluer_etat_global(self, joueur):
        """
        Évalue l'état global du plateau pour le joueur.
        :param joueur: Index du joueur (0 ou 1).
        :return: Score basé sur la proximité des conditions de victoire.
        """
        score = 0
        bornes_controlees = [
            numero_borne
            for numero_borne, borne in self.bornes.items()
            if borne.controle_par == joueur
        ]

        # Score pour contrôler 5 bornes
        score += len(bornes_controlees) * 5  # Bonus par borne contrôlée

        # Score pour 3 bornes adjacentes
        bornes_controlees.sort()
        for i in range(len(bornes_controlees) - 2):
            if bornes_controlees[i] + 1 == bornes_controlees[i + 1] and bornes_controlees[i] + 2 == bornes_controlees[
                i + 2]:
                score += 20  # Bonus important pour 3 bornes adjacentes

        return score

    def calculate_reward(self, joueur, carte=None, numero_borne=None, revendication=False, nom_carte_tactique=None):
        """
        Calcule la récompense pour une action spécifique (jouer une carte ou revendiquer une borne).
        :param nom_carte_tactique:
        :param joueur: Le joueur qui effectue l'action.
        :param carte: La carte jouée (None si c'est une revendication).
        :param numero_borne: La borne ciblée.
        :param revendication: Indique si l'action est une revendication.
        :return: Récompense numérique.
        """
        reward = 0

        # Si l'action est une revendication
        reward = 0

        if revendication:
            if self.peut_revendiquer_borne(numero_borne, joueur):
                reward += 15  # Récompense pour revendication réussie
                # Bonus si cela contribue à 3 bornes adjacentes ou 5 bornes
                reward += self.evaluer_etat_global(joueur)
            else:
                reward -= 5  # Pénalité pour revendication échouée
            return reward

        if carte and numero_borne is not None:
            reward += self.evaluer_action(carte, numero_borne, joueur)

            # Bonus pour une action contribuant à contrôler une borne critique
            if self.gagnant_borne(numero_borne) == joueur:
                reward += 10

            # Bonus global
            reward += self.evaluer_etat_global(joueur)

        return reward

    def peut_revendiquer_borne(self, borne, j, nom_carte_tactique = None):
        """
        Vérifie si un joueur peut revendiquer une borne.
        """
        joueur = self.joueurs[j]
        joueur_adverse = self.joueurs[1 - j]

        if len(self.bornes[borne].joueur1_cartes) == self.bornes[borne].combat_de_boue and len(self.bornes[borne].joueur2_cartes) == self.bornes[borne].combat_de_boue:
            if self.bornes[borne].controle_par is None:
                main_joueur = self.evaluer_mains(joueur, borne, nom_carte_tactique)
                main_joueur_adverse = self.evaluer_mains(joueur_adverse, borne, nom_carte_tactique)
                if main_joueur > main_joueur_adverse:
                    return True
                elif main_joueur_adverse > main_joueur:
                    return False
                else:
                    somme_joueur = 0
                    somme_joueur_adverse = 0
                    for carte in self.bornes[borne].joueur1_cartes:
                        somme_joueur += carte.force
                    for carte in self.bornes[borne].joueur2_cartes:
                        somme_joueur_adverse += carte.force
                    if somme_joueur > somme_joueur_adverse:
                        return True
                    elif somme_joueur_adverse > somme_joueur:
                        return False
            else:
                return False
        else :
            return False

    def gagnant_borne(self, numero_borne):
        """
        Détermine quel joueur contrôle la borne spécifiée.
        :param numero_borne: Numéro de la borne.
        :return: 0 si le joueur 1 contrôle la borne, 1 si le joueur 2 la contrôle, None sinon.
        """
        borne = self.bornes[numero_borne]
        cartes_joueur1 = borne.joueur1_cartes
        cartes_joueur2 = borne.joueur2_cartes

        # Une borne ne peut être gagnée que si chaque joueur a joué le maximum de cartes autorisées
        if len(cartes_joueur1) < 3 or len(cartes_joueur2) < 3:
            return None

        # Évaluer les combinaisons des deux joueurs
        score_joueur1 = self.evaluer_mains(cartes_joueur1, numero_borne)
        score_joueur2 = self.evaluer_mains(cartes_joueur2, numero_borne)

        if score_joueur1 > score_joueur2:
            return 0  # Joueur 1 contrôle la borne
        elif score_joueur2 > score_joueur1:
            return 1  # Joueur 2 contrôle la borne
        else:
            return None  # Égalité ou borne encore contestée

    def joueur_courant(self):
        """ Retourne le joueur qui doit jouer actuellement."""
        return self.joueur_actuel

    def nombre_bornes(self):
        """Retourne le nombre total de bornes sur le plateau."""
        return len(self.bornes)


    def main_joueur(self, joueur):
        """ Retourne la main du joueur spécifié."""
        if isinstance(joueur, int):
            return self.joueurs[joueur].main
        elif joueur in self.joueurs:
            return joueur.main

    def peut_jouer_carte(self, borne, joueur):
        """ Vérifie si un joueur peut jouer une carte sur une borne spécifique."""
        if isinstance(joueur, int):
            joueur = self.joueurs[joueur]

        cartes_joueur = self.bornes[borne].joueur1_cartes if joueur == self.joueurs[0] else self.bornes[borne].joueur2_cartes

        # Vérifier que la borne n'est pas déjà revendiquée
        if self.bornes[borne].controle_par is not None:
            return False

        # Vérifier si le joueur a déjà joué le maximum de cartes autorisées sur cette borne
        self.bornes[borne].combat_de_boue = 3  # Exemple : 3 cartes max par borne
        if len(cartes_joueur) >= self.bornes[borne].combat_de_boue:
            return False

        return True

    def ajouter_carte(self, numero_borne, joueur_index, carte, capacite):
        """Ajoute une carte à une borne pour un joueur."""
        if numero_borne != 0:
            borne = self.bornes[numero_borne]
            if capacite == "Modes de combat":
                borne.borne.append(carte)
            else:
                if joueur_index == 0:
                    borne.joueur1_cartes.append(carte)
                elif joueur_index == 1:
                    borne.joueur2_cartes.append(carte)
        elif numero_borne == 0:
            self.defausse.append(carte)


    def initialiser_cartes(self, mode):
        """Initialise les cartes de clans et tactiques, puis mélange la pioche."""
        self.pioche_clan, self.pioche_tactique = generer_cartes()
        if mode == "classic":
            self.pioche_tactique = []
        random.shuffle(self.pioche_clan)
        random.shuffle(self.pioche_tactique)

    def commencer_nouvelle_manche(self, mode, nbr_manche):

        for joueur in self.joueurs:
            joueur.main = []
            joueur.borne_controlee = 0
        for borne in self.bornes:
            self.bornes[borne].controle_par = None
            self.bornes[borne].joueur1_cartes = []
            self.bornes[borne].joueur2_cartes = []
        self.pioche_clan.clear()
        self.pioche_tactique.clear()


        self.initialiser_cartes(mode)
        self.distribuer_cartes()
        self.displayPlateau(mode, nbr_manche, False, {})

    def distribuer_cartes(self):
        """Distribue les cartes aux joueurs au début de la partie."""
        for joueur in self.joueurs:
            for i in range(self.nbr_cartes):
                joueur.distribuer(self.pioche_clan)

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

        if len(self.pioche_clan) == 0 and len(self.pioche_tactique) == 0:
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
                if len(bornes[1].joueur1_cartes) == bornes[1].combat_de_boue and len(bornes[1].joueur2_cartes) == bornes[1].combat_de_boue:
                    liste.append(bornes[0])
        return liste

    def choix_revendiquer(self, buttons_plateau, revendicable, joueur, screen_plateau, nom_carte_tactique):
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
                                self.revendiquer_borne(numero_borne, joueur, screen_plateau, borne_rect, nom_carte_tactique)
                                revendiquer = True
            # Ajouter une condition pour éviter de rester bloqué
            if revendiquer:
                break

    def gagnant_revendiquer(self, numero_borne, joueur):
        self.bornes[numero_borne].controle_par = joueur
        self.joueurs[joueur].borne_controlee += 1

    def revendiquer_borne(self, numero_borne, joueur, screen_plateau, borne_rect, nom_carte_tactique):
        """Méthode pour revendiquer une borne."""
        joueur_adverse = 1 - joueur
        if len(self.bornes[numero_borne].joueur1_cartes) == self.bornes[numero_borne].combat_de_boue and len(self.bornes[numero_borne].joueur2_cartes) == self.bornes[numero_borne].combat_de_boue:
            if self.bornes[numero_borne].controle_par is None:
                main_joueur = self.evaluer_mains(joueur, numero_borne, nom_carte_tactique)
                main_joueur_adverse = self.evaluer_mains(joueur_adverse, numero_borne, nom_carte_tactique)
                print(main_joueur)
                print(main_joueur_adverse)
                if main_joueur > main_joueur_adverse:
                    self.gagnant_revendiquer(numero_borne, joueur)
                    if joueur == 0:
                        pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                        pygame.display.update(borne_rect)
                    elif joueur == 1:
                        pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                        pygame.display.update(borne_rect)

                #gerer les égalités en prenant en compte la force des cartes
                elif main_joueur > 1 and main_joueur_adverse > 1 and main_joueur_adverse == main_joueur :
                    combinaison = []
                    combinaison_adverse = []

                    if joueur == 0:
                        combinaison = sorted(self.bornes[numero_borne].joueur2_cartes, key=lambda x: x.force)
                        combinaison_adverse = sorted(self.bornes[numero_borne].joueur1_cartes, key=lambda x: x.force)
                    elif joueur == 1:
                        combinaison = sorted(self.bornes[numero_borne].joueur1_cartes, key=lambda x: x.force)
                        combinaison_adverse = sorted(self.bornes[numero_borne].joueur2_cartes, key=lambda x: x.force)

                    forces = [carte.force for carte in combinaison]
                    forces_adverse = [carte.force for carte in combinaison_adverse]

                    if forces[0] > forces_adverse[0]:
                        self.gagnant_revendiquer(numero_borne, joueur)
                        if joueur == 0:
                            pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                            pygame.display.update(borne_rect)
                        elif joueur == 1:
                            pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                            pygame.display.update(borne_rect)
                else:
                    somme_joueur = 0
                    somme_joueur_adverse = 0
                    for carte in self.bornes[numero_borne].joueur1_cartes:
                        somme_joueur += carte.force
                    for carte in self.bornes[numero_borne].joueur2_cartes:
                        somme_joueur_adverse += carte.force

                    if somme_joueur > somme_joueur_adverse:
                        self.gagnant_revendiquer(numero_borne, joueur)
                        if joueur == 0:
                            pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                            pygame.display.update(borne_rect)
                        elif joueur == 1:
                            pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                            pygame.display.update(borne_rect)


    def evaluer_mains(self, joueur, numero_borne, nom_carte_tactique = None):
        """Vérifie la meilleure combinaison possible parmi les cartes fournies."""
        if not nom_carte_tactique:
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


            if len(combinaison) == 3:
                # Vérifier Suite (trois valeurs successives de couleurs quelconques)
                if forces == list(range(forces[0], forces[0] + 3)):
                    return 2
                # Vérifier Somme (trois cartes quelconques)
                else:
                    return 1

            return 0
        elif nom_carte_tactique == "Colin-Maillard":
            return 0

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau, mode, nbr_manche, screen_width, screen_height):
        """Gère le déroulement d'une manche de jeu."""

        button_revendiquer = {"revendiquer": pygame.Rect(1250, 600, 200, 50)}
        button_passer = {"passer": pygame.Rect(1250, 660, 200, 50)}

        nombre_manche = 0
        while nombre_manche != nbr_manche:
            running = True
            joueur = 0
            self.joueur_actuel = joueur
            image_borne = {}
            nom_carte_tactique = None
            passer = False
            while running:
                revendicable = self.verif_borne_revendicable()

                if self.joueurs[joueur].nom == "IA":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                    time.sleep(0.5)
                    reward = 0
                    # Générer les actions possibles
                    self.q_agent.actions = generate_actions(self)
                    print(f"Actions disponibles : {self.q_agent.actions}")  # Affiche les actions générées

                    # L'IA choisit une action
                    current_state = self
                    action = self.q_agent.choose_action(self)
                    print(f"Action choisie par l'IA : {action}")
                    if action is None:
                        print("Aucune action possible pour l'IA. Passer le tour.")
                        self.joueur_actuel = 1 - self.joueur_actuel
                        return

                    if isinstance(action[0], CarteClan):
                        carte, borne = action
                        print(f"L'IA joue la carte {carte.force}-{carte.couleur} sur la borne {borne}")
                        reward = self.calculate_reward(self.joueur_actuel, carte, borne)
                        self.ajouter_carte(borne, self.joueur_actuel, carte, "")
                        self.joueurs[self.joueur_actuel].main.remove(carte)
                        if isinstance(carte, CarteTactique) and carte.capacite == "Modes de combat":
                            nom_carte_tactique = carte.nom

                        # Vérifiez les revendications possibles après avoir joué
                    revendications = [
                        ("REVENDIQUER", borne)
                        for borne in range(1, self.nombre_bornes() + 1)
                        if self.peut_revendiquer_borne(borne, self.joueur_actuel, nom_carte_tactique)
                    ]

                    for revendication in revendications:
                        _, borne = revendication
                        print(f"L'IA revendique la borne {borne}")
                        for i in range(1, 10):
                            if i == borne :
                                borne_rect = pygame.Rect(410 + (i - 1) * 110, 350, 100, 50)
                                reward = self.calculate_reward(self.joueur_actuel, numero_borne=borne, revendication=True, nom_carte_tactique=nom_carte_tactique)
                                self.revendiquer_borne(borne, self.joueur_actuel, screen_plateau, borne_rect, nom_carte_tactique)

                    # Calculer la récompense

                    # Mettre à jour la table Q
                    next_state = self
                    self.q_agent.update_q_value(self, action, reward, next_state)

                    # Réduire le taux d'exploration
                    self.q_agent.decay_exploration_rate()

                    car, bor = action

                    if joueur == 0:
                        deplacer_carte(screen_plateau, joueur, car, bor, self.bornes[bor].joueur1_cartes)
                    else:
                        deplacer_carte(screen_plateau, joueur, car, bor, self.bornes[bor].joueur2_cartes)
                    self.joueurs[joueur].piocher_ia(self.pioche_clan, self.pioche_tactique, "pioche_clan")
                    pygame.display.update()

                    if not self.verifier_fin_manche():
                        nombre_manche += 1
                        self.commencer_nouvelle_manche(mode, nbr_manche)
                    else:
                        # Passer au joueur suivant
                        joueur = 1 - joueur
                        self.joueur_actuel = joueur
                        passer = True

                else:
                    # Gérer les événements Pygame
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                    # Affichage des composants sur la surface hors écran
                    for button_key, button_rect in buttons_plateau.items():
                        if button_key == "pioche_tactique" or button_key == "defausse":
                            if mode != "classic":
                                screen_plateau.blit(buttons_images[button_key], button_rect.topleft)
                        else:
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

                    buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main, False)
                    pygame.display.flip()

                    carte_index = None
                    carte_contour = None
                    borne_index = None
                    passer = False
                    carte_rect_list = []
                    carte_selectionnee = [None]
                    capacite = None


                    while borne_index is None:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                    if carte_index is None:
                                        if mode == "expert" and revendicable != []:
                                            if button_revendiquer["revendiquer"].collidepoint(event.pos):
                                                self.choix_revendiquer(buttons_plateau, revendicable, joueur, screen_plateau, nom_carte_tactique)
                                                running = self.verifier_fin_manche()
                                    else:
                                        if isinstance(carte_selectionnee[0], CarteTactique) and carte_selectionnee[0].capacite == "Ruses":
                                            for borne_key, borne_rect in buttons_plateau.items():
                                                if borne_rect.collidepoint(event.pos) and borne_key == "defausse":
                                                    borne_index = 0
                                        else:
                                            for borne_key, borne_rect in buttons_plateau.items():
                                                if borne_rect.collidepoint(event.pos) and borne_key.startswith("borne"):
                                                    numero_borne = int(borne_key.replace("borne", ""))
                                                    if isinstance(carte_selectionnee[0], CarteClan) or capacite != "Modes de combat" or (capacite == "Modes de combat"  and not self.bornes[numero_borne].borne):
                                                        if joueur == 0:
                                                            if len(self.bornes[numero_borne].joueur1_cartes) < self.bornes[numero_borne].combat_de_boue and self.bornes[
                                                                numero_borne].controle_par is None:
                                                                borne_index = numero_borne
                                                        elif joueur == 1:
                                                            if len(self.bornes[numero_borne].joueur2_cartes) < self.bornes[numero_borne].combat_de_boue and self.bornes[
                                                                numero_borne].controle_par is None:
                                                                borne_index = numero_borne
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
                                            carte_selectionnee[0] = self.joueurs[joueur].main[carte_index]
                                            if isinstance(carte_selectionnee[0], CarteTactique):
                                                capacite = carte_selectionnee[0].capacite

                    if borne_index is not None:
                        if isinstance(carte_selectionnee[0], CarteTactique):
                            if carte_selectionnee[0].capacite == "Troupes d'élites":
                                carte_selectionnee[0] = jouer_carte_troupes_elites(carte_selectionnee[0], screen_plateau, screen_width, screen_height, self.pioche_clan, self.pioche_tactique)
                                self.joueurs[joueur].main[carte_index] = carte_selectionnee[0]
                            elif carte_selectionnee[0].capacite == "Modes de combat":
                                nom_carte_tactique = carte_selectionnee[0].nom
                                if nom_carte_tactique == "Combat de Boue":
                                    self.bornes[borne_index].combat_de_boue = 4
                                carte_tactique = os.path.join(carte_tactique_path, f"{carte_selectionnee[0].nom}.jpg")
                                image_key = f"borne{borne_index}"
                                buttons_images[image_key] = load_and_scale_image(carte_tactique,100,50, carte_selectionnee[0].capacite)
                                image_borne[image_key] = carte_tactique
                            elif carte_selectionnee[0].capacite == "Ruses":
                                self.joueurs[joueur].main.remove(carte_selectionnee[0])
                                self.jouer_carte_ruse(carte_selectionnee[0], joueur, screen_plateau, screen_width, screen_height)

                        self.displayPlateau(mode, nbr_manche, True, image_borne)
                        config_button(screen_plateau, (169, 169, 169), button_passer["passer"], "Passer")
                        config_button(screen_plateau, (169, 169, 169), button_revendiquer["revendiquer"], "Revendiquer")
                        displayCarte(screen_plateau, joueur, self.joueurs[joueur].main, False)
                        for i in range(1, 10):
                            for carte in self.bornes[i].joueur1_cartes:
                                deplacer_carte(screen_plateau, 0, carte, i, self.bornes[i].joueur1_cartes)
                            for carte in self.bornes[i].joueur2_cartes:
                                deplacer_carte(screen_plateau, 1, carte, i, self.bornes[i].joueur2_cartes)
                        carte_choisi = self.joueurs[joueur].jouer_carte(self, borne_index, self.joueurs[joueur].main[carte_index], capacite)

                        if capacite != "Modes de combat" and capacite != "Ruses":
                            if joueur == 0:
                                deplacer_carte(screen_plateau, joueur, carte_choisi, borne_index, self.bornes[borne_index].joueur1_cartes)
                            else:
                                deplacer_carte(screen_plateau, joueur, carte_choisi, borne_index, self.bornes[borne_index].joueur2_cartes)

                            pygame.draw.rect(screen_plateau, (205, 200, 145), carte_rect_list[carte_index], width=0)
                            pygame.display.update(carte_rect_list[carte_index])


                    pygame.display.update()
                    if not (isinstance(carte_selectionnee[0], CarteTactique) and carte_selectionnee[0].nom == "Chasseur de Tête"):
                        self.joueurs[joueur].piocher(self.pioche_clan, self.pioche_tactique, buttons_plateau, screen_plateau)


                    joueur = 1 - joueur
                    self.joueur_actuel = joueur



                    revendicable = self.verif_borne_revendicable()

                while not passer or (len(self.pioche_clan) > 0 and len(self.pioche_tactique) > 0):
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
                                    self.choix_revendiquer(buttons_plateau, revendicable, joueur, screen_plateau, nom_carte_tactique)
                                    revendicable = self.verif_borne_revendicable()
                                    running = self.verifier_fin_manche()
                                    if not running:
                                        passer = True
                                        break
                afficher_pioche(60, screen_plateau, self.pioche_clan, "clan")

                if mode != "classic":
                    afficher_pioche(190, screen_plateau, self.pioche_tactique, "tactique")
                    afficher_pioche(325, screen_plateau, self.defausse, "defausse")

            nombre_manche += 1
            self.commencer_nouvelle_manche(mode, nbr_manche)
        self.fin_jeu()

    def displayPlateau(self, mode, nbr_manche, game_running, image_borne):
        """Fonction qui affiche le plateau."""
        pygame.init()

        # Initialisation de la fenêtre
        window_height = 750
        window_width = 1480
        pygame.display.set_caption("Schotten Totten : Jeux")
        screen_plateau = pygame.display.set_mode((window_width, window_height))

        # Récupération des chemins d'images
        pioche_path = os.path.join(base_dir, "Ressources")
        borne_path = os.path.join(base_dir, "Ressources", "Bornes")
        images_paths = {
            "pioche_clan": os.path.join(pioche_path, "Pioche.png"),
            "pioche_tactique": os.path.join(pioche_path, "Pioche.png"),
            **{f"borne{i}": os.path.join(borne_path, f"borne_{i - 1}.jpg") for i in range(1, 10)},
        }

        # Chargement des images des boutons
        buttons_images = {}
        for i in range(1, 10):
            image_key = f"borne{i}"
            buttons_images[image_key] = load_and_scale_image(images_paths[image_key],100,50, None)
        for borne_key, borne_path  in image_borne.items():
            buttons_images[borne_key] = load_and_scale_image(borne_path,100,50, "Modes de combat")
        buttons_images["pioche_clan"] = load_and_scale_image(images_paths["pioche_clan"], 85, 150, None)
        buttons_images["pioche_tactique"] = load_and_scale_image(images_paths["pioche_tactique"], 85, 150, None)
        buttons_images["defausse"] = load_and_scale_image(os.path.join(base_dir, "Ressources", "Back_Card.jpg"), 85, 150, None)

        buttons = {
            "pioche_clan": pygame.Rect(20, 300, 85, 150),
            "pioche_tactique": pygame.Rect(150, 300, 85, 150),
            "defausse" : pygame.Rect(280, 300, 85, 150),
            **{f"borne{i}": pygame.Rect(410 + (i - 1) * 110, 350, 100, 50) for i in range(1, 10)},
        }

        menu_running = True

        while menu_running:
            # Efface la surface hors écran
            screen_plateau.fill((205, 200, 145))  # Fond de la surface

            # Affichage des composants sur la surface hors écran
            for button_key, button_rect in buttons.items():
                if button_key == "pioche_tactique" or button_key == "defausse":
                    if mode != "classic":
                        screen_plateau.blit(buttons_images[button_key], button_rect.topleft)
                else:
                    screen_plateau.blit(buttons_images[button_key], button_rect.topleft)

            afficher_pioche(60, screen_plateau, self.pioche_clan, "clan")
            if mode != "classic":
                afficher_pioche(190, screen_plateau, self.pioche_tactique, "tactique")
                afficher_pioche(325, screen_plateau, self.defausse, "defausse")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    pygame.quit()
                    sys.exit()  # Arrêt du programme

            if not game_running:
                self.tour_de_jeu(screen_plateau, buttons_images, buttons, mode, nbr_manche, window_width, window_height)
            else:
                break

    def jouer_chasseur_de_tete(self, joueur, screen, screen_width, screen_height, capacite, pioche_clan, pioche_tactique):
        """Joue la carte Chasseur de Tête."""
        # Popup pour choisir deux cartes à remettre sous la pioche
        popup = Popup(screen, screen_width, screen_height, None)
        choix_pioche_clan, choix_pioche_tactique = popup.show(capacite, pioche_clan, pioche_tactique)

        # Piochez trois cartes
        cartes_piochees = []
        while choix_pioche_clan + choix_pioche_tactique > 0:
            if choix_pioche_clan:
                cartes_piochees.append(self.pioche_clan.popleft())
                choix_pioche_clan -= 1
            if choix_pioche_tactique:
                cartes_piochees.append(self.pioche_tactique.popleft())
                choix_pioche_tactique -= 1

        main = cartes_piochees + self.joueurs[joueur].main

        screen.fill((165, 140, 100))
        cards = displayCarte(screen, 2, main, True)
        button_valider = {"valider": pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 240, 150, 50)}

        pygame.draw.rect(screen, (205, 200, 145), button_valider["valider"])  # Fond clair
        pygame.draw.rect(screen, (0, 0, 0), button_valider["valider"], width=2)  # Bordure noire
        text_surface = pygame.font.Font(None, 36).render("Valider", True, (0, 0, 0))
        screen.blit(text_surface, text_surface.get_rect(center=button_valider["valider"].center))

        pygame.display.flip()

        choix_carte = []
        valider = False

        while not valider:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if len(choix_carte) == 2:
                        if button_valider["valider"].collidepoint(event.pos):
                            valider = True
                    for carte_key, carte_rect in cards.items():
                        if carte_rect.collidepoint(event.pos):
                            if carte_key not in choix_carte:
                                if len(choix_carte) < 2:
                                    choix_carte.append(carte_key)
                                    pygame.draw.rect(screen, (255, 0, 0), carte_rect, width=2)  # Contour rouge
                                    pygame.display.update(carte_rect)
                            else:
                                choix_carte.remove(carte_key)
                                pygame.draw.rect(screen, (255, 255, 255), carte_rect, width=2)  # Contour blanc
                                pygame.display.update(carte_rect)

        # Remettre les cartes choisies sous la pioche
        for carte_index in choix_carte:
            carte = main[carte_index]
            if isinstance(carte, CarteClan):
                pioche_clan.append(carte)
            elif isinstance(carte, CarteTactique):
                pioche_tactique.append(carte)
            main.remove(carte)

        return main

    def jouer_stratege(self, joueur, screen, screen_width, screen_height):
        """Joue la carte Stratège."""
        # Choisir une carte à déplacer
        cartes_joueur = self.bornes[joueur].joueur1_cartes  # Cartes du joueur
        popup = Popup(screen, screen_width, screen_height, None)
        carte_a_deplacer = popup.show_single_choice("Choisissez une carte à déplacer.")

        # Choisir une Borne de destination
        bornes_non_revendiquees = [i for i, borne in self.bornes.items() if borne.controle_par is None]
        popup = Popup(screen, screen_width, screen_height, None)
        borne_destination = popup.show_single_choice("Choisissez une Borne de destination.")

        if carte_a_deplacer and borne_destination:
            # Déplacer la carte vers la Borne choisie
            self.bornes[borne_destination].joueur1_cartes.append(carte_a_deplacer)

    """def jouer_banshee(self, screen, screen_width, screen_height):
        """"Joue la carte Banshee.""""
        # Choisissez une carte adverse à défausser
        cartes_adverses = [carte for borne in self.bornes.values() for carte in borne.joueur2_cartes if borne.controle_par is None]
        popup = Popup(screen, screen_width, screen_height, None)
        carte_a_défausser = popup.show_single_choice("Choisissez une carte adverse à défausser.")

        if carte_a_défausser:
            self.defausse.append(carte_a_défausser)

    def jouer_traitre(self, screen, screen_width, screen_height):
        """"Joue la carte Traître.""""
        # Choisissez une carte adverse à déplacer
        cartes_adverses = [carte for borne in self.bornes.values() for carte in borne.joueur2_cartes if
                           borne.controle_par is None]
        popup = Popup(screen, screen_width, screen_height, None)
        carte_a_deplacer = popup.show_single_choice("Choisissez une carte adverse à déplacer.")

        if carte_a_deplacer:
            # Déplacez la carte vers une Borne non revendiquée de votre côté
            bornes_non_revendiquees = [i for i, borne in self.bornes.items() if borne.controle_par is None]
            popup = Popup(screen, screen_width, screen_height, None)
            borne_destination = popup.show_single_choice("Choisissez une Borne pour placer la carte.")

            self.bornes[borne_destination].joueur1_cartes.append(carte_a_deplacer)"""

    def jouer_carte_ruse(self, carte, joueur, screen, screen_width, screen_height):
        """Joue une carte Tactique Ruse et l'ajoute à la défausse."""
        if carte.nom == "Chasseur de Tête":
            self.joueurs[joueur].main = self.jouer_chasseur_de_tete(joueur, screen, screen_width, screen_height, carte.capacite, self.pioche_clan, self.pioche_tactique)
        elif carte.nom == "Stratège":
            self.jouer_stratege(joueur, screen, screen_width, screen_height)
        """elif carte.nom == "Banshee":
            self.jouer_banshee(screen, screen_width, screen_height)
        elif carte.nom == "Traître":
            self.jouer_traitre(screen, screen_width, screen_height)"""

def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def afficher_pioche(x, screen, pioche, mode):
    rect_ = pygame.Rect(x - 30, 455, 100, 40)  # Définir les dimensions du rectangle
    pygame.draw.rect(screen, (205, 200, 145), rect_)

    smallfont = pygame.font.SysFont('Forte', 35)
    nombre_pioche = smallfont.render(str(len(pioche)), True, (139, 69, 19))
    rect_text = nombre_pioche.get_rect(center=rect_.center)
    rect_text.x -= 20
    screen.blit(nombre_pioche, rect_text.topleft)
    nom_pioche = smallfont.render(mode, True, (139, 69, 19))
    rect_text = nom_pioche.get_rect(center=rect_.center)
    rect_text.y -= rect_.height // 2 + 180
    rect_text.x -= 20
    screen.blit(nom_pioche, rect_text.topleft)





