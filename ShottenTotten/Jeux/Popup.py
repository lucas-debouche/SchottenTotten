import sys
import pygame

class Popup:
    def __init__(self, screen, screen_width, screen_height, troupe):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Centre la popup
        self.popup_x = self.screen_width // 2
        self.popup_y = self.screen_height // 2

        if troupe:
            self.couleurs = ["Rouge", "Vert", "Jaune", "Violet", "Bleu", "Orange"]
            if troupe == "joker":
                self.force = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            elif troupe == "espion":
                self.force = ["7"]
            elif troupe == "porte-bouclier":
                self.force = ["1", "2", "3"]
            self.menu1_open = False
            self.menu2_open = False



            # Boutons et menus relatifs à la popup
            self.menu1_rect = {"couleur": pygame.Rect(self.popup_x - 190, self.popup_y - 200, 150, 50)}
            self.menu2_rect = {"force": pygame.Rect(self.popup_x + 40, self.popup_y - 200, 150, 50)}

            self.options1_rects = {i: pygame.Rect(self.menu1_rect["couleur"].x,
                                                  self.menu1_rect["couleur"].y + (i + 1) * self.menu1_rect[
                                                      "couleur"].height,
                                                  self.menu1_rect["couleur"].width, self.menu1_rect["couleur"].height) for i
                                   in range(len(self.couleurs))}

            self.options2_rects = {i: pygame.Rect(self.menu2_rect["force"].x,
                                                  self.menu2_rect["force"].y + (i + 1) * self.menu2_rect["force"].height,
                                                  self.menu2_rect["force"].width, self.menu2_rect["force"].height) for i in
                                   range(len(self.force))}

        self.choix_couleur = None
        self.choix_force = None
        self.choix_pioche_clan = 0
        self.choix_pioche_tactique = 0

        self.button_valider = {"valider": pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 240, 150, 50)}
        self.pioche_clan = {"clan": pygame.Rect(self.screen_width // 2 - 190, self.screen_height // 2 - 200, 150, 50)}
        self.pioche_tactique = {"tactique": pygame.Rect(self.screen_width // 2 + 40, self.screen_height // 2 - 200, 150, 50)}

    def show(self, capacite, pioche_clan, pioche_tactique):
        running = True
        self.screen.fill((165, 140, 100))  # Efface l'écran principal
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Vérifie si le bouton "Valider" est cliqué
                    if capacite == "Troupes d'élites":
                        if self.menu1_rect["couleur"].collidepoint(event.pos):
                            self.menu1_open = not self.menu1_open
                        elif self.menu1_open:
                            for i, rect in self.options1_rects.items():
                                if rect.collidepoint(event.pos):
                                    self.choix_couleur = self.couleurs[i]
                                    self.menu1_open = False  # Fermer le menu des couleurs
                                    self.screen.fill((165, 140, 100))
                        elif self.menu2_rect["force"].collidepoint(event.pos):
                            self.menu2_open = not self.menu2_open
                        elif self.menu2_open:
                            for i, rect in self.options2_rects.items():
                                if rect.collidepoint(event.pos):
                                    self.choix_force = self.force[i]
                                    self.menu2_open = False  # Fermer le menu de force
                                    self.screen.fill((165, 140, 100))
                        elif self.button_valider["valider"].collidepoint(
                                event.pos) and self.choix_couleur and self.choix_force:
                            running = False

                    elif capacite == "Ruses":
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

            if capacite:
                # Dessin du bouton Valider
                smallfont = pygame.font.SysFont('Forte', 35)
                pygame.draw.rect(self.screen, (169, 169, 169), self.button_valider["valider"], border_radius=10)
                pygame.draw.rect(self.screen, (139, 69, 19), self.button_valider["valider"], width=2, border_radius=10)
                text_jouer = smallfont.render("Valider", True, (139, 69, 19))
                text_rect_jouer = text_jouer.get_rect(center=self.button_valider["valider"].center)
                self.screen.blit(text_jouer, text_rect_jouer)
                pygame.display.update(self.button_valider["valider"])
            if capacite == "Troupes d'élites":
                # Affiche les menus
                pygame.draw.rect(self.screen, (205, 200, 145), self.menu1_rect["couleur"])
                pygame.draw.rect(self.screen, (0, 0, 0), self.menu1_rect["couleur"], width=2)
                menu1_text = pygame.font.Font(None, 36).render(
                    str(self.choix_couleur) if self.choix_couleur else "Couleur", True, (0, 0, 0))
                self.screen.blit(menu1_text, menu1_text.get_rect(center=self.menu1_rect["couleur"].center))

                pygame.draw.rect(self.screen, (205, 200, 145), self.menu2_rect["force"])
                pygame.draw.rect(self.screen, (0, 0, 0), self.menu2_rect["force"], width=2)
                menu2_text = pygame.font.Font(None, 36).render(str(self.choix_force) if self.choix_force else "Force",
                                                               True, (0, 0, 0))
                self.screen.blit(menu2_text, menu2_text.get_rect(center=self.menu2_rect["force"].center))

                if self.menu1_open:
                    menuX_open(self.options1_rects, self.screen, self.couleurs)
                if self.menu2_open:
                    menuX_open(self.options2_rects, self.screen, self.force)

            elif capacite == "Ruses":
                if len(pioche_clan) - self.choix_pioche_clan > 0:
                    pygame.draw.rect(self.screen, (205, 200, 145), self.pioche_clan["clan"])
                else:
                    pygame.draw.rect(self.screen, (120, 120, 120), self.pioche_clan["clan"])
                pygame.draw.rect(self.screen, (0, 0, 0), self.pioche_clan["clan"], width=2)
                clan_text = pygame.font.Font(None, 36).render("Clan", True, (0, 0, 0))
                self.screen.blit(clan_text, clan_text.get_rect(center=self.pioche_clan["clan"].center))

                if len(pioche_tactique) - self.choix_pioche_tactique > 0:
                    pygame.draw.rect(self.screen, (205, 200, 145), self.pioche_tactique["tactique"])
                else:
                    pygame.draw.rect(self.screen, (120, 120, 120), self.pioche_tactique["tactique"])
                pygame.draw.rect(self.screen, (0, 0, 0), self.pioche_tactique["tactique"], width=2)
                tactique_text = pygame.font.Font(None, 36).render("Tactique", True, (0, 0, 0))
                self.screen.blit(tactique_text, tactique_text.get_rect(center=self.pioche_tactique["tactique"].center))

                # Affichage des compteurs de clics sous les boutons
                clan_count_text = pygame.font.Font(None, 36).render(f"Clics: {self.choix_pioche_clan}", True, (0, 0, 0))
                self.screen.blit(clan_count_text, (self.pioche_clan["clan"].x + 30, self.pioche_clan["clan"].y + 60))

                tactique_count_text = pygame.font.Font(None, 36).render(f"Clics: {self.choix_pioche_tactique}", True,(0, 0, 0))
                self.screen.blit(tactique_count_text,(self.pioche_tactique["tactique"].x + 30, self.pioche_tactique["tactique"].y + 60))

            pygame.display.flip()

        if self.choix_couleur and self.choix_force:
            return self.choix_couleur, self.choix_force
        elif self.choix_pioche_clan + self.choix_pioche_tactique == 3:
            return self.choix_pioche_clan, self.choix_pioche_tactique


def menuX_open(options_rects, screen, options):
    for i, rect in options_rects.items():
        pygame.draw.rect(screen, (205, 200, 145), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2)  # Bordure noire
        text_surface = pygame.font.Font(None, 36).render(options[i], True, (0, 0, 0))
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))
