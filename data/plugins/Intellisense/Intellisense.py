import pygame
from pygame.locals import *
import json

class IntelliSense:
        
    # ================================== Auto Completetions =============== #
    class AutoCompleter:
        def __init__(self, options):
            self.options = options
            self.matches = [""]
        
        def complete(self, word):
            if word:
                self.matches = [option for option in self.options if option and option.startswith(word)]
            return self.matches

    # Consturctor
    def __init__(self):
        self.dispAutoCompleteWindow = False
        self.autoCompletRect = pygame.Rect((0, 0, 0, 0))
        # self.font = pygame.font.Font("data/fonts/robot_mono.ttf", 14)
        self.font = pygame.font.SysFont("Consolas", 24)
        self.font_size = self.font.size("a")
        self.bg_color = (19, 37, 69)
        self.fg_color = (255, 255, 255)
        self.padding = 5
        self.keywords = []
        with open("data/plugins/IntelliSense/dataset.json", "r") as file:
            self.keywords = json.load(file)
        self.suggestions = []
        self.autoCompleter = self.AutoCompleter(self.keywords["py_server"])
        self.active_idx = 0
        self.active_word = ""
        self.active_word_color = (255, 46, 102)



    def handle_events(self, event, ctrl):
        if event.key == pygame.K_SPACE and ctrl:
            self.dispAutoCompleteWindow = not self.dispAutoCompleteWindow
            return True # just for not adding character
        elif event.key == pygame.K_SPACE:
            self.suggestions = []
            self.curr_word = ""
    

    def complete(self):
        self.active_word = self.suggestions[self.active_idx]
        return self.active_word

    # Selecting the active word
    def update_active_index(self, direction):
        # For DownWards
        if direction == 1:
            if self.active_idx < len(self.suggestions) - 1:
                self.active_idx += 1
            else:
                self.active_idx = 0
        # For UpWards
        elif direction == -1:
            if self.active_idx > 0:
                self.active_idx -= 1
            else:
                self.active_idx = len(self.suggestions) - 1
    
    
    def haveSuggestions(self):
        return len(self.suggestions) != 0


    def get_auto_completions(self, text, curr_line):
        self.text = text
        if self.text[curr_line] and self.text[curr_line][-1] != " ":
            self.curr_word = self.text[curr_line].split()[-1]
            if self.curr_word:
                self.suggestions = self.autoCompleter.complete(self.curr_word)
            # if self.suggestions: # for debug
            #     print(self.suggestions)
            
                    

    def display_auto_completions(self, surf, cursor_surf_rect):
        posx = cursor_surf_rect[0] + self.padding
        posy = cursor_surf_rect[1] + self.padding
        # Active word
        pygame.draw.rect(surf, self.active_word_color, ((posx, posy + (self.font_size[1] * self.active_idx)), (self.autoCompletRect.w - self.padding * 2, self.font_size[1])))
        for i, suggestion in enumerate(self.suggestions):
            suggestion_txt = self.font.render(suggestion, 1, self.fg_color)
            surf.blit(suggestion_txt, (posx, (self.font_size[1] * i) + posy))



    def draw(self, surf, cursor_surf_rect_pos, text, curr_line, curr_col):
        if self.dispAutoCompleteWindow and text[curr_line]:
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

