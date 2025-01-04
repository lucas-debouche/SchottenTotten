import threading

from SchottenTotten.Jeux.Joueur import *
from SchottenTotten.Jeux.IA import *

current_dir, base_dir, carte_clan_path, carte_tactique_path, back_card_path = chemin()
pygame.init()
smallfont = pygame.font.SysFont('Forte', 35)

class Borne:
    """Représente une borne sur le plateau avec des cartes et un contrôle."""

    def __init__(self):
        self.joueur1_cartes = []
        self.joueur2_cartes = []
        self.borne = []
        self.controle_par = None  # Joueur qui contrôle cette borne
        self.combat_de_boue = 3


def evaluer_mains_supp(joueur, borne, cartes_supp=None):
    """Évalue la meilleure combinaison possible pour l'ia sur une borne si elle ajoute une carte sur celle-ci."""
    cartes = list(borne.joueur1_cartes if joueur == 0 else borne.joueur2_cartes)
    if cartes_supp:
        cartes.extend(cartes_supp)

    # Trier les cartes par valeur
    cartes.sort(key=lambda c: c.force)

    # Évaluer les combinaisons possibles
    forces = [c.force for c in cartes]
    couleurs = [c.couleur for c in cartes]

    # Vérifier Suite couleur (trois cartes de la même couleur successives)
    if len(set(couleurs)) == 1 and len(forces) >= 3 and all(
            forces[i] + 1 == forces[i + 1] for i in range(len(forces) - 1)):
        return 10

    # Vérifier Brelan (trois cartes de la même valeur)
    if any(forces.count(f) >= 3 for f in forces):
        return 8

    # Vérifier Couleur (trois cartes de la même couleur)
    if len(set(couleurs)) == 1:
        return 6

    # Vérifier Suite (trois valeurs successives de couleurs quelconques)
    if len(forces) >= 3 and all(forces[i] + 1 == forces[i + 1] for i in range(len(forces) - 1)):
        return 4

    # Vérifier Somme (trois cartes quelconques)
    return sum(forces) if len(forces) <= 3 else sum(sorted(forces, reverse=True)[:3])


def evaluer_compatibilite_carte(carte, main):
    """Évalue la compatibilité d'une carte avec les combinaisons potentielles de la main."""
    forces = [c.force for c in main if isinstance(c, CarteClan) and c != carte]
    couleurs = [c.couleur for c in main if isinstance(c, CarteClan) and c != carte]

    score = 0

    # Bonus si la carte peut compléter une suite
    if carte.force - 1 in forces and carte.force + 1 in forces:
        score += 5

    # Bonus si la carte peut compléter un brelan
    if forces.count(carte.force) == 2:
        score += 4

    # Bonus si la carte peut compléter une couleur
    if couleurs.count(carte.couleur) >= 2:
        score += 3

    return score


def simuler_ajout_carte(borne, joueur, valeur, couleur):
    """Simule l'ajout d'une carte à une borne et retourne le score obtenu."""
    carte_temp = CarteClan(valeur, couleur)
    cartes_temp = borne.joueur1_cartes + [carte_temp] if joueur == 0 else borne.joueur2_cartes + [carte_temp]
    return evaluer_mains_supp(joueur, borne, cartes_supp=cartes_temp)


def ia_choisir_cartes_a_remettre(main):
    """Sélectionne les deux cartes les moins utiles pour l'IA à remettre sous la pioche."""
    cartes_evaluees = []
    for carte in main:
        if isinstance(carte, CarteClan):
            compatibilite = evaluer_compatibilite_carte(carte, main)
            cartes_evaluees.append((carte, compatibilite))
        else:
            cartes_evaluees.append((carte, 0))  # Priorité basse pour les cartes tactiques inutiles

    cartes_evaluees.sort(key=lambda x: x[1])
    return [c[0] for c in cartes_evaluees[:2]]


def determiner_meilleure_valeur_couleur_porte_bouclier(borne, joueur):
    """Détermine la meilleure valeur et couleur pour un Porte-Bouclier sur une borne donnée."""
    valeurs = [1, 2, 3]
    couleurs = ["rouge", "vert", "bleu", "jaune", "violet", "orange"]
    meilleure_combinaison = (0, "")
    meilleur_score = 0

    for valeur in valeurs:
        for couleur in couleurs:
            score = simuler_ajout_carte(borne, joueur, valeur, couleur)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_combinaison = (valeur, couleur)

    return meilleure_combinaison


def determiner_meilleure_valeur_couleur_joker(borne, joueur):
    """Détermine la meilleure valeur et couleur pour un Joker sur une borne donnée."""
    valeurs = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    couleurs = ["rouge", "vert", "bleu", "jaune", "violet", "orange"]
    meilleure_combinaison = (0, "")
    meilleur_score = 0

    for valeur in valeurs:
        for couleur in couleurs:
            score = simuler_ajout_carte(borne, joueur, valeur, couleur)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_combinaison = (valeur, couleur)

    return meilleure_combinaison


