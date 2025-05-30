"""03_Background V1
Description: This is going to be a road on some open 
grass with animations which match the ovement of 
the car (accelrating and deccelerating)
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
ROAD_WIDTH = 15

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
        # makes the road
        rows = math.ceil(self.height / TILE_SIZE)  
        columns = math.ceil(self.width / TILE_SIZE)

        background = [[0 for _ in range(columns)] for _ in range(rows)]

        # Vertical road in center
        center_x = columns // 2
        for y in range(rows):
            for dx in range(-ROAD_WIDTH//2, ROAD_WIDTH//2 + 1):
                if 0 <= center_x + dx < columns:
                    background[y][center_x + dx] = 1
            
        return background
        
    def draw_background(self):
        # Fill backgorund with grass
        self.background.fill(GRASS_COLOUR)
        # Draw roads
        for y in range(len(self.road_map)):
            for x in range(len(self.road_map[0])):
                if self.road_map[y][x] == 1:
                    pygame.draw.rect(
                        self.background, 
                        ROAD_COLOUR, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )
        # Draw road markings
        self.draw_road_markings()
    
    def draw_road_markings(self):
        # Calculate road center position (in pixels)
        road_center_x = self.width // 2
        
        # Calculate marking dimensions
        mark_width = 4
        mark_height = TILE_SIZE * 2  # Height of each dash
        mark_gap = TILE_SIZE * 2     # Space between dashes
        
        # Draw dashed center line
        for y in range(0, self.height, mark_height + mark_gap):
            pygame.draw.rect(
                self.background,
                WHITE,
                (road_center_x - mark_width//2,  # Center the marking horizontally
                y,                              # Vertical position
                mark_width,                     # Line thickness
                mark_height)                    # Line length
            )
                    
    def draw(self,screen):
        # draws the screen
        screen.blit(self.background,(0,0))



background = Background()
# Main game loop
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # draw
    background.draw(screen)

    pygame.display.update()
    clock.tick(60)