import Plateau
import Carte

Modes = {1 : "Classique", 2 : "Tactique", 3 : "Expert"}

class Mode:
    def __init__(self):
        self.mode = 0

mode = Mode()

def choix_borne():
    choix = int(input("Choisis une borne (1-" + str(len(Plateau.plateau)) + ")\n"))
    while (choix < 1) or (choix > len(Plateau.plateau)):
        print("Choisis une borne valable")
        choix = int(input("Choisis une borne (1-" + str(len(Plateau.plateau)) + ")\n"))
    return choix