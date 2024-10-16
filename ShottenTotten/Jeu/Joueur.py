import Carte
import Jeu

class Joueur:
    def __init__(self, nom, main, score):
        self.nom = nom
        self.main = main
        self.score = score

    def score(self):
        self.score += 1
        return self.score

    def jouer(self):
        ""

    def piocher(self):
        if Jeu.mode == 1:
            nombrecartemax = 6
        else:
            nombrecartemax = 7

        if len(self.main)<nombrecartemax:
            carte = Carte.Pioche[0]
            Carte.Pioche.pop(0)
            self.main.append(carte)
            return self.main, Carte.Pioche
