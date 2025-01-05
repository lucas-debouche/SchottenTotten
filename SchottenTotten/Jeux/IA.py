import json
import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from SchottenTotten.Jeux.Carte import *

# Définir le chemin du dossier
SAVE_DIR = '../SAVE_DIR'  # Nom du dossier où tout sera sauvegardé

# Créer le dossier s'il n'existe pas
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- Réseau de neurones pour approximer Q(s, a) ---
class QNetwork(nn.Module):
    """Réseau de neurones pour approximer la fonction Q(s, a)."""
    def __init__(self, input_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        """Passe avant dans le réseau."""
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class NeuralQLearningAgent:
    """Agent de Q-learning basé sur un réseau neuronal pour approximer Q(s, a)."""
    def __init__(self, input_size, action_size, mode, learning_rate=0.001, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.99, batch_size = 64):
        self.input_size = input_size
        self.action_size = action_size
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.batch_size = batch_size

        # Initialisation du réseau et de l'optimiseur
        self.q_network = QNetwork(input_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()

        # Mémoire de rejouabilité
        self.memory = deque(load_experiences_from_file(mode), maxlen=10000)

        # Statistiques
        self.total_rewards = []

        self.action_counter = 0

        load_model_weights(self.q_network, mode)

    def choose_action(self, state, possible_actions):
        """Choisit une action en utilisant epsilon-greedy."""
        if any(isinstance(action, CarteTactique) for action in possible_actions):
            tactical_actions = [action for action in possible_actions if isinstance(action, CarteTactique)]
            return random.choice(tactical_actions)

        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(possible_actions)

        # Convertir l'état en tenseur
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)

        # Filtrer les actions possibles
        q_values_filtered = [q_values[0, action].item() for action in possible_actions]
        return possible_actions[q_values_filtered.index(max(q_values_filtered))]

    def decay_exploration_rate(self):
        """Réduit le taux d'exploration pour privilégier l'exploitation."""
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_rate * 0.99, 0.01)

    def store_experience(self, state, action, reward, next_state, possible_next_actions, done):
        """Stocke une expérience dans la mémoire de rejouabilité."""
        self.memory.append((state, action, reward, next_state, possible_next_actions, done))

    def replay(self):
        """Réalise un apprentissage par lot en utilisant des expériences de la mémoire."""
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, possible_next_actions, dones = zip(*batch)

        states_tensor = torch.tensor(np.array(states), dtype=torch.float32)
        actions_tensor = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1)
        next_states_tensor = torch.tensor(np.array(next_states), dtype=torch.float32)
        dones_tensor = torch.tensor(dones, dtype=torch.float32).unsqueeze(1)

        # Calcul des cibles Q
        q_values = self.q_network(states_tensor).gather(1, actions_tensor)
        next_q_values = self.q_network(next_states_tensor)

        max_next_q_values = torch.tensor([
            max(next_q_values[i, possible_actions].tolist()) if len(possible_actions) > 0 else 0
            for i, possible_actions in enumerate(possible_next_actions)
        ], dtype=torch.float32).unsqueeze(1)

        targets = rewards_tensor + (1 - dones_tensor) * self.discount_factor * max_next_q_values

        # Mise à jour du réseau neuronal
        loss = self.criterion(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def log_performance(self, reward, mode):
        """Enregistre la récompense obtenue à la fin d'une partie pour analyse."""
        self.total_rewards.append(reward)
        save_model_weights(self.q_network, mode)


    def train_on_experience(self, state, action, reward, next_state, possible_next_actions, done, mode):
        """Entraîne directement sur une expérience donnée."""
        # Ajout de l'expérience à la mémoire
        self.store_experience(state, action, reward, next_state, possible_next_actions, done)
        save_experiences_to_file(self.memory, mode)

        # Mise à jour immédiate du réseau neuronal
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
        action_tensor = torch.tensor([action], dtype=torch.int64)

        # Prédiction de Q(s, a)
        q_values = self.q_network(state_tensor)
        q_value = q_values[0, action_tensor]

        # Calcul de la cible pour Q(s, a)
        with torch.no_grad():
            next_q_values = self.q_network(next_state_tensor)
            max_next_q = max(
                [next_q_values[0, a].item() for a in possible_next_actions]) if possible_next_actions else 0
            target = reward + self.discount_factor * max_next_q

        # Calcul de la perte et rétropropagation
        loss = self.criterion(q_value, torch.tensor([target], dtype=torch.float32))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Entraînement par lot si nécessaire
        self.action_counter += 1
        if self.action_counter % 10 == 0:  # Exécuter `replay` toutes les 10 actions
            self.replay()

class CustomJSONEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour sérialiser des objets spécifiques."""
    def default(self, obj):
        """Sérialisation des objets spécifiques."""
        if isinstance(obj, CarteClan):
            return obj.to_dict()  # Utiliser to_dict() pour CarteClan
        elif isinstance(obj, CarteTactique):
            return obj.to_dict()
        # Ajoute d'autres classes personnalisées ici si nécessaire
        return super().default(obj)

# Exemple d'intégration dans le jeu
def convert_plateau_to_vector(state):
    """Convertit l'état du plateau en vecteur pour l'entrée du réseau."""
    vector = []
    for borne in state.bornes.values():
        vector.extend([
            len(borne.joueur1_cartes),  # Nombre de cartes joueur 1
            len(borne.joueur2_cartes),  # Nombre de cartes joueur 2
            1 if borne.controle_par == 0 else 0,
            1 if borne.controle_par == 1 else 0
        ])
    return vector

def save_experiences_to_file(memory, mode, max_per_file=1000):
    """Sauvegarde les expériences dans plusieurs fichiers JSON."""
    if not isinstance(memory, list):  # Si `memory` n'est pas une liste, le convertir
        memory = list(memory)
    if mode == "classic":
        filename = 'experiences_classic.json'
    elif mode == "tactic":
        filename = 'experiences_tactic.json'
    else:
        filename = 'experiences_expert.json'
    # Diviser les expériences en groupes de max_per_file
    for i in range(0, len(memory), max_per_file):
        chunk = memory[i:i + max_per_file]
        chunk_filename = f"{os.path.splitext(filename)[0]}_part{i // max_per_file + 1}.json"
        filepath = os.path.join(SAVE_DIR, chunk_filename)
        # Préparer les données pour le fichier JSON
        experiences = [
            {
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'possible_next_action': possible_next_action,
                'done': done
            }
            for state, action, reward, next_state, possible_next_action, done in chunk
        ]
        # Sauvegarder les données dans le fichier
        with open(filepath, 'w') as file:
            json.dump(experiences, file, cls=CustomJSONEncoder, indent=4)

def load_experiences_from_file(mode, directory=SAVE_DIR):
    """Charge toutes les expériences sauvegardées depuis plusieurs fichiers JSON."""
    experiences = []
    if mode == "classic":
        filename_prefix = 'experiences_classic'
    elif mode == "tactic":
        filename_prefix = 'experiences_tactic'
    else:
        filename_prefix = 'experiences_expert'
    # Parcourir tous les fichiers correspondant au préfixe dans le répertoire
    for file in os.listdir(directory):
        if file.startswith(filename_prefix) and file.endswith('.json'):
            filepath = os.path.join(directory, file)
            try:
                # Charger le contenu JSON du fichier
                with open(filepath, 'r') as f:
                    file_experiences = json.load(f)

                # Convertir les expériences en format compatible
                experiences.extend([
                    (
                        CarteClan(**experience['state']) if isinstance(experience['state'], dict) and 'force' in experience['state'] else CarteTactique(**experience['state']) if isinstance(experience['state'], dict) and 'capacite' in experience['state'] else experience['state'],
                        experience['action'],
                        experience['reward'],
                        CarteClan(**experience['next_state']) if isinstance(experience['next_state'], dict) and 'force' in experience['next_state'] else experience['next_state'],
                        experience['possible_next_action'],
                        experience['done']
                    )
                    for experience in file_experiences
                ])
                print(f"Fichier chargé : {filepath} ({len(file_experiences)} expériences)")

            except json.JSONDecodeError as e:
                print(f"Erreur de décodage JSON dans le fichier {filepath}: {e}")
            except FileNotFoundError:
                print(f"Fichier non trouvé : {filepath}")

    return experiences


def save_model_weights(model, mode):
    """Sauvegarde les poids du modèle dans un fichier."""
    if mode == "classic":
        filename = 'q_network_weights_classic.pth'
    elif mode == "tactic":
        filename = 'q_network_weights_tactic.pth'
    else:
        filename = 'q_network_weights_expert.pth'
    filepath = os.path.join(SAVE_DIR, filename)  # Chemin complet
    torch.save(model.state_dict(), filepath)


def load_model_weights(model, mode):
    """Charge les poids du modèle à partir d'un fichier."""
    if mode == "classic":
        filename = 'q_network_weights_classic.pth'
    elif mode == "tactic":
        filename = 'q_network_weights_tactic.pth'
    else:
        filename = 'q_network_weights_expert.pth'
    filepath = os.path.join(SAVE_DIR, filename)  # Chemin complet
    try:
        model.load_state_dict(torch.load(filepath))
    except FileNotFoundError:
        print("Pas de fichier de poids trouvé. Réinitialisation du modèle.")

