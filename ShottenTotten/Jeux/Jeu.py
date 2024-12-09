from ShottenTotten.Jeux.Carte import generer_cartes, determiner_combinaison, displayCarte


def comparaison_cartes(self, numero_borne):
    """Compare les cartes des joueurs pour trouver la meilleure combinaison"""
    j1 = determiner_combinaison(self.plateau.bornes[numero_borne].joueur1_cartes)
    j2 = determiner_combinaison(self.plateau.bornes[numero_borne].joueur2_cartes)
    if j1<j2:
        return self.joueurs[0]
    else:
        return self.joueurs[1]


