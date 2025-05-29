"""02_Player V3.1
Description: making the player, design, controls, hitbox and animations
Updates: Trialling different moving options (angle change for left and right movement)
kept the car centered to the screen and can only turn 
(This makes it so background and objects around the car move around relative to the player)
By Rafael Anggawijaya 
"""

import pygame
import sys
import math

# Starting pygame
pygame.init()

# Setting up screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Ricers")

# Player Car size
player_width = 50
player_length = 75

# Frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
player_colour = (40, 18, 150)


class Player:
    def __init__(self, width, height, color):
        # Create a surface for the player
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.original_image.fill(color)
        
        # Position will always be center
        self.pos = [WIDTH // 2, HEIGHT // 2]
        
        # Rotation variables
        self.direction = 0  # Angle in degrees
        self.rotation_speed = 3  # How fast the car turns
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def movement(self, user_input):
        # Handle rotation only
        if user_input[pygame.K_LEFT] or user_input[pygame.K_a]:
            self.direction += self.rotation_speed
        if user_input[pygame.K_RIGHT] or user_input[pygame.K_d]:
            self.direction -= self.rotation_speed
        
        # Keep direction within 0-360 degrees
        self.direction %= 360
        
        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, self.direction)
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# Create player
player = Player(player_width, player_length, player_colour)

# Main game loop
while True:
    # sets the colour of the background
    screen.fill(WHITE)
    # quit game (helps testing)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    user_movement = pygame.key.get_pressed()
    player.movement(user_movement)
    player.draw(screen)

    pygame.display.update()
    clock.tick(60)