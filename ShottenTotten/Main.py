import Jeu.Carte
import Jeu.Joueur
import Jeu.Plateau
import Jeu.Jeu

print("j'essaye")

choix_mode = int(input("Choisis un mode de jeu :\n1) Classsique\n2) Tactique\n3) Expert\n"))
while (choix_mode < 1) or (choix_mode > 3):
    print("Choisis un mode de jeu valable")
    choix_mode = int(input("Choisis un mode de jeu :\n1) Classsique\n2) Tactique\n3) Expert\n"))

Jeu.Jeu.mode = Jeu.Jeu.Modes[choix_mode]
print(Jeu.Jeu.mode)



