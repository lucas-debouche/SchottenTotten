from Jeux.Jeu import Jeu
from Jeux.Joueur import Joueur

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

    # Ajoutez ici la boucle principale du jeu (à compléter en fonction des règles)
    # Exemple :
    # while not jeu.est_termine():
    #     jeu.tour_de_jeu()

if __name__ == "__main__":
    main()
