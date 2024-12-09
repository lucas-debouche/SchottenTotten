from Jeux.Jeu import Jeu
from ShottenTotten.Jeux.Carte import generer_cartes
from Jeux.Menu import Menu
from ShottenTotten.Jeux.Plateau import Plateau, melanger_pioche


def main():
    # Initialisation du jeu
    menu = Menu()
    menu.displayAcceuil()
    jeu = Jeu()
    jeu.initialiser_cartes()
    jeu.configurer_joueurs()


    print("\nJeu prêt à commencer !")
    print(f"Mode choisi : {menu.mode}")
    print(f"Manches jouées : {menu.nbr_manche}")
    print(f"Joueurs : {[jeu.joueurs[joueur].nom for joueur in range(len(jeu.joueurs))]}")


if __name__ == "__main__":
    main()
