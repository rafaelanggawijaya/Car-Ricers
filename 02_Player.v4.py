"""02_Player V4
Description: making the player, design, controls, hitbox and animations
Updates: added car image 
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
pygame.display.set_caption("Car Ricers - Pixel Roads")

# Colors
SKY_COLOR = (100, 180, 255)
GRASS_COLOR = (60, 160, 60)
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (200, 200, 200)
PLAYER_COLOR = (40, 18, 150)

# Tile settings
TILE_SIZE = 40
ROAD_WIDTH = 5  # in tiles

# Car dimensions
CAR_WIDTH = 40
CAR_LENGTH = 60

# Frame rate
clock = pygame.time.Clock()

class RoadBackground:
    def __init__(self):
        # Create a larger surface than screen for scrolling
        self.bg_width = WIDTH * 2
        self.bg_height = HEIGHT * 2
        self.background = pygame.Surface((self.bg_width, self.bg_height))
        
        # Generate road pattern
        self.road_map = self.generate_road_map()
        self.draw_background()
        
        # For scrolling
        self.offset_x = WIDTH//2 - self.bg_width//2
        self.offset_y = HEIGHT//2 - self.bg_height//2
    
    def generate_road_map(self):
        # Create empty map (0 = grass, 1 = road)
        rows = self.bg_height // TILE_SIZE
        cols = self.bg_width // TILE_SIZE
        road_map = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # Horizontal main road
        center_y = rows // 2
        for x in range(cols):
            for dy in range(-ROAD_WIDTH//2, ROAD_WIDTH//2 + 1):
                if 0 <= center_y + dy < rows:
                    road_map[center_y + dy][x] = 1
        
        # Vertical intersecting roads every 20 tiles
        for x in range(0, cols, 20):
            for y in range(rows):
                for dx in range(-ROAD_WIDTH//2, ROAD_WIDTH//2 + 1):
                    if 0 <= x + dx < cols:
                        road_map[y][x + dx] = 1
        
        return road_map
    
    def draw_background(self):
        # Fill with grass
        self.background.fill(GRASS_COLOR)
        
        # Draw roads
        for y in range(len(self.road_map)):
            for x in range(len(self.road_map[0])):
                if self.road_map[y][x] == 1:
                    pygame.draw.rect(
                        self.background, 
                        ROAD_COLOR, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )
        
        # Draw road markings
        self.draw_road_markings()
    
    def draw_road_markings(self):
        # Horizontal center lines
        center_y = len(self.road_map) // 2
        for x in range(0, self.bg_width, TILE_SIZE * 4):
            pygame.draw.rect(
                self.background,
                LINE_COLOR,
                (x, center_y * TILE_SIZE - 2, TILE_SIZE * 3, 4)
            )
        
        # Vertical center lines
        for x in range(0, len(self.road_map[0]), 20):
            for y in range(0, self.bg_height, TILE_SIZE * 4):
                pygame.draw.rect(
                    self.background,
                    LINE_COLOR,
                    (x * TILE_SIZE - 2, y, 4, TILE_SIZE * 3)
                )
    
    def update_offset(self, car_pos):
        # Center background on car with smoothing
        target_x = WIDTH//2 - car_pos[0]
        target_y = HEIGHT//2 - car_pos[1]
        
        self.offset_x += (target_x - self.offset_x) * 0.1
        self.offset_y += (target_y - self.offset_y) * 0.1
    
    def draw(self, screen):
        # Draw the visible portion of background
        screen.blit(self.background, (self.offset_x, self.offset_y))

class Player:
    def __init__(self, width, height, color):
        # uploads image
        self.original_image = self.original_image = pygame.image.load("player_car.png").convert_alpha()
        # changes scale of image
        self.original_image = pygame.transform.scale(self.original_image, (width, height))

        # Hitbox for testing
        pygame.draw.rect(self.original_image, color, (0, 0, width, height), 5)
        
        # Add yellow dot to indicate front (top center)
        pygame.draw.circle(self.original_image, (255, 255, 0), (width//2, 10), 5)
        
        # Position and movement variables
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = pygame.math.Vector2()
        self.direction = 270  # 270° = pointing up
        self.rotation_speed = 3
        self.acceleration = 0.2
        self.max_speed = 5
        self.deceleration = 0.1
        self.brake_strength = 0.3
        
        # Rotate original image so top (yellow dot) faces right initially
        self.original_image = pygame.transform.rotate(self.original_image, -90)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def movement(self, user_input):
        # Handle acceleration forward (W/UP)
        if user_input[pygame.K_UP] or user_input[pygame.K_w]:
            # Calculate acceleration vector in facing direction
            rad = math.radians(self.direction)
            self.velocity.x += math.cos(rad) * self.acceleration
            self.velocity.y += math.sin(rad) * self.acceleration
        
        # Handle braking/reversing (S/DOWN)
        if user_input[pygame.K_DOWN] or user_input[pygame.K_s]:
            # Brake in current direction
            if self.velocity.length() > 0:
                brake_dir = self.velocity.normalize()
                self.velocity.x -= brake_dir.x * self.brake_strength
                self.velocity.y -= brake_dir.y * self.brake_strength
        
        # Natural deceleration
        if not (user_input[pygame.K_UP] or user_input[pygame.K_w] or 
                user_input[pygame.K_DOWN] or user_input[pygame.K_s]):
            if self.velocity.length() > self.deceleration:
                decel_dir = self.velocity.normalize()
                self.velocity.x -= decel_dir.x * self.deceleration
                self.velocity.y -= decel_dir.y * self.deceleration
            else:
                self.velocity = pygame.math.Vector2()
        
        # Limit speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Handle steering
        turn_speed = self.rotation_speed * (0.2 + 0.8 * (self.velocity.length() / self.max_speed))
        
        if user_input[pygame.K_LEFT] or user_input[pygame.K_a]:
            self.direction -= turn_speed
        if user_input[pygame.K_RIGHT] or user_input[pygame.K_d]:
            self.direction += turn_speed
        
        # Keep direction within 0-360 degrees
        self.direction %= 360
        
        # Update position
        self.pos += self.velocity
        
        # Rotate the image (negative because pygame y-axis is inverted)
        self.image = pygame.transform.rotate(self.original_image, -self.direction)
        self.rect = self.image.get_rect(center=self.pos)
        
    
    def draw(self, screen):
        # Always draw car at screen center (background moves instead)
        screen.blit(self.image, self.rect)

# Create game objects
road_bg = RoadBackground()
player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOR)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Update
    user_input = pygame.key.get_pressed()
    player.movement(user_input)
    road_bg.update_offset(player.pos)
    
    # Draw
    screen.fill(SKY_COLOR)  # Fill areas beyond background
    road_bg.draw(screen)
    player.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)