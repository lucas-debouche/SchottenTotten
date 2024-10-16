import Carte
import Jeu
import Plateau

class Joueur:
    def __init__(self, nom, main, score):
        self.nom = nom
        self.main = main
        self.score = score

    def score(self):
        self.score += 1
        return self.score

    def jouer(self):
        if Jeu.mode == 1:
            nombrecartemax = 6
        else:
            nombrecartemax = 7

        choix_carte = int(input("Choisis une carte à jouer (1-" + str(nombrecartemax) + ")\n"))
        while (choix_carte < 1) or (choix_carte > nombrecartemax):
            print("Choisis une carte valable")
            choix_carte = int(input("Choisis une carte à jouer (1-" + str(nombrecartemax) + ")\n"))
        carte = self.main[choix_carte - 1]

        if carte.capacite == Carte.Capacites[1]:
            choix_borne = Jeu.choix_borne()
            Plateau.plateau.bornes[choix_borne - 1][0].append(carte)
            self.main.pop(choix_carte - 1)
        elif carte.capacite == Carte.Capacites[2]:
            choix_borne = Jeu.choix_borne()
            Plateau.plateau.bornes[choix_borne - 1][1].append(carte)
            self.main.pop(choix_carte - 1)
        elif carte.capacite == Carte.Capacites[3]:
            Plateau.plateau.defausse.append(carte)
            self.main.pop(choix_carte - 1)
        else:
            choix_borne = Jeu.choix_borne()
            Plateau.plateau.bornes[choix_borne - 1][0].append(carte)
            self.main.pop(choix_carte - 1)


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

    def regarder_defausse(self):
        ""
