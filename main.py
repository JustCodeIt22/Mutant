import pygame, sys
from TextEditor import *

pygame.init()

version = 2.0
pygame.display.set_caption(f"Mutant v{version}")

logo = pygame.image.load("data/imgs/mu_logo.png")
pygame.display.set_icon(logo)

clock = pygame.time.Clock()
dispInfo = pygame.display.Info()
SCREEN_WIDTH = 800 #dispInfo.current_w
SCREEN_HEIGHT = 600 #dispInfo.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
texteditor = TextEditor((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            running = False
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.display.quit()
                pygame.quit()
                running = False
                sys.exit()
        texteditor.handle_events(event)
    
    screen.fill(texteditor.bg_color)
    texteditor.draw()
    pygame.display.update()
    clock.tick(60)