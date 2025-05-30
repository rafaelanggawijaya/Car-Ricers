"""Testing
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
PLAYER_COLOUR = (40, 18, 150)
GRASS_COLOUR = (130, 235, 49)
ROAD_COLOUR = (45, 46, 45)
AI_CAR_COLORS = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 15

# Car dimensions
CAR_WIDTH = 50
CAR_LENGTH = 80  # Longer side will be front/back
SAFE_DISTANCE = CAR_LENGTH * 1.5  # Minimum distance between cars

class AICar:
    def __init__(self, y_pos):
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.color = random.choice(AI_CAR_COLORS)
        self.speed = random.uniform(5, 15)  # Random speed between 5 and 15
        self.original_speed = self.speed  # Store original speed for resetting
        
        # Calculate road boundaries
        road_center_x = WIDTH // 2
        road_half_width = (ROAD_WIDTH * TILE_SIZE) // 2
        
        # Determine which lane to spawn in (1 of 4 lanes)
        self.lane = random.randint(0, 3)
        lane_width = (ROAD_WIDTH * TILE_SIZE) / 4
        
        # Calculate x position based on lane
        self.x = road_center_x - road_half_width + (self.lane * lane_width) + (lane_width / 2) - (self.width / 2)
        
        # Start position (top of screen)
        self.y = y_pos
        
        # Lane change variables
        self.lane_change_timer = 0
        self.target_lane = self.lane
        self.is_changing_lanes = False
        self.lane_change_speed = 2  # How fast lane changes happen
        
        # Collision avoidance
        self.avoiding_collision = False
        self.avoidance_timer = 0
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.length)
    
    def check_collision(self, other_car):
        return self.get_rect().colliderect(other_car.get_rect())
    
    def check_proximity(self, other_cars):
        """Check if any car is too close in front or behind"""
        for car in other_cars:
            if car != self:
                # Check vertical distance (same lane or adjacent lanes)
                vertical_dist = abs(car.y - self.y)
                lane_dist = abs(car.lane - self.lane)
                
                # If car is in front and close
                if (car.y < self.y and vertical_dist < SAFE_DISTANCE and lane_dist <= 1):
                    return True
        return False
    
    def find_safe_lane(self, other_cars):
        """Find the safest lane to change to (left or right)"""
        current_lane = self.lane
        possible_lanes = []
        
        # Check if left lane is available
        if current_lane > 0:
            left_lane_clear = True
            for car in other_cars:
                if car != self and car.lane == current_lane - 1 and abs(car.y - self.y) < SAFE_DISTANCE:
                    left_lane_clear = False
                    break
            if left_lane_clear:
                possible_lanes.append(current_lane - 1)
        
        # Check if right lane is available
        if current_lane < 3:
            right_lane_clear = True
            for car in other_cars:
                if car != self and car.lane == current_lane + 1 and abs(car.y - self.y) < SAFE_DISTANCE:
                    right_lane_clear = False
                    break
            if right_lane_clear:
                possible_lanes.append(current_lane + 1)
        
        # Return a random safe lane if available
        if possible_lanes:
            return random.choice(possible_lanes)
        return current_lane  # Stay in current lane if no safe options
    
    def update(self, background_speed, other_cars):
        # Check for cars in proximity
        if self.check_proximity(other_cars):
            if not self.avoiding_collision:
                self.avoiding_collision = True
                self.avoidance_timer = 30  # About 0.5 seconds at 60 FPS
                
                # Slow down slightly when avoiding
                self.speed = max(self.original_speed * 0.8, 5)
                
                # Try to find a safer lane
                self.target_lane = self.find_safe_lane(other_cars)
                if self.target_lane != self.lane:
                    self.is_changing_lanes = True
        else:
            if self.avoiding_collision:
                self.avoidance_timer -= 1
                if self.avoidance_timer <= 0:
                    self.avoiding_collision = False
                    self.speed = self.original_speed
        
        # Move car downward (relative to background scroll)
        self.y += self.speed + background_speed
        
        # Random lane changing logic (only when not avoiding)
        if not self.avoiding_collision:
            self.lane_change_timer -= 1
            if self.lane_change_timer <= 0 and not self.is_changing_lanes:
                if random.random() < 0.01:  # 1% chance per frame to consider lane change
                    if random.random() < 0.5 and self.lane > 0:  # Try to move left
                        self.target_lane = self.lane - 1
                        self.is_changing_lanes = True
                    elif self.lane < 3:  # Try to move right
                        self.target_lane = self.lane + 1
                        self.is_changing_lanes = True
                    self.lane_change_timer = random.randint(60, 180)  # 1-3 seconds before next attempt
        
        # Handle lane changing
        if self.is_changing_lanes:
            road_center_x = WIDTH // 2
            road_half_width = (ROAD_WIDTH * TILE_SIZE) // 2
            lane_width = (ROAD_WIDTH * TILE_SIZE) / 4
            
            target_x = road_center_x - road_half_width + (self.target_lane * lane_width) + (lane_width / 2) - (self.width / 2)
            
            # Move toward target lane
            if abs(self.x - target_x) < 1:  # Reached target
                self.x = target_x
                self.lane = self.target_lane
                self.is_changing_lanes = False
            else:
                self.x += (target_x - self.x) * 0.05  # Smooth interpolation
        
        # Wrap around when off screen
        if self.y > HEIGHT + self.length:
            self.y = -self.length
            self.lane = random.randint(0, 3)  # Random new lane when respawning
            self.speed = random.uniform(5, 15)  # Random new speed
            self.original_speed = self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.length))
        # Add some details to make it look more like a car
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, self.width - 10, 10))  # Windshield
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + self.length - 15, self.width - 10, 10))  # Rear window

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
        
        # Edge line properties (keep existing)
        line_width = 4
        line_length = TILE_SIZE * 2
        line_gap = TILE_SIZE * 2
        
        # Draw center dashed lines (modified for 4 lanes)
        # First calculate lane positions
        lane_width = ROAD_WIDTH * TILE_SIZE / 4  # Split road into 4 lanes
        for lane_divider in [-1, 0, 1]:  # Now drawing 3 dividers for 4 lanes
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
        
        # Keep existing continuous edge lines (no changes)
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

# Create AI cars
ai_cars = []
for i in range(8):  # Create 8 AI cars
    # Space them out vertically
    ai_cars.append(AICar(random.randint(-HEIGHT, 0)))

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    
    # Update systems
    background.update(keys)
    
    # Update AI cars (passing the list of all cars for collision detection)
    for car in ai_cars:
        car.update(background.speed, ai_cars)
    
    # Draw everything
    background.draw(screen)
    
    # Draw AI cars
    for car in ai_cars:
        car.draw(screen)
    
    pygame.display.update()
    clock.tick(60)