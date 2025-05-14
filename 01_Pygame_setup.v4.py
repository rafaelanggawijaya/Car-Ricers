"""01_Pygame_setup V4
Description: Setting up the UI of the game
Updates: Testing out resizeable window
By Rafael Anggawijaya 
"""
import pygame
import sys


# Starting pygame
pygame.init()

# Setting up screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Car Ricers")

# Colors
WHITE = (255, 255, 255)


# Main game loop
while True:
    # sets the colour of the background
    screen.fill(WHITE)
    # quit game (helps testing)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)