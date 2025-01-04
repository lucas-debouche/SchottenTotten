import sys
import pygame

class Popup:
    """Classe représentant une popup interactive utilisée dans le jeu pour effectuer des choix."""

    def __init__(self, screen, screen_width, screen_height, troupe):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Centre de la popup
        self.popup_x = self.screen_width // 2
        self.popup_y = self.screen_height // 2

        if troupe:
            # Initialisation des options de couleur et de force en fonction du type de troupe
            self.couleurs = ["Rouge", "Vert", "Jaune", "Violet", "Bleu", "Orange"]
            if troupe == "joker":
                self.force = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            elif troupe == "espion":
                self.force = ["7"]
            elif troupe == "porte-bouclier":
                self.force = ["1", "2", "3"]
            self.menu1_open = False
            self.menu2_open = False

            # Définition des rectangles pour les menus et options
            self.menu1_rect = {"couleur": pygame.Rect(self.popup_x - 190, self.popup_y - 200, 150, 50)}
            self.menu2_rect = {"force": pygame.Rect(self.popup_x + 40, self.popup_y - 200, 150, 50)}
            self.options1_rects = {
                i: pygame.Rect(
                    self.menu1_rect["couleur"].x,
                    self.menu1_rect["couleur"].y + (i + 1) * self.menu1_rect["couleur"].height,
                    self.menu1_rect["couleur"].width,
                    self.menu1_rect["couleur"].height
                ) for i in range(len(self.couleurs))
            }
            self.options2_rects = {
                i: pygame.Rect(
                    self.menu2_rect["force"].x,
                    self.menu2_rect["force"].y + (i + 1) * self.menu2_rect["force"].height,
                    self.menu2_rect["force"].width,
                    self.menu2_rect["force"].height
                ) for i in range(len(self.force))
            }

        self.choix_couleur = None
        self.choix_force = None
        self.choix_pioche_clan = 0
        self.choix_pioche_tactique = 0

        # Bouton "Valider" et pioches
        self.button_valider = {"valider": pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 240, 150, 50)}
        self.pioche_clan = {"clan": pygame.Rect(self.screen_width // 2 - 190, self.screen_height // 2 - 200, 150, 50)}
        self.pioche_tactique = {"tactique": pygame.Rect(self.screen_width // 2 + 40, self.screen_height // 2 - 200, 150, 50)}

    def show(self, capacite, pioche_clan, pioche_tactique):
        """Affiche la popup à l'écran et gère les interactions avec l'utilisateur."""
        running = True
        self.screen.fill((165, 140, 100))  # Efface l'écran principal
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Gestion des clics sur les éléments de la popup
                    if capacite == "Troupes d'élites":
                        # Ouverture et sélection dans les menus
                        if self.menu1_rect["couleur"].collidepoint(event.pos):
                            self.menu1_open = not self.menu1_open
                        elif self.menu1_open:
                            for i, rect in self.options1_rects.items():
                                if rect.collidepoint(event.pos):
                                    self.choix_couleur = self.couleurs[i]
                                    self.menu1_open = False
                                    self.screen.fill((165, 140, 100))
                        elif self.menu2_rect["force"].collidepoint(event.pos):
                            self.menu2_open = not self.menu2_open
                        elif self.menu2_open:
                            for i, rect in self.options2_rects.items():
                                if rect.collidepoint(event.pos):
                                    self.choix_force = self.force[i]
                                    self.menu2_open = False
                                    self.screen.fill((165, 140, 100))
                        elif self.choix_couleur and self.choix_force:
                            self.afficher_button_valider((205, 200, 145))
                            if self.button_valider["valider"].collidepoint(event.pos):
                                running = False

                    elif capacite == "Ruses":
                        # Gestion des pioches
                        if self.choix_pioche_clan + self.choix_pioche_tactique == 3:
                            if self.button_valider["valider"].collidepoint(event.pos):
                                running = False
                        else:
                            if self.pioche_clan["clan"].collidepoint(event.pos) and len(pioche_clan) - self.choix_pioche_clan > 0:
                                self.choix_pioche_clan += 1
                                self.screen.fill((165, 140, 100))
                            if self.pioche_tactique["tactique"].collidepoint(event.pos) and len(pioche_tactique) - self.choix_pioche_tactique > 0:
                                self.choix_pioche_tactique += 1
                                self.screen.fill((165, 140, 100))

            # Affichage des éléments
            if capacite:
                self.afficher_button_valider((169, 169, 169))
            if capacite == "Troupes d'élites":
                self._afficher_menus()
            elif capacite == "Ruses":
                self._afficher_pioches(pioche_clan, pioche_tactique)

            pygame.display.flip()

        if self.choix_couleur and self.choix_force:
            return self.choix_couleur, self.choix_force
        elif self.choix_pioche_clan + self.choix_pioche_tactique == 3:
            return self.choix_pioche_clan, self.choix_pioche_tactique

    def afficher_button_valider(self, couleur):
        """Affiche le bouton "Valider" sur la popup."""
        smallfont = pygame.font.SysFont('Forte', 35)
        pygame.draw.rect(self.screen, couleur, self.button_valider["valider"], border_radius=10)
        pygame.draw.rect(self.screen, (139, 69, 19), self.button_valider["valider"], width=2, border_radius=10)
        text_jouer = smallfont.render("Valider", True, (139, 69, 19))
        text_rect_jouer = text_jouer.get_rect(center=self.button_valider["valider"].center)
        self.screen.blit(text_jouer, text_rect_jouer)
        pygame.display.update(self.button_valider["valider"])

    def _afficher_menus(self):
        """Affiche les menus déroulants pour les choix de couleur et de force."""
        # Menu couleur
        pygame.draw.rect(self.screen, (205, 200, 145), self.menu1_rect["couleur"])
        pygame.draw.rect(self.screen, (0, 0, 0), self.menu1_rect["couleur"], width=2)
        menu1_text = pygame.font.Font(None, 36).render(
            str(self.choix_couleur) if self.choix_couleur else "Couleur", True, (0, 0, 0))
        self.screen.blit(menu1_text, menu1_text.get_rect(center=self.menu1_rect["couleur"].center))

        # Menu force
        pygame.draw.rect(self.screen, (205, 200, 145), self.menu2_rect["force"])
        pygame.draw.rect(self.screen, (0, 0, 0), self.menu2_rect["force"], width=2)
        menu2_text = pygame.font.Font(None, 36).render(
            str(self.choix_force) if self.choix_force else "Force", True, (0, 0, 0))
        self.screen.blit(menu2_text, menu2_text.get_rect(center=self.menu2_rect["force"].center))

        # Ouverture des menus
        if self.menu1_open:
            menuX_open(self.options1_rects, self.screen, self.couleurs)
        if self.menu2_open:
            menuX_open(self.options2_rects, self.screen, self.force)

    def _afficher_pioches(self, pioche_clan, pioche_tactique):
        """Affiche les boutons de pioche pour les cartes de clan et tactiques."""
        # Pioches clan et tactique
        if len(pioche_clan) - self.choix_pioche_clan > 0:
            pygame.draw.rect(self.screen, (205, 200, 145), self.pioche_clan["clan"], border_radius=10)
            pygame.draw.rect(self.screen, (139, 69, 19), self.pioche_clan["clan"], width=2, border_radius=10)
        text_pioche_clan = pygame.font.Font(None, 36).render(
            f"{self.choix_pioche_clan}/3 Clan", True, (139, 69, 19))
        self.screen.blit(text_pioche_clan, text_pioche_clan.get_rect(center=self.pioche_clan["clan"].center))

        if len(pioche_tactique) - self.choix_pioche_tactique > 0:
            pygame.draw.rect(self.screen, (205, 200, 145), self.pioche_tactique["tactique"], border_radius=10)
            pygame.draw.rect(self.screen, (139, 69, 19), self.pioche_tactique["tactique"], width=2, border_radius=10)
        text_pioche_tactique = pygame.font.Font(None, 36).render(
            f"{self.choix_pioche_tactique}/3 Tactique", True, (139, 69, 19))
        self.screen.blit(text_pioche_tactique, text_pioche_tactique.get_rect(center=self.pioche_tactique["tactique"].center))


def menuX_open(menu_rects, screen, options):
    """Affiche les options du menu déroulant à l'écran."""
    font = pygame.font.Font(None, 36)
    for i, rect in menu_rects.items():
        pygame.draw.rect(screen, (205, 200, 145), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=1)
        text = font.render(str(options[i]), True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
