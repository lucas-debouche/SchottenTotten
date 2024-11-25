from Jeux.Jeu import Jeu
from Jeux.Carte import generer_cartes
from Jeux.Jeu import melanger_pioche


def main():
    """Point d'entrée principal du programme."""

    # Initialisation du jeu
    jeu = Jeu()
    jeu.initialiser_cartes()
    jeu.choisir_mode()
    jeu.nombre_manches()
    jeu.nombre_joueurs()
    jeu.configurer_joueurs()

    print("\nJeu prêt à commencer !")
    print(f"Mode choisi : {jeu.mode}")
    print(f"Manches jouées : {jeu.nbr_manche}")
    print(f"Joueurs : {[joueur.nom for joueur in jeu.joueurs]}")

    cartes_clans, cartes_tactiques = generer_cartes()
    if jeu.mode == 1:  # Mode classique
        cartes_tactiques = []

    jeu.pioche = melanger_pioche(cartes_clans, cartes_tactiques)
    jeu.tour_de_jeu()


if __name__ == "__main__":
    main()
