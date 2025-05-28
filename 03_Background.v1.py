"""03_Background V1
Description: making the player, design, controls, hitbox and animations
Updates: Creating a road generator class for background
By Rafael Anggawijaya 
"""

import pygame
import sys
import math

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
BLACK = (0,0,0)
PLAYER_COLOUR = (40, 18, 150)
GRASS_COLOUR = (130, 235, 49)
ROAD_COLOUR = (45, 46, 45)

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 5

# class for background
class Background:
    def __init__(self):
        # sets the size to screen
        self.height = HEIGHT
        self.width = WIDTH
        self.background = pygame.Surface((WIDTH,HEIGHT))
        
        # generate road pattern
        self.road_map = self.generate_road_map()
        self.draw_background()

    def generate_road_map(self):
        # Creates the backbround
        rows = self.height // TILE_SIZE
        collum = self.width // TILE_SIZE
        background = [[0 for _ in range(collum)] for _ in range(rows)]

        # road
        center_y = rows // 2
        for x in range(collum):
            for dy in range(-ROAD_WIDTH//2, ROAD_WIDTH//2 + 1):
                if 0 <= center_y + dy < rows:
                    background[center_y + dy][x] = 1
        
        return background
    def draw_background(self):
        # Fill backgorund with grass
        screen.fill(GRASS_COLOUR)
        # Draw roads
        for y in range(len(self.road_map)):
            for x in range(len(self.road_map[0])):
                if self.road_map[y][x] == 1:
                    pygame.draw.rect(
                        self.background, 
                        ROAD_COLOUR, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )
    def draw(self,screen):
        # draws the screen
        screen.blit(self.background,(0,0))




# Main game loop
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # draw
    screen.fill(GRASS_COLOUR)
    Background.draw(screen)

    pygame.display.update()
    clock.tick(60)