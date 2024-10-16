class Plateau:
    def __init__(self, bornes):
        self.bornes = bornes
        self.defausse = []

    def revendiquer(self, numeroborne):
        self.bornes.pop(numeroborne)
        return self.bornes

#initialisation du plateau composé de 9 bornes, chaque borne contient une liste pour chaque joueur et une liste pour la carte tactique
plateau = Plateau({1 : [[],[],[]], 2 : [[],[],[]], 3 : [[],[],[]], 4 : [[],[],[]], 5 : [[],[],[]], 6 : [[],[],[]], 7 : [[],[],[]], 8 : [[],[],[]], 9 : [[],[],[]]})