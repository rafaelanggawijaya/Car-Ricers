"""05 Game_loop v1
Description: This is the game ove screen which happens 
when either the player hits another car or brakes for 
too long. It allows the user to play agian or quit or 
go to menu which will be made later
Update: Made the game over screen
By Rafael Anggawijaya"""

import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Ricers")

# Frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRASS_COLOUR = (130, 235, 49)
ROAD_COLOUR = (45, 46, 45)
AI_CAR_COLOURS = ["orange", "red", "blue", "white"]
PLAYER_COLOUR = (40, 18, 150)
AI_HITBOX_COLOUR = (171, 14, 40)

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 15  # In tiles
LANE_COUNT = 4
LANE_WIDTH = (ROAD_WIDTH * TILE_SIZE) // LANE_COUNT

# Car dimensions
CAR_WIDTH = 50
CAR_LENGTH = 80

# multi varible use
BRAKE_STRENGTH = 0.1
# Add these new variables at the top with other game settings
GAME_ACTIVE = True
FONT = pygame.font.SysFont('Arial', 50)
SMALL_FONT = pygame.font.SysFont('Arial', 30)

# Add this function (place it with your other classes)
def end_screen():
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # Game over text
    game_over_text = FONT.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    
    # Restart text
    restart_text = SMALL_FONT.render("Press SPACE to restart", True, WHITE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))

    # quit text
    quit_text = SMALL_FONT.render("Press Q to Quit", True, WHITE)
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 250))
    pygame.display.update()

while True:
    end_screen()