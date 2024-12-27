import random
import numpy as np

# --- Alpha-Bêta Pruning ---
def alpha_beta_pruning(state, depth, alpha, beta, maximizing_player, evaluate, generate_actions, apply_action):
    if depth == 0 or is_terminal_state(state):
        return None, evaluate(state)

    if maximizing_player:
        max_eval = float('-inf')
        best_action = None
        for action in generate_actions(state):
            new_state = apply_action(state, action)  # Utiliser une copie de l'état
            _, eval_score = alpha_beta_pruning(new_state, depth - 1, alpha, beta, False, evaluate, generate_actions, apply_action)
            if eval_score > max_eval:
                max_eval = eval_score
                best_action = action
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return best_action, max_eval
    else:
        min_eval = float('inf')
        best_action = None
        for action in generate_actions(state):
            new_state = apply_action(state, action)  # Utiliser une copie de l'état
            _, eval_score = alpha_beta_pruning(new_state, depth - 1, alpha, beta, True, evaluate, generate_actions, apply_action)
            if eval_score < min_eval:
                min_eval = eval_score
                best_action = action
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return best_action, min_eval

# --- Q-Learning ---
class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.995):
        """
        Initialisation de l'agent Q-Learning.

        :param actions: Liste des actions possibles.
        :param learning_rate: Taux d'apprentissage alpha.
        :param discount_factor: Facteur de discount gamma.
        :param exploration_rate: Probabilité d'exploration initiale epsilon.
        :param exploration_decay: Décroissance de epsilon.
        """
        self.q_table = {}  # Table Q(s, a) initialement vide
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

    def get_q_value(self, state, action):
        """Retourne la valeur Q(s, a) ou 0 si elle n'existe pas."""
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        """Choisit une action en fonction de l'exploration ou de l'exploitation."""
        if random.random() < self.exploration_rate:
            return random.choice(self.actions)  # Exploration
        else:
            # Exploitation : choisir l'action avec la plus grande valeur Q
            q_values = {action: self.get_q_value(state, action) for action in self.actions}
            return max(q_values, key=q_values.get)

    def update_q_value(self, state, action, reward, next_state):
        """Met à jour la valeur Q(s, a) en utilisant la formule de Q-Learning."""
        max_q_next = max([self.get_q_value(next_state, a) for a in self.actions], default=0.0)
        new_q = (1 - self.learning_rate) * self.get_q_value(state, action) + \
                self.learning_rate * (reward + self.discount_factor * max_q_next)
        self.q_table[(state, action)] = new_q

    def decay_exploration_rate(self):
        """Réduit le taux d'exploration epsilon."""
        self.exploration_rate *= self.exploration_decay

# --- Adaptation pour Schotten Totten ---
def evaluate(state):
    """
    Évalue l'état actuel du plateau pour le joueur max.
    :param state: Instance de la classe Plateau représentant l'état du jeu.
    :return: Score évalué.
    """
    score = 0

    # Points pour les bornes contrôlées
    for borne in range(state.nombre_bornes()):
        gagnant = state.gagnant_borne(borne)
        if gagnant == "max":
            score += 10  # Borne contrôlée par max
        elif gagnant == "min":
            score -= 10  # Borne contrôlée par min

    # Points pour des combinaisons prometteuses
    for borne in range(state.nombre_bornes()):
        max_combinaison = state.score_combinaison("max", borne)
        min_combinaison = state.score_combinaison("min", borne)
        score += max_combinaison - min_combinaison

    return score

def generate_actions(state):
    """
    Génère toutes les actions possibles pour le joueur courant.
    :param state: Instance de la classe Plateau représentant l'état du jeu.
    :return: Liste des actions possibles.
    """
    actions = []
    joueur_courant = state.joueur_courant()
    main = state.main_joueur(joueur_courant)

    for carte in main:
        for borne in range(1, state.nombre_bornes()+1):
            if state.peut_jouer_carte(borne, joueur_courant):
                actions.append((carte, borne))  # (Carte à jouer, Borne cible)

    return actions

def apply_action(state, action):
    """
    Applique une action à une copie de l'état et retourne ce nouvel état.
    """
    carte, borne = action
    nouveau_state = state.clone()  # Crée une copie indépendante de l'état
    joueur = nouveau_state.joueur_actuel
    nouveau_state.appliquer_action_jeu(action, joueur)  # Applique l'action sur la copie
    return nouveau_state


def is_terminal_state(state):
    """
    Vérifie si l'état est terminal.
    """
    if state is None:
        raise ValueError("L'état 'state' est None. Vérifiez l'initialisation du plateau.")

    # Toutes les bornes sont revendiquées
    if all(state.gagnant_borne(borne) is not None for borne in range(1, state.nombre_bornes() + 1)):
        return True

    # Vérifier si un joueur a atteint les bornes nécessaires pour gagner
    bornes_max = sum(1 for borne in range(1, state.nombre_bornes() + 1) if state.gagnant_borne(borne) == "max")
    bornes_min = sum(1 for borne in range(1, state.nombre_bornes() + 1) if state.gagnant_borne(borne) == "min")
    return bornes_max >= state.bornes_a_gagner() or bornes_min >= state.bornes_a_gagner()