def determiner_meilleure_couleur_espion(borne, joueur):
    """Détermine la meilleure couleur pour un Espion sur une borne donnée."""
    couleurs = ["rouge", "vert", "bleu", "jaune", "violet", "orange"]
    meilleur_score = 0
    meilleure_couleur = ""

    for couleur in couleurs:
        score = simuler_ajout_carte(borne, joueur, 7, couleur)
        if score > meilleur_score:
            meilleur_score = score
            meilleure_couleur = couleur

    return meilleure_couleur


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
        self.nbr_manches = None

        # Initialisation de l'agent Q-Learning
        self.neural_agent = None

    def to_state_representation(self):
        """Retourne une représentation de l'état pour Q-Learning."""
        state_repr = []
        for borne in self.bornes.values():
            # Convertir chaque élément de l'état en un tuple immuable
            state_repr.append((tuple(borne.joueur1_cartes), tuple(borne.joueur2_cartes), borne.controle_par))
        return tuple(state_repr)

    def generate_actions(self):
        """Génère toutes les actions possibles pour le joueur actuel."""
        joueur = self.joueur_courant()
        actions = []

        # Actions pour jouer une carte
        for carte in self.main_joueur(joueur) or []:
            if isinstance(carte, CarteTactique):
                if carte.capacite == "Ruses":
                    actions.append((carte, "RUSE"))
                elif carte.capacite == "Modes de combat":
                    for borne in range(1, self.nombre_bornes() + 1):
                        if not self.bornes[borne].borne:
                            actions.append((carte, borne))
            else:
                for borne in range(1, self.nombre_bornes() + 1):
                    if self.peut_jouer_carte(borne, joueur):
                        actions.append((carte, borne))

        # Actions pour revendiquer une borne
        for borne in range(1, self.nombre_bornes() + 1):
            if self.peut_revendiquer_borne(borne, joueur):
                actions.append(("REVENDIQUER", borne))

        return actions

    def evaluer_action(self, carte, numero_borne, joueur):
        """Évalue la qualité d'une action en fonction de son impact sur la formation de combinaisons."""
        borne = self.bornes[numero_borne]
        cartes = borne.joueur1_cartes + [carte] if joueur == 0 else borne.joueur2_cartes + [carte]

        if isinstance(carte, CarteTactique):
            if carte.capacite == "Ruses":
                return 5
            elif carte.capacite == "Modes de combat":
                return 3

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
        """Évalue l'impact global de jouer une carte sur une borne spécifique."""
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
        """Évalue l'état global du plateau pour le joueur."""
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

    def calculate_reward(self, joueur, carte=None, numero_borne=None, revendication=False):
        """Calcule la récompense pour une action spécifique (jouer une carte ou revendiquer une borne)."""

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
        """Vérifie si un joueur peut revendiquer une borne."""
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
        """Détermine quel joueur contrôle la borne spécifiée."""
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
        """Retourne la main du joueur spécifié."""
        if isinstance(joueur, int):
            return self.joueurs[joueur].main
        elif joueur in self.joueurs:
            return joueur.main
        return []

    def peut_jouer_carte(self, borne, joueur):
        """Vérifie si un joueur peut jouer une carte sur une borne spécifique."""
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

    def commencer_nouvelle_manche(self, mode, nbr_manche, entrainement):
        """Commence une nouvelle manche."""
        self.reset_plateau(mode)
        self.displayPlateau(mode, nbr_manche, False, {}, entrainement)

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
                self.joueurs[joueur].score += 1
                print(f"{joueur.nom} remporte la manche (5 bornes contrôlées).")
                return False

            # Vérifier si un joueur contrôle 3 bornes consécutives
            consecutives = 0
            for numero_borne, borne in self.bornes.items():
                if borne.controle_par == joueur:
                    consecutives += 1
                    if consecutives == 3:
                        self.joueurs[joueur].score += 1
                        print(f"{joueur.nom} remporte la manche (3 bornes consécutives).")
                        return False
                else:
                    consecutives = 0

        if len(self.pioche_clan) == 0 and len(self.pioche_tactique) == 0:
            if self.joueurs[0].borne_controlee > self.joueurs[1].borne_controlee:
                self.joueurs[0].score += 1
                print(f"{self.joueurs[0].nom} remporte la manche (plus de bornes contrôlées que {self.joueurs[1].nom}).")
                return False
            elif self.joueurs[0].borne_controlee < self.joueurs[1].borne_controlee:
                self.joueurs[1].score += 1
                print(f"{self.joueurs[1].nom} remporte la manche (plus de bornes contrôlées que {self.joueurs[0].nom}).")
                return False
            else:
                print(f"{self.joueurs[0].nom} et {self.joueurs[1].nom} ne marque pas de point (même nombre de bornes contrôlées).")
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
        """Retourne les bornes revendicables."""
        # Vérification d'activation du bouton Revendiquer
        liste = []
        for bornes in self.bornes.items():
            if bornes[1].controle_par is None:
                if len(bornes[1].joueur1_cartes) == bornes[1].combat_de_boue and len(bornes[1].joueur2_cartes) == bornes[1].combat_de_boue:
                    liste.append(bornes[0])
        return liste

    def choix_revendiquer(self, buttons_plateau, revendicable, joueur, screen_plateau, nom_carte_tactique):
        """Vérifie si une borne peut être revendiquée"""
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
        """Attribue les points au gagnant d'une revendication"""
        self.bornes[numero_borne].controle_par = joueur
        self.joueurs[joueur].borne_controlee += 1

    def revendiquer_borne(self, numero_borne, joueur, screen_plateau, borne_rect, nom_carte_tactique):
        """Méthode pour revendiquer une borne."""
        joueur_adverse = 1 - joueur
        if len(self.bornes[numero_borne].joueur1_cartes) == self.bornes[numero_borne].combat_de_boue and len(self.bornes[numero_borne].joueur2_cartes) == self.bornes[numero_borne].combat_de_boue:
            if self.bornes[numero_borne].controle_par is None:
                main_joueur = self.evaluer_mains(joueur, numero_borne, nom_carte_tactique)
                main_joueur_adverse = self.evaluer_mains(joueur_adverse, numero_borne, nom_carte_tactique)
                if main_joueur > main_joueur_adverse:
                    self.gagnant_revendiquer(numero_borne, joueur)
                    if borne_rect:
                        if joueur == 0:
                            pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                            pygame.display.update(borne_rect)
                        elif joueur == 1:
                            pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                            pygame.display.update(borne_rect)

                #gerer les égalités en prenant en compte la force des cartes
                elif 1 < main_joueur == main_joueur_adverse and main_joueur_adverse > 1:
                    combinaison = []
                    combinaison_adverse = []

                    if joueur == 0:
                        combinaison = sorted(self.bornes[numero_borne].joueur1_cartes, key=lambda x: x.force)
                        combinaison_adverse = sorted(self.bornes[numero_borne].joueur2_cartes, key=lambda x: x.force)
                    elif joueur == 1:
                        combinaison = sorted(self.bornes[numero_borne].joueur2_cartes, key=lambda x: x.force)
                        combinaison_adverse = sorted(self.bornes[numero_borne].joueur1_cartes, key=lambda x: x.force)

                    forces = [carte.force for carte in combinaison]
                    forces_adverse = [carte.force for carte in combinaison_adverse]

                    if forces[0] > forces_adverse[0]:
                        self.gagnant_revendiquer(numero_borne, joueur)
                        if borne_rect:
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
                        if borne_rect:
                            if joueur == 0:
                                pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                                pygame.display.update(borne_rect)
                            elif joueur == 1:
                                pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                                pygame.display.update(borne_rect)


    def evaluer_mains(self, joueur, numero_borne, nom_carte_tactique = None):
        """Vérifie la meilleure combinaison possible parmi les cartes fournies."""
        if not nom_carte_tactique or "Combat de Boue":
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

    def tour_de_jeu(self, screen_plateau, buttons_images, buttons_plateau, mode, nbr_manche, screen_width, screen_height, entrainement):
        """Gère le déroulement d'une manche de jeu."""

        button_revendiquer = {"revendiquer": pygame.Rect(1250, 600, 200, 50)}
        button_passer = {"passer": pygame.Rect(1250, 660, 200, 50)}

        if nbr_manche:
            self.nbr_manches = nbr_manche
        nombre_manche = 0
        while nombre_manche < self.nbr_manches:
            running = True
            joueur = 0
            self.joueur_actuel = joueur
            image_borne = {}
            nom_carte_tactique = None
            passer = False

            if self.neural_agent is None:
                self.neural_agent = NeuralQLearningAgent(
                    input_size=len(self.bornes) * 4,  # Chaque borne a 4 caractéristiques
                    action_size=len(self.generate_actions()),  # Actions possibles
                    mode=mode,
                    learning_rate=0.001,
                    discount_factor=0.9,
                    exploration_rate=1.0,
                    exploration_decay=0.99,
                    batch_size = 64
                )
            total_reward = 0
            while running:
                revendicable = self.verif_borne_revendicable()
                if self.joueurs[joueur].nom.startswith("IA"):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    #time.sleep(0.5)
                    reward = 0
                    # Conversion de l'état actuel en vecteur
                    current_state_vector = convert_plateau_to_vector(self)

                    # Génération des actions possibles
                    possible_actions = self.generate_actions()
                    self.neural_agent.action_size = len(possible_actions)

                    # Choix de l'action par l'agent
                    action = self.neural_agent.choose_action(current_state_vector, list(range(len(possible_actions))))
                    chosen_action = possible_actions[action]

                    # Si l'IA choisit une carte tactique
                    if isinstance(chosen_action[0], CarteTactique):
                        carte = chosen_action[0]
                        if carte.capacite == "Modes de combat":
                            borne_index = self.jouer_carte_tactique_ia(carte, joueur, screen_plateau)
                            nom_carte_tactique = carte.nom
                            if nom_carte_tactique == "Combat de Boue":
                                self.bornes[borne_index].combat_de_boue = 4
                            carte_tactique = os.path.join(carte_tactique_path, f"{carte.nom}.jpg")
                            image_key = f"borne{borne_index}"
                            buttons_images[image_key] = load_and_scale_image(carte_tactique, 100, 50, carte.capacite)
                            image_borne[image_key] = carte_tactique
                        else:
                            self.jouer_carte_tactique_ia(carte, joueur, screen_plateau)

                        self.displayPlateau(mode, nbr_manche, True, image_borne, False)
                        for borne_key, borne_rect in buttons_plateau.items():
                            if borne_key != "pioche_clan" and borne_key != "pioche_tactique" and borne_key != "defausse":
                                numero_borne = int(borne_key.replace("borne", ""))
                                if self.bornes[numero_borne].controle_par == 0:
                                    pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                                    pygame.display.update(borne_rect)
                                elif self.bornes[numero_borne].controle_par == 1:
                                    pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                                    pygame.display.update(borne_rect)
                        for i in range(1, 10):
                            for carte in self.bornes[i].joueur1_cartes:
                                deplacer_carte(screen_plateau, 0, carte, i, self.bornes[i].joueur1_cartes)
                            for carte in self.bornes[i].joueur2_cartes:
                                deplacer_carte(screen_plateau, 1, carte, i, self.bornes[i].joueur2_cartes)
                        pygame.display.update()

                    elif isinstance(chosen_action[0], CarteClan):
                        carte, borne = chosen_action
                        reward = self.calculate_reward(self.joueur_actuel, carte, borne)
                        self.ajouter_carte(borne, self.joueur_actuel, carte, "")
                        self.joueurs[self.joueur_actuel].main.remove(carte)
                        car, bor = chosen_action
                        if joueur == 0:
                            deplacer_carte(screen_plateau, joueur, car, bor, self.bornes[bor].joueur1_cartes)
                        else:
                            deplacer_carte(screen_plateau, joueur, car, bor, self.bornes[bor].joueur2_cartes)

                    elif chosen_action[0] == "REVENDIQUER":
                        _, borne = chosen_action
                        reward = self.calculate_reward(self.joueur_actuel, numero_borne=borne, revendication=True)
                        for i in range(1, 10):
                            if i == borne :
                                borne_rect = pygame.Rect(410 + (i - 1) * 110, 350, 100, 50)
                                self.revendiquer_borne(borne, self.joueur_actuel, screen_plateau, borne_rect, None)
                    # Ajoutez une vérification explicite des revendications restantes
                    revendications = [
                        ("REVENDIQUER", borne)
                        for borne in range(1, self.nombre_bornes() + 1)
                        if self.peut_revendiquer_borne(borne, self.joueur_actuel, nom_carte_tactique)
                    ]

                    for revendication in revendications:
                        _, borne = revendication
                        reward = self.calculate_reward(self.joueur_actuel, numero_borne=borne, revendication=True)
                        borne_rect = pygame.Rect(410 + (borne - 1) * 110, 350, 100, 50)
                        self.revendiquer_borne(borne, self.joueur_actuel, screen_plateau, borne_rect, None)


                    # Nouvel état après l'action
                    next_state_vector = convert_plateau_to_vector(self)
                    possible_next_actions = self.generate_actions()

                    done = not self.verifier_fin_manche()
                    # Mise à jour du réseau neuronal
                    self.neural_agent.train_on_experience(
                        current_state_vector, action, reward, next_state_vector,
                        list(range(len(possible_next_actions))), done, mode
                    )

                    if mode != "classic":
                        if len(self.pioche_clan) > 0 and len(self.pioche_tactique) > 0:
                            self.joueurs[joueur].piocher_ia(self.pioche_clan, self.pioche_tactique, random.choice(["pioche_clan", "pioche_tactique"]))
                        elif len(self.pioche_clan) == 0 and len(self.pioche_tactique) > 0:
                            self.joueurs[joueur].piocher_ia(self.pioche_clan, self.pioche_tactique, "pioche_tactique")
                        elif len(self.pioche_clan) > 0 and len(self.pioche_tactique) == 0:
                            self.joueurs[joueur].piocher_ia(self.pioche_clan, self.pioche_tactique, "pioche_clan")

                    else:
                        self.joueurs[joueur].piocher_ia(self.pioche_clan, self.pioche_tactique,"pioche_clan")
                    pygame.display.update()

                    total_reward += reward
                    # Décroissance du taux d'exploration
                    self.neural_agent.decay_exploration_rate()

                    if not self.verifier_fin_manche():
                        self.neural_agent.log_performance(total_reward, mode)
                        running = False
                    else:
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

                    config_button(screen_plateau, button_color, smallfont, button_revendiquer["revendiquer"], "Revendiquer")
                    config_button(screen_plateau, (169, 169, 169), smallfont, button_passer["passer"], "Passer")

                    buttons = displayCarte(screen_plateau, joueur, self.joueurs[joueur].main, False)
                    for borne_key, borne_rect in buttons_plateau.items():
                        if borne_key != "pioche_clan" and borne_key != "pioche_tactique" and borne_key != "defausse":
                            numero_borne = int(borne_key.replace("borne", ""))
                            if self.bornes[numero_borne].controle_par == 0:
                                pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                                pygame.display.update(borne_rect)
                            elif self.bornes[numero_borne].controle_par == 1:
                                pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                                pygame.display.update(borne_rect)
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
                                    if not carte_index:
                                        if mode == "expert" and revendicable != []:
                                            if button_revendiquer["revendiquer"].collidepoint(event.pos):
                                                self.choix_revendiquer(buttons_plateau, revendicable, joueur, screen_plateau, nom_carte_tactique)
                                                running = self.verifier_fin_manche()
                                    for carte_key, carte_rect in buttons.items():
                                        carte_rect_list.append(carte_rect)
                                        if carte_rect.collidepoint(event.pos):
                                            config_button(screen_plateau, (169, 169, 169), smallfont, button_revendiquer["revendiquer"], "Revendiquer")
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
                                    if carte_index is not None :
                                        if isinstance(carte_selectionnee[0], CarteTactique) and carte_selectionnee[0].capacite == "Ruses":
                                            for borne_key, borne_rect in buttons_plateau.items():
                                                if borne_rect.collidepoint(event.pos) and borne_key == "defausse":
                                                    j = None
                                                    choisir_defausse = False
                                                    if carte_selectionnee[0].nom == "Banshee" or carte_selectionnee[0].nom == "Traître":
                                                        j = 1 - joueur
                                                    elif carte_selectionnee[0].nom == "Stratège":
                                                        j = joueur
                                                    if j is not None:
                                                        for index, borne in self.bornes.items():
                                                            if j == 0:
                                                                if len(borne.joueur1_cartes):
                                                                    choisir_defausse = True
                                                            if j == 1:
                                                                if len(borne.joueur2_cartes):
                                                                    choisir_defausse = True
                                                    else:
                                                        choisir_defausse = True
                                                    if choisir_defausse:
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
                                if carte_selectionnee[0].nom == "Chasseur de Tête":
                                    self.joueurs[joueur].main.remove(carte_selectionnee[0])
                                self.jouer_carte_ruse(carte_selectionnee[0], joueur, screen_plateau, screen_width, screen_height, buttons_plateau, buttons_images)

                        self.displayPlateau(mode, nbr_manche, True, image_borne, False)
                        for borne_key, borne_rect in buttons_plateau.items():
                            if borne_key != "pioche_clan" and borne_key != "pioche_tactique" and borne_key != "defausse":
                                numero_borne = int(borne_key.replace("borne", ""))
                                if self.bornes[numero_borne].controle_par == 0:
                                    pygame.draw.rect(screen_plateau, (255, 0, 0), borne_rect, width=2)
                                    pygame.display.update(borne_rect)
                                elif self.bornes[numero_borne].controle_par == 1:
                                    pygame.draw.rect(screen_plateau, (0, 0, 255), borne_rect, width=2)
                                    pygame.display.update(borne_rect)
                        config_button(screen_plateau, (169, 169, 169), smallfont, button_passer["passer"], "Passer")
                        config_button(screen_plateau, (169, 169, 169), smallfont, button_revendiquer["revendiquer"], "Revendiquer")
                        displayCarte(screen_plateau, joueur, self.joueurs[joueur].main, False)
                        for i in range(1, 10):
                            for carte in self.bornes[i].joueur1_cartes:
                                deplacer_carte(screen_plateau, 0, carte, i, self.bornes[i].joueur1_cartes)
                            for carte in self.bornes[i].joueur2_cartes:
                                deplacer_carte(screen_plateau, 1, carte, i, self.bornes[i].joueur2_cartes)
                        carte_choisi = self.joueurs[joueur].jouer_carte(self, borne_index, carte_selectionnee[0], capacite)

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

                while not passer:
                    config_button(screen_plateau, (205, 200, 145), smallfont, button_passer["passer"], "Passer")
                    if revendicable:
                        config_button(screen_plateau, (205, 200, 145), smallfont, button_revendiquer["revendiquer"], "Revendiquer")
                    else:
                        config_button(screen_plateau, (169, 169, 169), smallfont, button_revendiquer["revendiquer"], "Revendiquer")
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
                self.afficher_pioches(screen_plateau, (205, 200, 145), mode)

            nombre_manche += 1
            self.commencer_nouvelle_manche(mode, None, entrainement)
        self.fin_jeu()

    def afficher_pioches(self, screen_plateau, couleur, mode):
        """Affiche les différentes pioches"""
        afficher_pioche(60, screen_plateau, self.pioche_clan, "clan", couleur)
        if mode != "classic":
            afficher_pioche(190, screen_plateau, self.pioche_tactique, "tactique", couleur)
            afficher_pioche(325, screen_plateau, self.defausse, "defausse", couleur)


    def displayPlateau(self, mode, nbr_manche, game_running, image_borne, entrainement):
        """Fonction qui affiche le plateau."""
        pygame.init()

        # Initialisation de la fenêtre
        window_height = 750
        window_width = 1480
        pygame.display.set_caption("Schotten Totten : Jeux")
        screen_plateau = pygame.display.set_mode((window_width, window_height))
        if not entrainement:
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

                self.afficher_pioches(screen_plateau, (205, 200, 145), mode)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        menu_running = False
                        pygame.quit()
                        sys.exit()  # Arrêt du programme

                if not game_running and nbr_manche:
                    self.tour_de_jeu(screen_plateau, buttons_images, buttons, mode, nbr_manche, window_width, window_height, entrainement)
                else:
                    break
        else:
            fenetre_attente(self, nbr_manche, mode)

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

        config_button(screen, (169, 169, 169), smallfont, button_valider["valider"], "Valider")

        pygame.display.flip()

        choix_carte = []
        valider = False

        while not valider:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                    if len(choix_carte) == 2:
                        config_button(screen, (205, 200, 145), smallfont, button_valider["valider"], "Valider")
                        if button_valider["valider"].collidepoint(event.pos):
                            valider = True
                    else:
                        config_button(screen, (169, 169, 169), smallfont, button_valider["valider"], "Valider")

        carte = []
        # Remettre les cartes choisies sous la pioche
        for carte_index in choix_carte:
            carte.append(main[carte_index])
            if isinstance(carte, CarteClan):
                pioche_clan.append(carte)
            elif isinstance(carte, CarteTactique):
                pioche_tactique.append(carte)
        for i in carte:
            main.remove(i)
        return main

    def jouer_stratege_banshee_traitre(self, joueur, screen, screen_width, screen_height, buttons_plateau, buttons_images, nom):
        """Joue la carte Stratège."""
        screen.fill((165, 140, 100))
        cards = {}
        if nom == "Banshee" or nom == "Traître":
            joueur = 1 - joueur

        if joueur == 0:
            for i in range(1, 10):
                cards[i] = []
                for carte in reversed(self.bornes[i].joueur1_cartes):
                    cards[i].append((carte, deplacer_carte(screen, joueur, carte, i, self.bornes[i].joueur1_cartes)))
        elif joueur == 1:
            for i in range(1, 10):
                cards[i] = []
                for carte in reversed(self.bornes[i].joueur2_cartes):
                    cards[i].append(
                        (carte, deplacer_carte(screen, joueur, carte, i, self.bornes[i].joueur2_cartes)))

        for button_key, button_rect in buttons_plateau.items():
            if button_key.startswith("borne") or (button_key == "defausse" and nom != "Traître"):
                screen.blit(buttons_images[button_key], button_rect.topleft)
                afficher_pioche(325, screen, self.defausse, "defausse", (165, 140, 100))

        button_valider = {"valider": pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 240, 150, 50)}
        config_button(screen, (169, 169, 169), smallfont, button_valider["valider"], "Valider")

        pygame.display.flip()

        carte_choisie = None
        borne_initiale = None
        borne_choisie = None

        valider = False
        # Choisir une carte à déplacer
        while not valider:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for borne_index, cartes in cards.items():
                        for carte_clan, carte_rect in reversed(cartes):  # Parcourir dans l'ordre inversé
                            if carte_rect.collidepoint(event.pos) and not self.bornes[borne_index].controle_par:
                                if not carte_choisie:
                                    carte_choisie = carte_clan
                                    borne_initiale = borne_index
                                    pygame.draw.rect(screen, (255, 0, 0), carte_rect, width=2)  # Contour rouge
                                    pygame.display.update(carte_rect)
                                else:
                                    carte_choisie = None
                                    borne_initiale = None
                                    pygame.draw.rect(screen, (255, 255, 255), carte_rect, width=2)  # Contour blanc
                                    pygame.display.update(carte_rect)
                                break
                    if carte_choisie:
                        for borne_key, borne_rect in buttons_plateau.items():
                            if borne_rect.collidepoint(event.pos):
                                if borne_key == "defausse" and nom != "Traître":
                                    borne_choisie = 0
                                elif nom != "Banshee":
                                    numero_borne = int(borne_key.replace("borne", ""))
                                    if joueur == 0:
                                        if len(self.bornes[numero_borne].joueur2_cartes) < self.bornes[
                                            numero_borne].combat_de_boue and not self.bornes[
                                            numero_borne].controle_par:
                                            borne_choisie = numero_borne
                                    elif joueur == 1:
                                        if len(self.bornes[numero_borne].joueur1_cartes) < self.bornes[
                                            numero_borne].combat_de_boue and not self.bornes[
                                            numero_borne].controle_par:
                                            borne_choisie = numero_borne
                    if carte_choisie is not None and borne_choisie is not None:
                        config_button(screen, (205, 200, 145), smallfont, button_valider["valider"], "Valider")
                        if button_valider["valider"].collidepoint(event.pos):
                            valider = True
                    else:
                        config_button(screen, (169, 169, 169), smallfont, button_valider["valider"], "Valider")

        # Déplacer la carte vers la Borne choisie
        if nom == "Stratège":
            if carte_choisie and borne_choisie and valider:
                if joueur == 0:
                    self.bornes[borne_initiale].joueur1_cartes.remove(carte_choisie)
                    if borne_choisie != 0:
                        self.bornes[borne_choisie].joueur1_cartes.append(carte_choisie)
                    else:
                        self.defausse.append(carte_choisie)
                elif joueur == 1:
                    self.bornes[borne_initiale].joueur2_cartes.remove(carte_choisie)
                    if borne_choisie != 0:
                        self.bornes[borne_choisie].joueur2_cartes.append(carte_choisie)
                    else:
                        self.defausse.append(carte_choisie)
        elif nom == "Banshee":
            if carte_choisie and borne_initiale and valider:
                if joueur == 0:
                    self.bornes[borne_initiale].joueur1_cartes.remove(carte_choisie)
                elif joueur == 1:
                    self.bornes[borne_initiale].joueur2_cartes.remove(carte_choisie)
                self.defausse.append(carte_choisie)
        elif nom == "Traître":
            if carte_choisie and borne_choisie and valider:
                if joueur == 0:
                    self.bornes[borne_initiale].joueur1_cartes.remove(carte_choisie)
                    self.bornes[borne_choisie].joueur2_cartes.append(carte_choisie)
                elif joueur == 1:
                    self.bornes[borne_initiale].joueur2_cartes.remove(carte_choisie)
                    self.bornes[borne_choisie].joueur1_cartes.append(carte_choisie)

    def jouer_carte_ruse(self, carte, joueur, screen, screen_width, screen_height, buttons_plateau, buttons_image):
        """Joue une carte Tactique Ruse et l'ajoute à la défausse."""
        if carte.nom == "Chasseur de Tête":
            self.joueurs[joueur].main = self.jouer_chasseur_de_tete(joueur, screen, screen_width, screen_height, carte.capacite, self.pioche_clan, self.pioche_tactique)
        elif carte.nom == "Stratège":
            self.jouer_stratege_banshee_traitre(joueur, screen, screen_width, screen_height, buttons_plateau, buttons_image, carte.nom)
        elif carte.nom == "Banshee":
            self.jouer_stratege_banshee_traitre(joueur, screen, screen_width, screen_height, buttons_plateau, buttons_image, carte.nom)
        elif carte.nom == "Traître":
            self.jouer_stratege_banshee_traitre(joueur, screen, screen_width, screen_height, buttons_plateau, buttons_image, carte.nom)

    def entrainement_rapide(self, nombre_essais, mode):
        """Lance un nombre de parties simulées un certain nombre de fois"""
        self.reset_plateau(mode)
        for i in range(nombre_essais):
            print(f"Partie {i + 1}/{nombre_essais} en cours...")
            self.partie_simulee()
            self.reset_plateau(mode)  # Réinitialiser le plateau pour une nouvelle partie

    def partie_simulee(self):
        """Jouer une partie rapidement sans affichage."""
        total_reward = 0
        self.joueur_actuel = 0

        if self.neural_agent is None:
            self.neural_agent = NeuralQLearningAgent(
                input_size=len(self.bornes) * 4,  # Chaque borne a 4 caractéristiques
                action_size=len(self.generate_actions()),  # Actions possibles
                mode="classic",
                learning_rate=0.001,
                discount_factor=0.9,
                exploration_rate=1.0,
                exploration_decay=0.99,
                batch_size=64
            )
        while self.verifier_fin_manche():

            # IA 1 joue
            state = convert_plateau_to_vector(self)
            possible_actions = self.generate_actions()
            self.neural_agent.action_size = len(possible_actions)
            action = self.neural_agent.choose_action(state, list(range(len(possible_actions))))
            action_choisie = possible_actions[action]
            reward0 = self.effectuer_action(state, action_choisie, action)  # Exécuter l'action choisie par l'IA

            # IA 2 joue (même logique)
            state = convert_plateau_to_vector(self)
            possible_actions = self.generate_actions()
            self.neural_agent.action_size = len(possible_actions)
            action = self.neural_agent.choose_action(state, list(range(len(possible_actions))))
            action_choisie = possible_actions[action]
            reward1 = self.effectuer_action(state, action_choisie, action)

            total_reward = reward0 + reward1

        self.neural_agent.log_performance(total_reward, "classic")

    def reset_plateau(self, mode):
        """Réinitialise le plateau."""
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

    def effectuer_action(self, state, action_choisie, action):
        """Gère le tour de l'ia en entrainement"""
        reward = 0

        if isinstance(action_choisie[0], CarteClan):
            objet, borne = action_choisie
            reward = self.calculate_reward(self.joueur_actuel, objet, borne)
            self.ajouter_carte(borne, self.joueur_actuel, objet, "")
            self.joueurs[self.joueur_actuel].main.remove(objet)

        elif action_choisie[0] == "REVENDIQUER":
            _, borne = action_choisie
            reward = self.calculate_reward(self.joueur_actuel, numero_borne=borne, revendication=True)
            for i in range(1, 10):
                if i == borne:
                    borne_rect = None
                    self.revendiquer_borne(borne, self.joueur_actuel, None, borne_rect, None)

        # Ajoutez une vérification explicite des revendications restantes
        revendications = [
            ("REVENDIQUER", borne)
            for borne in range(1, self.nombre_bornes() + 1)
            if self.peut_revendiquer_borne(borne, self.joueur_actuel)
        ]

        for revendication in revendications:
            _, borne = revendication
            reward = self.calculate_reward(self.joueur_actuel, numero_borne=borne, revendication=True)
            borne_rect = None
            self.revendiquer_borne(borne, self.joueur_actuel, None, borne_rect, None)

        # Nouvel état après l'action
        next_state_vector = convert_plateau_to_vector(self)
        possible_next_actions = self.generate_actions()

        done = not self.verifier_fin_manche()
        # Mise à jour du réseau neuronal
        self.neural_agent.train_on_experience(
            [carte.to_dict() if isinstance(carte, CarteClan) else carte for carte in state], action, reward, next_state_vector,
            list(range(len(possible_next_actions))), done
        )

        # Décroissance du taux d'exploration
        self.neural_agent.decay_exploration_rate()

        self.joueurs[self.joueur_actuel].piocher_ia(self.pioche_clan, self.pioche_tactique, "pioche_clan")

        self.joueur_actuel = 1 - self.joueur_actuel
        return reward

    def jouer_carte_tactique_ia(self, carte, joueur, screen_plateau):
        """Gère automatiquement le jeu des cartes tactiques par l'IA en respectant les règles spécifiques de chaque carte."""
        self.joueurs[joueur].main.remove(carte)
        if carte.nom == "Stratège":
            # Déplacer une carte d'une borne à une autre pour maximiser le gain
            meilleur_score = -float('inf')
            carte_choisie = None
            borne_initiale = None
            borne_cible = None

            for numero_borne, borne in self.bornes.items():
                cartes = borne.joueur1_cartes if joueur == 0 else borne.joueur2_cartes
                for carte_test in cartes:
                    for cible, borne_cible_test in self.bornes.items():
                        if cible != numero_borne and not borne_cible_test.controle_par:
                            score = self.evaluer_action_globale(carte_test, cible, joueur)
                            if score > meilleur_score:
                                meilleur_score = score
                                carte_choisie = carte_test
                                borne_initiale = numero_borne
                                borne_cible = cible

            #Appliquer l'effet
            print(f"IA joue 'Stratège' de la borne: {borne_initiale} sur la borne: {borne_cible} avec la carte: {carte_choisie}.")
            if carte_choisie and borne_cible:
                if joueur == 0:
                    self.bornes[borne_initiale].joueur1_cartes.remove(carte_choisie)
                    if borne_cible != 0:
                        self.bornes[borne_cible].joueur1_cartes.append(carte_choisie)
                    else:
                        self.defausse.append(carte_choisie)
                elif joueur == 1:
                    self.bornes[borne_initiale].joueur2_cartes.remove(carte_choisie)
                    if borne_cible != 0:
                        self.bornes[borne_cible].joueur2_cartes.append(carte_choisie)
                    else:
                        self.defausse.append(carte_choisie)

        elif carte.nom == "Banshee":
            # Déplacer une carte de l'adversaire à la défausse
            meilleur_carte = None
            meilleur_borne = None

            for numero_borne, borne in self.bornes.items():
                cartes = borne.joueur2_cartes if joueur == 0 else borne.joueur1_cartes
                for carte_test in cartes:
                    score = self.evaluer_action_globale(carte_test, numero_borne, joueur)
                    if score > 0:  # Toute carte peut être un bon choix pour diminuer l'adversaire
                        meilleur_carte = carte_test
                        meilleur_borne = numero_borne

            # Appliquer l'effet
            print(f"IA joue 'Banshee' enlève la carte: {meilleur_carte} de la borne: {meilleur_borne}.")
            if meilleur_carte and meilleur_borne:
                if joueur == 0:
                    self.bornes[meilleur_borne].joueur2_cartes.remove(meilleur_carte)
                elif joueur == 1:
                    self.bornes[meilleur_borne].joueur1_cartes.remove(meilleur_carte)
                self.defausse.append(meilleur_carte)

        elif carte.nom == "Traître":
            # Déplacer une carte de l'adversaire vers une borne non contrôlée
            meilleur_carte = None
            borne_initiale = None
            borne_cible = None
            meilleur_score = -float('inf')

            for numero_borne, borne in self.bornes.items():
                cartes = borne.joueur2_cartes if joueur == 0 else borne.joueur1_cartes
                for carte_test in cartes:
                    for cible, borne_cible_test in self.bornes.items():
                        if cible != numero_borne and not borne_cible_test.controle_par:
                            score = self.evaluer_action_globale(carte_test, cible, joueur)
                            if score > meilleur_score:
                                meilleur_score = score
                                meilleur_carte = carte_test
                                borne_initiale = numero_borne
                                borne_cible = cible

            # Appliquer l'effet
            print(f"IA joue 'Traite' de la borne: {borne_initiale} sur la borne: {borne_cible} avec la carte: {meilleur_carte}.")
            if meilleur_carte and borne_cible:
                if joueur == 0:
                    self.bornes[borne_initiale].joueur2_cartes.remove(meilleur_carte)
                    self.bornes[borne_cible].joueur1_cartes.append(meilleur_carte)
                elif joueur == 1:
                    self.bornes[borne_initiale].joueur1_cartes.remove(meilleur_carte)
                    self.bornes[borne_cible].joueur2_cartes.append(meilleur_carte)

        elif carte.nom == "Colin-Maillard":
            # Ajouter un effet aveugle à une borne (empêche l'évaluation)
            meilleur_borne = None
            for numero_borne, borne in self.bornes.items():
                if not borne.controle_par:
                    meilleur_borne = numero_borne
                    break

            # Appliquer l'effet
            print(f"IA joue 'Colin Maillard' sur la Borne {meilleur_borne}.")
            return meilleur_borne

        elif carte.nom == "Combat de Boue":
            # Augmente le nombre de cartes nécessaires pour revendiquer une Borne
            borne_cible = self.choisir_borne_pour_combat_de_boue(joueur)
            if borne_cible:
                self.bornes[borne_cible].combat_de_boue = 4
                print(f"IA joue 'Combat de Boue' sur la Borne {borne_cible}.")
            else:
                print("Aucune Borne valide pour 'Combat de Boue'.")

            # Appliquer l'effet
            return borne_cible

        elif carte.nom == "Chasseur de Tête":
            # Permet de piocher trois cartes et en renvoyer deux sous la pioche
            cartes_piochees = []

            # Piocher trois cartes de la ou des pioches disponibles
            for _ in range(3):
                if self.pioche_clan:
                    cartes_piochees.append(self.pioche_clan.popleft())
                elif self.pioche_tactique:
                    cartes_piochees.append(self.pioche_tactique.popleft())

            print(f"IA pioche les cartes : {[str(c) for c in cartes_piochees]}.")

            # Ajouter les cartes piochées à la main de l'IA
            self.joueurs[joueur].main.extend(cartes_piochees)

            # Choisir deux cartes à remettre sous la pioche
            cartes_a_remettre = ia_choisir_cartes_a_remettre(self.joueurs[joueur].main)
            for carte_a_remettre in cartes_a_remettre:
                self.joueurs[joueur].main.remove(carte_a_remettre)
                if isinstance(carte_a_remettre, CarteClan):
                    self.pioche_clan.append(carte_a_remettre)
                else:
                    self.pioche_tactique.append(carte_a_remettre)

            print(f"IA remet les cartes {[str(c) for c in cartes_a_remettre]} sous la pioche.")

        elif carte.nom == "Joker":
            # Permet de jouer un Joker en choisissant la meilleure couleur et valeur
            borne_index, borne_cible = self.choisir_borne_pour_joker(joueur)
            if borne_cible:
                valeur, couleur = determiner_meilleure_valeur_couleur_joker(borne_cible, joueur)
                carte_choisis = CarteClan(couleur, valeur)
                borne_cible.joueur1_cartes.append(carte_choisis) if joueur == 0 else borne_cible.joueur2_cartes.append(carte_choisis)
                print(f"IA joue 'Joker' avec valeur {valeur} et couleur {couleur} sur la Borne {borne_cible}.")
                if joueur == 0:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur1_cartes)
                else:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur2_cartes)


        elif carte.nom == "Espion":
            # Permet de jouer un Espion en choisissant une couleur optimale
            borne_index, borne_cible = self.choisir_borne_pour_espion(joueur)
            if borne_cible:
                couleur = determiner_meilleure_couleur_espion(borne_cible, joueur)
                carte_choisis = CarteClan(couleur, 7)
                borne_cible.joueur1_cartes.append(carte_choisis) if joueur == 0 else borne_cible.joueur2_cartes.append(carte_choisis)
                print(f"IA joue 'Espion' avec couleur {couleur} sur la Borne {borne_cible}.")
                if joueur == 0:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur1_cartes)
                else:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur2_cartes)

        elif carte.nom == "Porte-Bouclier":
            # Permet de jouer un Porte-Bouclier avec une valeur et une couleur optimales
            borne_index, borne_cible = self.choisir_borne_pour_porte_bouclier(joueur)
            if borne_cible:
                valeur, couleur = determiner_meilleure_valeur_couleur_porte_bouclier(borne_cible, joueur)
                carte_choisis = CarteClan(couleur, valeur)
                borne_cible.joueur1_cartes.append(carte_choisis) if joueur == 0 else borne_cible.joueur2_cartes.append(carte_choisis)
                print(f"IA joue 'Porte-Bouclier' avec valeur {valeur} et couleur {couleur} sur la Borne {borne_cible}.")
                if joueur == 0:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur1_cartes)
                else:
                    deplacer_carte(screen_plateau, joueur, carte_choisis, borne_cible, self.bornes[borne_index].joueur2_cartes)

        else:
            raise ValueError(f"Capacité inconnue pour la carte tactique: {carte.capacite}")

    def choisir_borne_pour_combat_de_boue(self, joueur):
        """Sélectionne la meilleure borne pour jouer 'Combat de Boue'."""
        meilleures_bornes = []
        for numero_borne, borne in self.bornes.items():
            if borne.controle_par is None and len(borne.joueur1_cartes) == 2 and len(borne.joueur2_cartes) == 2:
                score_joueur = self.evaluer_mains(joueur, numero_borne)
                score_adversaire = self.evaluer_mains(1 - joueur, numero_borne)
                if score_adversaire > score_joueur:
                    meilleures_bornes.append((numero_borne, score_adversaire - score_joueur))
            else:
                meilleures_bornes.append((random.randint(1, 9), 0 ))

        if meilleures_bornes:
            meilleures_bornes.sort(key=lambda x: x[1], reverse=True)
            return meilleures_bornes[0][0]
        return None

    def choisir_borne_pour_joker(self, joueur):
        """Sélectionne la meilleure borne pour jouer 'Joker'."""
        meilleures_bornes = []
        for numero_borne, borne in self.bornes.items():
            if borne.controle_par is None:
                score_avant = self.evaluer_mains(joueur, numero_borne)
                score_apres = score_avant + 10  # Supposition d'un boost important avec le Joker
                meilleures_bornes.append((numero_borne, score_apres - score_avant))

        if meilleures_bornes:
            meilleures_bornes.sort(key=lambda x: x[1], reverse=True)
            return meilleures_bornes[0][0], self.bornes[meilleures_bornes[0][0]]
        return None

    def choisir_borne_pour_espion(self, joueur):
        """Sélectionne la meilleure borne pour jouer 'Espion'."""
        meilleures_bornes = []
        for numero_borne, borne in self.bornes.items():
            if borne.controle_par is None:
                score_avant = self.evaluer_mains(joueur, numero_borne)
                score_apres = score_avant + 5  # Supposition d'un boost modéré avec l'Espion
                meilleures_bornes.append((numero_borne, score_apres - score_avant))

        if meilleures_bornes:
            meilleures_bornes.sort(key=lambda x: x[1], reverse=True)
            return meilleures_bornes[0][0], self.bornes[meilleures_bornes[0][0]]
        return None

    def choisir_borne_pour_porte_bouclier(self, joueur):
        """Sélectionne la meilleure borne pour jouer 'Porte-Bouclier'."""
        meilleures_bornes = []
        for numero_borne, borne in self.bornes.items():
            if borne.controle_par is None:
                score_avant = self.evaluer_mains(joueur, numero_borne)
                score_apres = score_avant + 3  # Supposition d'un boost léger avec le Porte-Bouclier
                meilleures_bornes.append((numero_borne, score_apres - score_avant))

        if meilleures_bornes:
            meilleures_bornes.sort(key=lambda x: x[1], reverse=True)
            return meilleures_bornes[0][0], self.bornes[meilleures_bornes[0][0]]
        return None


