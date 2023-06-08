import pygame
import os
import json
from pygame.locals import *
from ...algorithms import *

class FileManager:
    def __init__(self, bg_color, font, width, height, fg_color = (0, 0, 0)):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font = pygame.font.Font("data/plugins/FileManager/data/font/robot_mono.ttf", 16)
        self.heading_font = pygame.font.Font("data/plugins/FileManager/data/font/retro_font.ttf", 24)
        self.heading = self.heading_font.render("File Explorer".upper(), 1, (0, 0, 0))
        self.isOpen = False
        
        self.dir_list = os.listdir(os.getcwd())
        self.relative_path = os.path.dirname(__file__) # recalculating relative path
        with open("data/plugins/FileManager/data/icons.json", "r") as file:
            self.ics = json.load(file)
        self.ic_imgs = {}
        for k, v in self.ics.items():
            self.ic_imgs[k] = pygame.image.load(v).convert_alpha()

        self.width = width
        self.height = height
        self.opening_n_closing_speed = cnv_to_per(10, self.width)
        self.fm_rect = pygame.Rect((0, 0, 0, self.height))
        self.dirnames_x = -self.width + 10 # just for off screen
        self.dirnames_top = 40
        self.dirnames_margin = 22
    
    # Handle events
    def handle_events(self, event, ctrl):
        if event.key == pygame.K_t and ctrl:
            self.isOpen = not self.isOpen
            print("Open file manger", self.isOpen)
            return True # just for not adding character
    
    # Display dirnames
    def display_dirnames(self, surf):
        surf.blit(self.heading, (self.dirnames_x - 18, 10))
        for i, dirs in enumerate(self.dir_list):
            dir_name = self.font.render(dirs, 1, self.fg_color)
            pos = (self.dirnames_x - 12,  (self.dirnames_margin * (i + 1)) + self.dirnames_top)
            if self.fm_rect.width >= self.width//2:
                surf.blit(dir_name, (self.dirnames_x + 12, (self.dirnames_margin * (i + 1))+ self.dirnames_top))
                self.draw_icon(surf, dirs, pos)
    

    def reload(self):
        self.dir_list = os.listdir(os.getcwd())
        # with open(os.getcwd().replace("\\","/") + "/data/plugins/FileManager/data/icons.json", "r") as file:
        #     self.ics = json.load(file)
        # self.ic_imgs = {}
        # for k, v in self.ics.items():
        #     self.ic_imgs[k] = pygame.image.load(v).convert_alpha()

    def draw_icon(self, surf, dirs, pos):
        file_name = dirs.split(".")
        if len(file_name) == 1:
            surf.blit(self.ic_imgs["folder_ic"], pos)
        if len(file_name) == 2:
            try:
                surf.blit(self.ic_imgs[file_name[-1] + "_ic"], pos)
            except:
                surf.blit(self.ic_imgs["default_ic"], pos)
                print(f"icon of {file_name[-1]} not present in database")

    # Draw 
    def draw(self, surf):
        if self.isOpen:
            if self.fm_rect.width <= self.width:
                self.fm_rect.width += self.opening_n_closing_speed
                self.dirnames_x += self.opening_n_closing_speed
        else:
            if self.fm_rect.width > 0:
                self.fm_rect.width -= self.opening_n_closing_speed
                self.dirnames_x -= self.opening_n_closing_speed
        
        # Lazy loading
        if self.fm_rect.width > 0:
            
            pygame.draw.rect(surf, self.bg_color, self.fm_rect)
            self.display_dirnames(surf)