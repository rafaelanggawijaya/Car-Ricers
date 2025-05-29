"""03_Background V2
Description: This is going to be a road on some open 
grass with animations which match the ovement of 
the car (accelrating and deccelerating)
Updates: This is going to be a road on some open 
grass with animations which match the movement of 
the car (accelrating and deccelerating)
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
BLACK = (0, 0, 0)
PLAYER_COLOUR = (40, 18, 150)
GRASS_COLOUR = (130, 235, 49)
ROAD_COLOUR = (45, 46, 45)

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 15

# Car dimensions
CAR_WIDTH = 50
CAR_LENGTH = 80  # Longer side will be front/back

class Background:
    def __init__(self):
        self.height = HEIGHT
        self.width = WIDTH
        self.background = pygame.Surface((WIDTH, HEIGHT))
        
        # animations variables
        self.scroll_y = 0
        self.speed = 0
        self.max_speed = 10
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
        
        # Draw center dashed line with scrolling
        for y in range(-int(self.scroll_y), self.height, line_length + line_gap):
            pygame.draw.rect(
                self.background,
                WHITE,
                (road_center_x - line_width//2,
                 y,
                 line_width,
                 line_length)
            )
        
        # Draw continuous edge lines
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

class Player:
    def __init__(self, width, height, color):
        # Create surface with original dimensions (width=50, height=80)
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Load and scale the car
        self.player_image = pygame.image.load("player_car.png").convert_alpha()
        self.player_image = pygame.transform.scale(self.player_image, (width, height))
        
        # Draw car
        self.original_image.blit(self.player_image, (0, 0))
        
        # Hitbox
        pygame.draw.rect(self.original_image, color, (0, 0, width, height), 2)
        
        # Add yellow front indicator 
        pygame.draw.circle(self.original_image, (255, 255, 0), (width//2, 10), 5)
        
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = pygame.math.Vector2()
        self.direction = 270  # Pointing up
        self.rotation_speed = 3
        self.acceleration = 0.1
        self.max_speed = 2
        self.deceleration = 0.4
        self.brake_strength = 0.1
        self.brake_hold_time = False
        self.brake_cooldown = 2000  # 2000ms = 2 seconds
        self.drift_speed = 1  # downward motion when not movinvg
        self.max_drift_speed = 2  # Maximum drift speed
        
        self.original_image = pygame.transform.rotate(self.original_image, -90)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def movement(self, user_input):
        # Acceleration foward
        if user_input[pygame.K_UP] or user_input[pygame.K_w]:
            rad = math.radians(self.direction)
            self.velocity.x += math.cos(rad) * self.acceleration
            self.velocity.y += math.sin(rad) * self.acceleration
        
        # Braking
        if user_input[pygame.K_DOWN] or user_input[pygame.K_s]:
            if self.velocity.length() > 0 and self.brake_hold_time == False:
                brake_dir = self.velocity.normalize()
                self.velocity.x -= brake_dir.x * self.brake_strength
                self.velocity.y -= brake_dir.y * self.brake_strength
                # cheecks if velocity hits zero
                if (brake_dir.x > 0 and self.velocity.x < 0) or (brake_dir.x < 0 and self.velocity.x > 0) or \
                (brake_dir.y > 0 and self.velocity.y < 0) or (brake_dir.y < 0 and self.velocity.y > 0):
                    self.velocity.x = 0
                    self.velocity.y = 0
                    pygame.time.delay(2000)
                    self.brake_hold_time = True
                
            
        
        
        # Check if no movement keys are pressed
        no_movement_keys = not (user_input[pygame.K_UP] or user_input[pygame.K_w] or 
                            user_input[pygame.K_DOWN] or user_input[pygame.K_s])
        
        # Natural deceleration when no keys pressed
        if no_movement_keys or self.brake_hold_time:
            if self.velocity.length() > self.deceleration:
                decel_dir = self.velocity.normalize()
                self.velocity.x -= decel_dir.x * self.deceleration
                self.velocity.y -= decel_dir.y * self.deceleration
            else:
                self.velocity = pygame.math.Vector2()
            
            # Apply downward drift when completely stopped
            if self.velocity.length() == 0:
                self.velocity.y = min(self.velocity.y + self.drift_speed, self.max_drift_speed)
        
        # Speed limit
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Steering
        turn_speed = self.rotation_speed * (0.2 + 0.8 * (self.velocity.length() / self.max_speed))
        
        if user_input[pygame.K_LEFT] or user_input[pygame.K_a]:
            self.direction -= turn_speed
        if user_input[pygame.K_RIGHT] or user_input[pygame.K_d]:
            self.direction += turn_speed
        
        self.direction %= 360
        self.pos += self.velocity
        self.image = pygame.transform.rotate(self.original_image, -self.direction)
        self.rect = self.image.get_rect(center=self.pos)
    
    def keep_on_screen(self):
        car_rect = self.image.get_rect(center=self.pos)
        if car_rect.left < 0:
            self.pos.x -= car_rect.left
        if car_rect.right > WIDTH:
            self.pos.x -= (car_rect.right - WIDTH)
        if car_rect.top < 0:
            self.pos.y -= car_rect.top
        if car_rect.bottom > HEIGHT:
            self.pos.y -= (car_rect.bottom - HEIGHT)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Create game objects
player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOUR)
background = Background()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    
    # Update systems
    background.update(keys)
    player.movement(keys)
    player.keep_on_screen()
    
    # Draw everything
    background.draw(screen)
    player.draw(screen)

    pygame.display.update()
    clock.tick(60)