import pygame
from pygame.locals import *
import json

class IntelliSense:
        
    # ================================== Auto Completetions =============== #
    class AutoCompleter:
        def __init__(self, options):
            self.options = options
            self.matches = [""]
        
        def complete(self, word, state):
            if word:
                self.matches = [option for option in self.options if option and option.startswith(word)]
            
            return self.matches

    # Consturctor
    def __init__(self):
        self.dispAutoCompleteWindow = False
        self.autoCompletRect = pygame.Rect((0, 0, 0, 0))
        # self.font = pygame.font.Font("data/fonts/robot_mono.ttf", 14)
        self.font = pygame.font.SysFont("Consolas", 16)
        self.font_size = self.font.size("a")
        self.bg_color = (19, 37, 69)
        self.fg_color = (255, 255, 255)
        self.padding = 5
        self.keywords = []
        with open("data/plugins/IntelliSense/dataset.json", "r") as file:
            self.keywords = json.load(file)
        self.suggestions = []
        self.autoCompleter = self.AutoCompleter(self.keywords["py_server"])



    def handle_events(self, event, ctrl):
        if event.key == pygame.K_SPACE and ctrl:
            self.dispAutoCompleteWindow = not self.dispAutoCompleteWindow
            return True # just for not adding character
        elif event.key == pygame.K_SPACE:
            self.suggestions = []
            self.curr_word = ""



    def get_auto_completions(self, text, curr_line):
        self.text = text
        if self.text[curr_line] and self.text[curr_line][-1] != " ":
            self.curr_word = self.text[curr_line].split()[-1]
            if self.curr_word:
                self.suggestions = self.autoCompleter.complete(self.curr_word, 0)
            # if self.suggestions: # for debug
            #     print(self.suggestions)
            
                    

    def display_auto_completions(self, surf, cursor_surf_rect):
        for i, suggestion in enumerate(self.suggestions):
            suggestion_txt = self.font.render(suggestion, 1, self.fg_color)
            posx = cursor_surf_rect[0] + self.padding
            posy = cursor_surf_rect[1] + self.padding
            surf.blit(suggestion_txt, (posx, (self.font_size[1] * i) + posy))



    def draw(self, surf, cursor_surf_rect_pos, text, curr_line):
        if self.dispAutoCompleteWindow:
            try:
                # calculating width according to the max element of the suggestions
                self.autoCompletRect.w = len(max(self.suggestions, key=len)) * self.font_size[0] + (self.padding * 2)
            except ValueError:
                self.autoCompletRect.w = 0
            # calculating height according to the length of suggestions
            self.autoCompletRect.h = (self.font_size[1] ) * len(self.suggestions) + self.padding * 2
            # positioning accordingn to the cursor pos
            self.autoCompletRect.topleft = cursor_surf_rect_pos
            pygame.draw.rect(surf, self.bg_color, self.autoCompletRect)
            pygame.draw.rect(surf, (255, 255, 255), self.autoCompletRect, 1)
            self.get_auto_completions(text, curr_line)
            self.display_auto_completions(surf, cursor_surf_rect_pos)


    def update(self):
        pass



