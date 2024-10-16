Couleurs = {1 : "Bleu", 2 : "Vert", 3 : "Jaune", 4 : "Marron", 5 : "Rouge", 6 : "Violet"}
Capacites = {1 : "Troupes d'élites", 2 : "Modes de combat", 3 : "Ruses"}
NomsCartesTactiques = {1 : "Joker", 2 : "Espion", 3 : "Porte-Bouclier",
                       4 : "Colin-Maillard", 5 : "Combat de Boue", 6 : "Chasseur de Tête",
                       7 : "Stratège", 8 : "Banshee", 9 : "Traître"}

class CarteClan:
    def __init__(self, couleur, force):
        self.couleur = couleur
        self.force = force

class CarteTactique:
    def __init__(self, capacite, nom):
        self.capacite = capacite
        self.nom = nom

CartesClans = []
CartesTactiques = []

for i in Couleurs:
    for j in range (1,10):
        carte = CarteClan(Couleurs[i], j)
        CartesClans.append(carte)

for i in range(len(CartesClans)):
    print(CartesClans[i].couleur, CartesClans[i].force)

Joker = CarteTactique(Capacites[1], NomsCartesTactiques[1])
Espion = CarteTactique(Capacites[1], NomsCartesTactiques[2])
PorteBouclier = CarteTactique(Capacites[1], NomsCartesTactiques[3])
ColinMaillard = CarteTactique(Capacites[2], NomsCartesTactiques[4])
CombatDeBoue = CarteTactique(Capacites[2], NomsCartesTactiques[5])
ChasseurDeTete = CarteTactique(Capacites[3], NomsCartesTactiques[6])
Stratege = CarteTactique(Capacites[3], NomsCartesTactiques[7])
Banshee = CarteTactique(Capacites[3], NomsCartesTactiques[8])
Traitre = CarteTactique(Capacites[3], NomsCartesTactiques[9])
CartesTactiques.append(Joker)
CartesTactiques.append(Joker)
CartesTactiques.append(Espion)
CartesTactiques.append(PorteBouclier)
CartesTactiques.append(ColinMaillard)
CartesTactiques.append(CombatDeBoue)
CartesTactiques.append(ChasseurDeTete)
CartesTactiques.append(Stratege)
CartesTactiques.append(Banshee)
CartesTactiques.append(Traitre)


for i in range(len(CartesTactiques)):
    print(CartesTactiques[i].capacite, CartesTactiques[i].nom)