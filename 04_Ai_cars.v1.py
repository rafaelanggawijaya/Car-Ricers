"""04 Ai_cars v1
Description: this is the 'obstacles' the playerwill hve to avoid
Updates: made ai cars which randomly spawn and move down the screen
By Rafael Anggawijaya 
"""

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
AI_CAR_COLORS = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 15  # In tiles
LANE_COUNT = 4
LANE_WIDTH = (ROAD_WIDTH * TILE_SIZE) // LANE_COUNT

# Car dimensions
CAR_WIDTH = 50
CAR_LENGTH = 80

class AICar:
    def __init__(self, lane):
        # variables for ai
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.color = AI_CAR_COLORS[lane]
        self.speed = random.uniform(1, 7)
        self.lane = lane
        self.reset_car()
        
    def reset_car(self):
        # Place car at random position above screen with new random speed
        road_center_x = WIDTH // 2
        road_left = road_center_x - (ROAD_WIDTH * TILE_SIZE) // 2
        
        # Calculate x position based on lane
        self.x = road_left + (self.lane * LANE_WIDTH) + (LANE_WIDTH // 2) - (self.width // 2)
        
        # Start above screen with random delay
        self.y = random.randint(-HEIGHT, -CAR_LENGTH)
        
    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        
        # When car exits screen, reset it
        if self.y > HEIGHT:
            self.reset_car()
            
    def draw(self, screen):
        # Ai hitboxes
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.length), 4)

class Background:
    def __init__(self):
        self.height = HEIGHT
        self.width = WIDTH
        self.background = pygame.Surface((WIDTH, HEIGHT))
        
        # animations variables
        self.scroll_y = 0
        self.speed = 0
        self.max_speed = 30
        self.acceleration = 0.1
        self.deceleration = 0.2
        self.brake_strength = 0.3
        
        # Generate road pattern
        self.road_map = self.generate_road_map()
        self.draw_background()

    def generate_road_map(self):
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
        # Fill background with grass
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
    
    def update(self, keys):
        # Handle acceleration/deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.brake_strength, 0)
        else:
            self.speed = max(self.speed - self.deceleration, 0)
        
        # Update scroll position
        self.scroll_y += self.speed
        self.scroll_y %= (TILE_SIZE * 4)
        
        # Redraw background with new scroll position
        self.draw_background()
    
    def draw_road_markings(self):
        road_center_x = self.width // 2
        road_half_width = (ROAD_WIDTH * TILE_SIZE) // 2
        
        # Edge line properties
        line_width = 4
        line_length = TILE_SIZE * 2
        line_gap = TILE_SIZE * 2
        
        # Draw center dashed lines (for 4 lanes)
        lane_width = (ROAD_WIDTH * TILE_SIZE) / 4
        for lane_divider in [-1, 0, 1]:  # 3 dividers for 4 lanes
            line_x = road_center_x + (lane_divider * lane_width)
            for y in range(-int(self.scroll_y), self.height, line_length + line_gap):
                pygame.draw.rect(
                    self.background,
                    WHITE,
                    (line_x - line_width//2,
                    y,
                    line_width,
                    line_length)
                )
        
        # Continuous edge lines
        pygame.draw.rect(
            self.background,
            WHITE,
            (road_center_x - road_half_width, 0, line_width, self.height)
        )
        pygame.draw.rect(
            self.background,
            WHITE,
            (road_center_x + road_half_width - line_width, 0, line_width, self.height)
        )
    
    def draw(self, screen):
        screen.blit(self.background, (0, 0))

# Create game objects
background = Background()
ai_cars = [AICar(i) for i in range(4)]  # One car per lane

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    
    # Update systems
    background.update(keys)
    
    # Update AI cars
    for car in ai_cars:
        car.update(background.speed)
    
    # Draw everything
    background.draw(screen)
    for car in ai_cars:
        car.draw(screen)
    
    pygame.display.update()
    clock.tick(60)