from Jeux.Jeu import Jeu
from ShottenTotten.Jeux.Carte import generer_cartes
from Jeux.Joueur import Joueur
from ShottenTotten.Jeux.Jeu import melanger_pioche


def main():
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
    print(f"Joueurs : {[jeu.joueurs[joueur].nom for joueur in range(len(jeu.joueurs))]}")

    cartes_clans, carte_tactiques = generer_cartes()
    if jeu.mode == 1:
        carte_tactiques = []

    jeu.pioche = melanger_pioche(cartes_clans, carte_tactiques)

if __name__ == "__main__":
    main()
