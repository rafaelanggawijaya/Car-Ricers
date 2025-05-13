"""01_Pygame_setup V2
Description: Setting up the UI of the game
Updates:Changing sizes to find the best dimensions for screen
By Rafael Anggawijaya 
"""
import pygame
import sys


# Starting pygame
pygame.init()

# Setting up screen dimensions
WIDTH, HEIGHT = 1000, 500 # size of the screen (smaller)
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # screen dimensions
pygame.display.set_caption("Car Ricers") # naming of program

# Clock for controlling frame rate
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
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
    