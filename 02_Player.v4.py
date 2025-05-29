"""02_Player V4
Description: making the player, design, controls, hitbox and animations
Updates: adding in game car image and matching hitbox for testing later
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

# Car dimensions - width < length for proper front/back orientation
CAR_WIDTH = 50
CAR_LENGTH = 80  # Longer side will be front/back

# Frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
PLAYER_COLOR = (40, 18, 150)


class Player:
    def __init__(self, width, height, color):
        # Create surface with original dimensions (width=50, height=80)
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Load and scale the car image to match EXACTLY the original box size
        self.player_image = pygame.image.load("player_car.png").convert_alpha()
        self.player_image = pygame.transform.scale(self.player_image, (width, height))
        
        # Draw the perfectly scaled car image
        self.original_image.blit(self.player_image, (0, 0))
        
        # Draw hollow hitbox (same size as original)
        pygame.draw.rect(self.original_image, color, (0, 0, width, height), 2)
        
        # Add yellow front indicator (position matches original)
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
        
    # boudaries
    def keep_on_screen(self):
    # Get car's rotated rect
        car_rect = self.image.get_rect(center=self.pos)
        
        # Adjust position if needed
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

# Create player
player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOR)

# Main game loop
while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    user_movement = pygame.key.get_pressed()
    player.movement(user_movement)
    player.draw(screen)
    player.keep_on_screen()

    pygame.display.update()
    clock.tick(60)