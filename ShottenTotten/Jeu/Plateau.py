class Plateau:
    def __init__(self, bornes):
        self.bornes = bornes

    def revendiquer(self, numeroborne):
        self.bornes.pop(numeroborne)
        return self.bornes

Plateau = Plateau({1 : [0,0], 2 : [0,0], 3 : [0,0], 4 : [0,0], 5 : [0,0], 6 : [0,0], 7 : [0,0], 8 : [0,0], 9 : [0,0]})