def melanger_pioche(cartes_clans, cartes_tactiques):
    """Mélange les cartes et retourne une pioche."""
    pioche = cartes_clans + cartes_tactiques
    random.shuffle(pioche)
    return deque(pioche)

def afficher_pioche(x, screen, pioche, mode, couleur):
    """Affiche la pioche en fonction du mode"""
    rect_ = pygame.Rect(x - 30, 455, 100, 40)  # Définir les dimensions du rectangle
    pygame.draw.rect(screen, couleur, rect_)

    nombre_pioche = smallfont.render(str(len(pioche)), True, (139, 69, 19))
    rect_text = nombre_pioche.get_rect(center=rect_.center)
    rect_text.x -= 20
    screen.blit(nombre_pioche, rect_text.topleft)
    nom_pioche = smallfont.render(mode, True, (139, 69, 19))
    rect_text = nom_pioche.get_rect(center=rect_.center)
    rect_text.y -= rect_.height // 2 + 180
    rect_text.x -= 20
    screen.blit(nom_pioche, rect_text.topleft)

def fenetre_attente(plateau, nbr_manche, mode):
    """Affiche une fenêtre d'attente pendant l'entraînement."""
    # Initialiser pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Entraînement en cours...")
    font = pygame.font.Font(None, 50)

    # Lancer l'entraînement dans un thread séparé
    thread_entrainement = threading.Thread(target=plateau.entrainement_rapide, args=(nbr_manche, mode))
    thread_entrainement.start()

    # Boucle principale de la fenêtre
    clock = pygame.time.Clock()
    training_done = False
    progress = 0
    while not training_done:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Vérifier si l'entraînement est terminé
        training_done = not thread_entrainement.is_alive()

        # Calculer la progression
        progress = min(progress + (1 / nbr_manche), 1.0) if thread_entrainement.is_alive() else 1.0

        # Dessiner la barre de progression
        pygame.draw.rect(screen, (200, 200, 200), (100, 300, 400, 20))  # Fond de la barre
        pygame.draw.rect(screen, (0, 200, 0), (100, 300, int(400 * progress), 20))  # Barre de progression

        # Mettre à jour l'affichage
        screen.fill((255, 255, 255))  # Fond blanc
        if training_done:
            text_surface = font.render("Entraînement terminé !", True, (0, 200, 0))
        else:
            dots = (pygame.time.get_ticks() // 500) % 4  # Change tous les 500ms
            text_surface = font.render(f"Entraînement en cours{'.' * dots}", True, (0, 0, 200))
        screen.blit(text_surface, (100, 150))

        # Rafraîchir l'écran
        pygame.display.flip()
        clock.tick(30)  # Limiter à 30 FPS

    # Garder l'écran affiché après la fin de l'entraînement
    thread_entrainement.join()
    pygame.quit()
    sys.exit()
