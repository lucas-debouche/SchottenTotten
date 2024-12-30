import random
from ShottenTotten.Jeux.Carte import CarteClan

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
        Choisit une action en utilisant epsilon-greedy pour équilibrer exploration et exploitation.
        :param state: Instance de Plateau.
        :return: Action choisie.
        """
        if not self.actions:
            print("Aucune action valide disponible pour cet état.")
            return None  # Retourner None si aucune action n'est disponible

        # Exploration : choisir une action aléatoire avec probabilité epsilon
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)

        # Exploitation : évaluer les actions
        score = 0
        best_action = None
        best_score = float('-inf')

        for action in self.actions:
            # Si c'est une action de revendication
            if isinstance(action[0], str) and action[0] == "REVENDIQUER":
                borne = action[1]
                if state.peut_revendiquer_borne(borne, state.joueur_courant()):
                    score = 15  # Récompense élevée pour revendiquer une borne
                else:
                    score = -5  # Pénalité pour tentative inutile

            elif isinstance(action[0], CarteClan):
                carte, borne = action
                score = state.evaluer_action_globale(carte, borne, state.joueur_courant())
            if score > best_score:
                best_score = score
                best_action = action

        # Si aucune action optimale n'a été trouvée (par exemple, si scores égaux), choisir au hasard
        return best_action if best_action else random.choice(self.actions)

    def update_q_value(self, state, action, reward, next_state):
        """
        Met à jour la valeur Q pour un état-action donné.
        :param state: État actuel (doit être un tuple).
        :param action: Action choisie (doit être un tuple).
        :param reward: Récompense reçue.
        :param next_state: État suivant (doit être un tuple).
        """
        state = state.to_state_representation()
        next_state = next_state.to_state_representation()

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
    Prend en compte la stratégie des revendications.
    """
    joueur = state.joueur_courant()
    actions = []

    # Actions pour jouer une carte
    for carte in state.main_joueur(joueur):
        for borne in range(1, state.nombre_bornes() + 1):
            if state.peut_jouer_carte(borne, joueur):
                actions.append((carte, borne))  # Action pour jouer une carte

    # Actions pour revendiquer une borne
    for borne in range(1, state.nombre_bornes() + 1):
        if state.peut_revendiquer_borne(borne, joueur):
            actions.append(("REVENDIQUER", borne))

    # Prioriser les revendications de bornes critiques
    actions.sort(key=lambda action: state.evaluer_etat_global(joueur) if action[0] == "REVENDIQUER" else 0, reverse=True)

    return actions
