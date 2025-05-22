"""02_Player V3
Description: making the player, design, controls, hitbox and animations
Updates: Added boudaries to stop car from leaving the screen
By Rafael Anggawijaya 
"""
import pygame
import sys


# Starting pygame
pygame.init()

# Setting up screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Ricers")

# Player Car size
player_width = 50
player_length = 75
# Intial Co ordinates
intial_x = 600
intial_y = 550

# Fame rate
clock= pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
player_colour = (40, 18, 150)


class Player:
    def __init__(self, player_image, speed_x, speed_y):
        # changing variables
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.player_image = player_image

        # Intial Co_ordinates
        self.player_rect = self.player_image.get_rect()
        self.player_rect.x = intial_x
        self.player_rect.y = intial_y

        # Variables
        self.change_x = 0
        self.change_y = 0



    def movement(self, user_input):
        # Checks if key pressed
        if user_input[pygame.K_LEFT] or user_input[pygame.K_a]:
            self.change_x = -self.speed_x # changes left
        elif user_input[pygame.K_RIGHT] or user_input[pygame.K_d]:
            self.change_x = self.speed_x # changes right
        elif user_input[pygame.K_UP] or user_input[pygame.K_w]:
            self.change_y = -self.speed_y # changes up
        elif user_input[pygame.K_DOWN] or user_input[pygame.K_s]:
            self.change_y = self.speed_y # changes down

        self.player_rect.x += self.change_x
        self.player_rect.y += self.change_y

        # boundaries
        if self.player_rect.x < 0:
            self.player_rect.x = 0
        if self.player_rect.y < 0:
            self.player_rect.y = 0
        if self.player_rect.x > screen.get_width() - player_width:
            self.player_rect.x = screen.get_width() - player_width
        if self.player_rect.y > screen.get_height() - player_length:
            self.player_rect.y = screen.get_height() - player_length

    def draw(self, screen):
        screen.blit(self.player_image, (self.player_rect.x, self.player_rect.y))
# Hitbox/placeholder car design
player_hitbox = pygame.Surface((player_width, player_length))
player_hitbox.fill(player_colour)
player = Player(player_hitbox, 4, 5)





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
