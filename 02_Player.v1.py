"""02_Player V1
Description: making the player, design, controls, hitbox and animations
Updates:Added a box to represent the car (will be used of hitbox later)
By Rafael Anggawijaya 
"""
import pygame
import sys


# Starting pygame
pygame.init()

# Setting up screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Ricers")

# Player
player = [600,550,50,75]
# Colors
WHITE = (255, 255, 255)
player_colour = (40, 18, 150)


# Main game loop
while True:
    # sets the colour of the background
    screen.fill(WHITE)
    # quit game (helps testing)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.draw.rect(screen, player_colour, player)

    pygame.display.update()
