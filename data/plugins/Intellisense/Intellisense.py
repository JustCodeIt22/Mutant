import pygame
from pygame.locals import *

class Intellisense:
    def __init__(self):
        self.dispAutoCompleteWindow = False

    def handle_events(self, event, ctrl):
        if event.key == pygame.K_SPACE and ctrl:
            self.dispAutoCompleteWindow = not self.dispAutoCompleteWindow

    def get_auto_completions(self):
        pass

    def draw(self, surf, cursor_surf_rect):
        if self.dispAutoCompleteWindow:
            pygame.draw.rect(surf, (255, 255, 0), (cursor_surf_rect.bottomright, (100, 100)))


    def update(self):
        pass