import sys
import pygame

class Popup:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.couleurs = ["Rouge", "Vert", "Jaune", "Violet", "Bleu", "Orange"]
        self.force = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.menu1_open = False
        self.menu2_open = False

        # Centre la popup
        self.popup_x = self.screen_width // 2
        self.popup_y = self.screen_height // 2

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
        self.button_valider = {"valider": pygame.Rect(self.popup_x - 75, self.popup_y + 240, 150, 50)}

    def show(self):
        valider = False
        while not valider:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Vérifie si le bouton "Valider" est cliqué
                    if self.button_valider["valider"].collidepoint(
                            event.pos) and self.choix_couleur and self.choix_force:
                        valider = True
                        # Gestion des menus déroulants
                    elif self.menu1_rect["couleur"].collidepoint(event.pos):
                        self.menu1_open = not self.menu1_open
                    elif self.menu1_open:
                        for i, rect in self.options1_rects.items():
                            if rect.collidepoint(event.pos):
                                self.choix_couleur = self.couleurs[i]
                                self.menu1_open = False
                    elif self.menu2_rect["force"].collidepoint(event.pos):
                        self.menu2_open = not self.menu2_open
                    elif self.menu2_open:
                        for i, rect in self.options2_rects.items():
                            if rect.collidepoint(event.pos):
                                self.choix_force = self.force[i]
                                self.menu2_open = False

            # Affichage
            self.screen.fill((165, 140, 100))  # Efface l'écran principal

            # Affiche les menus
            pygame.draw.rect(self.screen, (205, 200, 145), self.menu1_rect["couleur"])  # Fond clair
            pygame.draw.rect(self.screen, (0, 0, 0), self.menu1_rect["couleur"], width=2)  # Bordure noire
            menu1_text = pygame.font.Font(None, 36).render(str(self.choix_couleur) if self.choix_couleur else "Couleur",
                                                           True, (0, 0, 0))
            self.screen.blit(menu1_text, menu1_text.get_rect(center=self.menu1_rect["couleur"].center))

            pygame.draw.rect(self.screen, (205, 200, 145), self.menu2_rect["force"])  # Fond clair
            pygame.draw.rect(self.screen, (0, 0, 0), self.menu2_rect["force"], width=2)  # Bordure noire
            menu2_text = pygame.font.Font(None, 36).render(str(self.choix_force) if self.choix_force else "Force", True,
                                                           (0, 0, 0))
            self.screen.blit(menu2_text, menu2_text.get_rect(center=self.menu2_rect["force"].center))

            # Bouton Valider
            pygame.draw.rect(self.screen, (205, 200, 145), self.button_valider["valider"])  # Fond clair
            pygame.draw.rect(self.screen, (0, 0, 0), self.button_valider["valider"], width=2)  # Bordure noire
            text_surface = pygame.font.Font(None, 36).render("Valider", True, (0, 0, 0))
            self.screen.blit(text_surface, text_surface.get_rect(center=self.button_valider["valider"].center))

            if self.menu1_open:
                menuX_open(self.options1_rects, self.screen, self.couleurs, None)
            if self.menu2_open:
                menuX_open(self.options2_rects, self.screen, self.force, None)

            pygame.display.flip()

        return self.choix_couleur, self.choix_force

def menuX_open(options_rects, screen, options, selected_index):
    for i, rect in options_rects.items():
        pygame.draw.rect(screen, (205, 200, 145), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2)  # Bordure noire
        text_surface = pygame.font.Font(None, 36).render(options[i], True, (0, 0, 0))
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))
