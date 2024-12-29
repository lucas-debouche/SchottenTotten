import random
import numpy as np

# --- Q-Learning ---
class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.99):
        """
        Initialise un agent Q-Learning.
        :param actions: Liste des actions possibles.
        :param learning_rate: Taux d'apprentissage (alpha).
        :param discount_factor: Facteur de réduction (gamma).
        :param exploration_rate: Taux d'exploration initial (epsilon).
        :param exploration_decay: Décroissance du taux d'exploration.
        """
        self.q_table = {}  # Table Q sous forme de dictionnaire : {(état, action): valeur Q}
        self.actions = actions  # Liste des actions possibles
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

    def choose_action(self, state):
        """
        Choisit une action en fonction de la politique epsilon-greedy.
        :param state: Représentation de l'état actuel.
        :return: Action choisie.
        """
        if not self.actions:  # Vérifiez si la liste des actions est vide
            raise ValueError("Aucune action valide disponible pour cet état.")

        if random.uniform(0, 1) < self.exploration_rate:
            # Exploration : choisir une action aléatoire
            return random.choice(self.actions)
        else:
            # Exploitation : choisir l'action avec la plus grande valeur Q
            q_values = [self.q_table.get((tuple(state), tuple(action)), 0) for action in self.actions]
            max_q = max(q_values)
            max_actions = [action for action, q in zip(self.actions, q_values) if q == max_q]
            return random.choice(max_actions)  # En cas d'égalité, choisir une action aléatoire parmi les meilleures

    def update_q_value(self, state, action, reward, next_state):
        """
        Met à jour la valeur Q pour un état-action donné.
        :param state: État actuel (doit être un tuple).
        :param action: Action choisie (doit être un tuple).
        :param reward: Récompense reçue.
        :param next_state: État suivant (doit être un tuple).
        """
        state = tuple(state)  # Assurez-vous que l'état est un tuple
        action = tuple(action)  # Assurez-vous que l'action est un tuple

        old_q_value = self.q_table.get((state, action), 0)
        next_q_values = [self.q_table.get((next_state, next_action), 0) for next_action in self.actions]
        max_next_q = max(next_q_values) if next_q_values else 0

        # Calcul de la nouvelle valeur Q
        new_q_value = (1 - self.learning_rate) * old_q_value + self.learning_rate * (
                    reward + self.discount_factor * max_next_q)
        self.q_table[(state, action)] = new_q_value

    def decay_exploration_rate(self):
        """
        Diminue le taux d'exploration (epsilon) pour favoriser l'exploitation à long terme.
        """
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_rate, 0.01)  # Évite que epsilon devienne trop faible

def generate_actions(state):
    """
    Génère toutes les actions possibles pour le joueur actuel.
    Inclut la possibilité de revendiquer une borne si les conditions sont remplies.
    """
    joueur = state.joueur_courant()
    actions = []

    # Actions pour jouer une carte
    for carte in state.main_joueur(joueur):
        for borne in range(1, state.nombre_bornes() + 1):
            if state.peut_jouer_carte(borne, joueur):
                actions.append((carte, borne))  # Action de type (Carte, Borne)

    # Actions pour revendiquer une borne
    for borne in range(1, state.nombre_bornes() + 1):
        if state.peut_revendiquer_borne(borne, joueur, None, 3):
            actions.append(("REVENDIQUER", borne))  # Action de type ("REVENDIQUER", Borne)

    return actions