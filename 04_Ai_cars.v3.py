"""04 Ai_cars v1
Description: this is the 'obstacles' the playerwill hve to avoid
Updates: added ai designs and continued to change ai
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
        self.acceleration = 0.2
        self.max_speed = 5
        self.deceleration = 0.4
        self.brake_strength = BRAKE_STRENGTH
        self.brake_hold_time = False
        self.brake_cooldown = 2000  # 2000ms = 2 seconds
        self.drift_speed = 1  # downward motion when not movinvg
        self.max_drift_speed = 2  # Maximum drift speed
        
        self.original_image = pygame.transform.rotate(self.original_image, -90)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def movement(self, user_input):
        # holds current co-ordinates for collison detection
        prev_pos = self.pos.copy()
        prev_velocity = self.velocity.copy()
        # Acceleration foward
        if user_input[pygame.K_UP] or user_input[pygame.K_w]:
            self.brake_hold_time = False
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

        collision = self.check_road_collision(background)
        
        if any(collision.values()):  # If any collision occurred
            # Only zero velocity in the direction of collision
            if collision['left'] or collision['right']:
                self.velocity.x = 0
                # Push away from the edge
                if collision['left']:
                    self.pos.x += 2
                else:
                    self.pos.x -= 2
            
            if collision['top'] or collision['bottom']:
                self.velocity.y = 0
                # Push away from the edge
                if collision['top']:
                    self.pos.y += 2
                else:
                    self.pos.y -= 2
            
            # Maintain rotation
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
    
    def check_road_collision(self, background):
        # Get car's hitbox rectangle
        car_rect = self.image.get_rect(center=self.pos)
        
        # Check multiple points around the perimeter for better precision
        check_points = [
            (car_rect.midleft),    # Left side
            (car_rect.midright),   # Right side
            (car_rect.midtop),     # Front
            (car_rect.midbottom),  # Back
            (car_rect.topleft),    # Corners
            (car_rect.topright),
            (car_rect.bottomleft),
            (car_rect.bottomright)
        ]
        
        # Track which edges are colliding
        collision_info = {
            'left': False,
            'right': False,
            'top': False,
            'bottom': False
        }
        
        for point_x, point_y in check_points:
            tile_x = int(point_x // TILE_SIZE)
            tile_y = int(point_y // TILE_SIZE)
            
            if (0 <= tile_y < len(background.road_map) and 
                0 <= tile_x < len(background.road_map[0])):
                if background.road_map[tile_y][tile_x] == 0:
                    # Determine which edge is colliding
                    if point_x == car_rect.left:
                        collision_info['left'] = True
                    elif point_x == car_rect.right:
                        collision_info['right'] = True
                    if point_y == car_rect.top:
                        collision_info['top'] = True
                    elif point_y == car_rect.bottom:
                        collision_info['bottom'] = True
        
        return collision_info
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class AiCar:
    def __init__(self, lane):
        # Ai variables
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.colour = AI_HITBOX_COLOUR
        self.colour_name = AI_CAR_COLOURS[lane]
        self.image = pygame.image.load(f"ai_{self.colour_name}_car.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.length))
        self.original_image = self.image.copy()
        self.speed = random.uniform(1, 7)
        self.lane = lane
        self.boost_multiplier = 2.0  # How much they accelerate when brakes are pressed
        self.boost_duration = 0
        self.max_boost_duration = 60
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.length)
        self.reset_car()
        
    def reset_car(self):
        road_center_x = WIDTH // 2
        road_left = road_center_x - (ROAD_WIDTH * TILE_SIZE) // 2
        
        # Calculate random position within lane
        lane_center = road_left + (self.lane * LANE_WIDTH) + (LANE_WIDTH // 2)
        min_x = lane_center - (LANE_WIDTH // 2) + (self.width // 2)
        max_x = lane_center + (LANE_WIDTH // 2) - (self.width // 2)
        self.x = random.uniform(min_x, max_x)
        
        # Start above screen with random delay
        self.y = random.randint(-HEIGHT * 2, -CAR_LENGTH)
        
        # random speed each respawn
        self.speed = random.uniform(1.5, 6.5)
            
    def update(self, scroll_speed, braking):
        # Handle acceleration/deceleration
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            # Handle boost when player brakes
            self.y -= self.speed
        else:
        
            self.y += self.speed + scroll_speed * 0.1
        
        # When car exits screen, reset it
        if self.y > HEIGHT:
            self.reset_car()
        
        self.rect.y = self.y
        self.rect.x = self.x
    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.length), 4)
        screen.blit(self.image, (self.x, self.y))
        

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
        self.brake_strength = BRAKE_STRENGTH
        
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
player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOUR)
ai_cars = [AiCar(i) for i in range(4)]  # One car per lane

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

     # Update AI cars and check for collisions
    for car in ai_cars:
        car.update(background.speed, keys)
        
        # Check collision between player and this AI car
        if player.rect.colliderect(car.rect):
            print("Collision detected!")
            # Handle collision (e.g., reduce speed, play sound, etc.)
            player.velocity *= 0.5  # Slow down player on collision
            
            # Optional: Push player away from collision
            if player.rect.centerx < car.rect.centerx:
                player.pos.x -= 10
            else:
                player.pos.x += 10
                
            # Update player rect after position change
            player.rect = player.image.get_rect(center=player.pos)
    
    # Update AI cars
    for car in ai_cars:
        car.update(background.speed, keys)
    
    # Draw everything
    background.draw(screen)
    player.draw(screen)
    for car in ai_cars:
        car.draw(screen)
    
    pygame.display.update()
    clock.tick(60)