"""Final Car ricers Version
Description: A Car racing game where your objective is to get pass as 
any cars before you crash. Please note to download all images for the
program to work
By Rafael Anggawijaya"""


import pygame
import sys
import math
import random


# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Ricers")
icon = pygame.image.load("game_icon.png")
pygame.display.set_icon(icon)

# Frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRASS_COLOR = (130, 235, 49)
ROAD_COLOR = (45, 46, 45)
AI_CAR_COLORS = ["orange", "red", "blue", "white"]
PLAYER_COLOR = (40, 18, 150)
AI_HITBOX_COLOR = (171, 14, 40)

# Tile settings for creating background
TILE_SIZE = 40
ROAD_WIDTH = 15  # In tiles
LANE_COUNT = 4
LANE_WIDTH = (ROAD_WIDTH * TILE_SIZE) // LANE_COUNT

# Car dimensions
CAR_WIDTH = 50
CAR_LENGTH = 80

# Game variables
BRAKE_STRENGTH = 0.1
FONT = pygame.font.SysFont('Arial', 50)
SMALL_FONT = pygame.font.SysFont('Arial', 30)

# Scoring
score = 0
score_increment_cooldown = 0
SCORE_COOLDOWN = 30

# Menu constants
MENU_FONT_SIZE = 48
MENU_ITEM_PADDING = 20
MENU_COLOR = (255, 255, 255)
MENU_HOVER_COLOR = (255, 200, 0)
MENU_TITLE_COLOR = (255, 0, 0)
MENU_TITLE_SIZE = 64

# Game states
MENU = 0
GAME_ACTIVE = 1
GAME_OVER = 2
HIGH_SCORES = 3
INSTRUCTIONS = 4
current_state = MENU


class Player:
    def __init__(self, width, height, color):
        self.original_image = pygame.Surface((width, height),
                                             pygame.SRCALPHA)
        self.player_image = pygame.image.load("player_car.png").convert_alpha()
        self.player_image = pygame.transform.scale(self.player_image,
                                                   (width, height))
        self.original_image.blit(self.player_image, (0, 0))
        
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.velocity = pygame.math.Vector2()
        self.direction = 270  # Pointing up
        self.rotation_speed = 3
        self.acceleration = 0.2
        self.max_speed = 5
        self.deceleration = 0.4
        self.brake_strength = BRAKE_STRENGTH
        self.brake_hold_time = False
        self.brake_cooldown = 2000  # 2000ms = 2 seconds
        self.drift_speed = 1  # downward motion when not moving
        self.max_drift_speed = 2  # Maximum drift speed
        
        self.original_image = pygame.transform.rotate(self.original_image, -90)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def movement(self, user_input):
        # Acceleration forward
        if user_input[pygame.K_UP] or user_input[pygame.K_w]:
            self.brake_hold_time = False
            rad = math.radians(self.direction)
            self.velocity.x += math.cos(rad) * self.acceleration
            self.velocity.y += math.sin(rad) * self.acceleration
        
        # Braking
        if user_input[pygame.K_DOWN] or user_input[pygame.K_s]:
            if self.velocity.length() > 0 and not self.brake_hold_time:
                brake_dir = self.velocity.normalize()
                self.velocity.x -= brake_dir.x * self.brake_strength
                self.velocity.y -= brake_dir.y * self.brake_strength
                
                if ((brake_dir.x > 0 and self.velocity.x < 0) or 
                    (brake_dir.x < 0 and self.velocity.x > 0) or
                    (brake_dir.y > 0 and self.velocity.y < 0) or 
                    (brake_dir.y < 0 and self.velocity.y > 0)):
                    self.velocity.x = 0
                    self.velocity.y = 0
                    self.brake_hold_time = True
        
        # Check if no movement keys are pressed
        no_movement_keys = not (
            user_input[pygame.K_UP] or user_input[pygame.K_w] or 
            user_input[pygame.K_DOWN] or user_input[pygame.K_s]
        )
        
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
                self.velocity.y = min(
                    self.velocity.y + self.drift_speed,
                    self.max_drift_speed
                )
        
        # Speed limit
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Steering
        turn_speed = self.rotation_speed * (
            0.2 + 0.8 * (self.velocity.length() / self.max_speed)
        )
        
        if user_input[pygame.K_LEFT] or user_input[pygame.K_a]:
            self.direction -= turn_speed
        if user_input[pygame.K_RIGHT] or user_input[pygame.K_d]:
            self.direction += turn_speed
        
        self.direction %= 360
        self.pos += self.velocity
        self.image = pygame.transform.rotate(self.original_image,
                                             -self.direction)
        self.rect = self.image.get_rect(center=self.pos)

        collision = self.check_road_collision(background)
        
        if any(collision.values()):  # If any collision occurred
            if collision['left'] or collision['right']:
                self.velocity.x = 0
                if collision['left']:
                    self.pos.x += 2
                else:
                    self.pos.x -= 2
            
            if collision['top'] or collision['bottom']:
                self.velocity.y = 0
                if collision['top']:
                    self.pos.y += 2
                else:
                    self.pos.y -= 2
            
            self.image = pygame.transform.rotate(self.original_image,
                                                 -self.direction)
            self.rect = self.image.get_rect(center=self.pos)
    
    def keep_on_screen(self):
        car_rect = self.image.get_rect(center=self.pos)
        if car_rect.left < 0:
            self.pos.x -= car_rect.left
        if car_rect.right > SCREEN_WIDTH:
            self.pos.x -= (car_rect.right - SCREEN_WIDTH)
        if car_rect.top < 0:
            self.pos.y -= car_rect.top
        if car_rect.bottom > SCREEN_HEIGHT:
            self.pos.y -= (car_rect.bottom - SCREEN_HEIGHT)
    
    def check_road_collision(self, background):
        car_rect = self.image.get_rect(center=self.pos)
        
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
        
        collision_info = {
            'left': False,
            'right': False,
            'top': False,
            'bottom': False
        }
        
        for point_x, point_y in check_points:
            tile_x = int(point_x // TILE_SIZE)
            tile_y = int(point_y // TILE_SIZE)
            
            if 0 <= tile_y < len(background.road_map) and \
               0 <= tile_x < len(background.road_map[0]):
                if background.road_map[tile_y][tile_x] == 0:
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
    
    def get_bottom(self):
        return self.rect.bottom


class AiCar:
    def __init__(self, lane):
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.color = AI_HITBOX_COLOR
        self.color_name = AI_CAR_COLORS[lane]
        self.image = pygame.image.load(
            f"ai_{self.color_name}_car.png"
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image,
                                            (self.width, self.length))
        self.original_image = self.image.copy()
        self.speed = random.uniform(1, 7)
        self.lane = lane
        self.boost_multiplier = 2.0
        self.boost_duration = 0
        self.max_boost_duration = 60
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.length)
        self.reset_car()
        self.passed = False  # Track if this car has been scored
        
    def reset_car(self):
        road_center_x = SCREEN_WIDTH // 2
        road_left = road_center_x - (ROAD_WIDTH * TILE_SIZE) // 2
        
        lane_center = road_left + (self.lane * LANE_WIDTH) + (LANE_WIDTH // 2)
        min_x = lane_center - (LANE_WIDTH // 2) + (self.width // 2)
        max_x = lane_center + (LANE_WIDTH // 2) - (self.width // 2)
        self.x = random.uniform(min_x, max_x)
        self.y = random.randint(-SCREEN_HEIGHT * 2, -CAR_LENGTH)
        self.speed = random.uniform(1.5, 6.5)
            
    def update(self, scroll_speed, braking):
        prev_top = self.rect.top
        
        if braking:
            self.y -= self.speed
        else:
            self.y += self.speed + scroll_speed * 0.1
        
        self.rect.y = self.y
        self.rect.x = self.x
        
        if not self.passed and player_bottom < self.rect.top:
            self.passed = True
            return True
        
        if self.y > SCREEN_HEIGHT:
            self.reset_car()
        
        return False
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Background:
    def __init__(self):
        self.height = SCREEN_HEIGHT
        self.width = SCREEN_WIDTH
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.scroll_y = 0
        self.speed = 0
        self.max_speed = 30
        self.acceleration = 0.1
        self.deceleration = 0.2
        self.brake_strength = BRAKE_STRENGTH
        
        self.road_map = self.generate_road_map()
        self.draw_background()

    def generate_road_map(self):
        rows = math.ceil(self.height / TILE_SIZE)  
        columns = math.ceil(self.width / TILE_SIZE)
        background = [[0 for _ in range(columns)] for _ in range(rows)]

        center_x = columns // 2
        for y in range(rows):
            for dx in range(-ROAD_WIDTH//2, ROAD_WIDTH//2 + 1):
                if 0 <= center_x + dx < columns:
                    background[y][center_x + dx] = 1
            
        return background
        
    def draw_background(self):
        self.background.fill(GRASS_COLOR)
        
        for y in range(len(self.road_map)):
            for x in range(len(self.road_map[0])):
                if self.road_map[y][x] == 1:
                    pygame.draw.rect(
                        self.background, 
                        ROAD_COLOR, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE,
                         TILE_SIZE)
                    )
        
        self.draw_road_markings()
    
    def update(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.brake_strength, 0)
        else:
            self.speed = max(self.speed - self.deceleration, 0)
        
        self.scroll_y += self.speed
        self.scroll_y %= (TILE_SIZE * 4)
        self.draw_background()
    
    def draw_road_markings(self):
        road_center_x = self.width // 2
        road_half_width = (ROAD_WIDTH * TILE_SIZE) // 2
        
        line_width = 4
        line_length = TILE_SIZE * 2
        line_gap = TILE_SIZE * 2
        
        lane_width = (ROAD_WIDTH * TILE_SIZE) / 4
        for lane_divider in [-1, 0, 1]:
            line_x = road_center_x + (lane_divider * lane_width)
            for y in range(-int(self.scroll_y), self.height, line_length +
                                                             line_gap):
                pygame.draw.rect(
                    self.background,
                    WHITE,
                    (line_x - line_width//2, y, line_width, line_length)
                )
        
        pygame.draw.rect(
            self.background,
            WHITE,
            (road_center_x - road_half_width, 0, line_width, self.height)
        )
        pygame.draw.rect(
            self.background,
            WHITE,
            (road_center_x + road_half_width - line_width, 0, line_width
             , self.height)
        )
    
    def draw(self, screen):
        screen.blit(self.background, (0, 0))


def draw_score(screen):
    score_text = SMALL_FONT.render(f"Score: {score}", True, WHITE)
    pygame.draw.rect(
        screen, 
        GRASS_COLOR, 
        (10, 10, score_text.get_width() + 20,
         score_text.get_height() + 10)
    )
    screen.blit(score_text, (20, 15))


def show_end_screen():
    end_screen = pygame.image.load("end_screen.png").convert_alpha()
    end_screen = pygame.transform.scale(end_screen, (SCREEN_WIDTH,
                                                     SCREEN_HEIGHT))
    screen.blit(end_screen, (0, 0))

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                             pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    game_over_text = FONT.render("GAME OVER", True, WHITE)
    screen.blit(
        game_over_text, 
        (SCREEN_WIDTH//2 - game_over_text.get_width()//2,
         SCREEN_HEIGHT//2 - 100)
    )

    high_score_text = SMALL_FONT.render(f"High Score: {high_score}",
                                        True, WHITE)
    screen.blit(
        high_score_text, 
        (SCREEN_WIDTH//2 - high_score_text.get_width()//2,
         SCREEN_HEIGHT//2)
    )

    score_text = SMALL_FONT.render(f"Your Score: {score}",
                                   True, WHITE)
    screen.blit(
        score_text, 
        (SCREEN_WIDTH//2 - score_text.get_width()//2,
         SCREEN_HEIGHT//2 + 50)
    )
    
    restart_text = SMALL_FONT.render("Press SPACE to restart",
                                     True, WHITE)
    screen.blit(
        restart_text, 
        (SCREEN_WIDTH//2 - restart_text.get_width()//2,
         SCREEN_HEIGHT//2 + 100)
    )
    
    quit_text = SMALL_FONT.render("Press Q to Quit to Menu",
                                  True, WHITE)
    screen.blit(
        quit_text, 
        (SCREEN_WIDTH//2 - quit_text.get_width()//2,
         SCREEN_HEIGHT//2 + 250)
    )
    
    pygame.display.update()


def load_high_score():
    try:
        with open("Hi_score.txt", "r") as hi_score_file:
            value = hi_score_file.read()
    except IOError:
        with open("Hi_score.txt", 'w') as hi_score_file:
            hi_score_file.write("0")
        value = "0"
    return value


def update_high_score(current_score, high_score):
    if int(current_score) > int(high_score):
        return current_score
    return high_score


def save_high_score(high_score):
    with open("Hi_score.txt", 'w') as high_score_file:
        high_score_file.write(str(high_score))


menu_items = [
    {"text": "Start Game", "action": GAME_ACTIVE},
    {"text": "High Scores", "action": HIGH_SCORES}, 
    {"text": "Tips/instructions", "action": INSTRUCTIONS},
    {"text": "Quit", "action": "quit"}
]


def draw_menu():
    menu_image = pygame.image.load("menu_background.png").convert_alpha()
    menu_image = pygame.transform.scale(menu_image, (SCREEN_WIDTH,
                                                     SCREEN_HEIGHT))
    screen.blit(menu_image, (0, 0))

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                             pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont(None, MENU_TITLE_SIZE)
    title_text = title_font.render("Car Ricers", True,
                                   MENU_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2,
                                             SCREEN_HEIGHT//4))
    screen.blit(title_text, title_rect)
    
    font = pygame.font.SysFont(None, MENU_FONT_SIZE)
    mouse_pos = pygame.mouse.get_pos()
    
    for i, item in enumerate(menu_items):
        is_hovered = (
            SCREEN_WIDTH//2 - 100 <= mouse_pos[0] <= SCREEN_WIDTH//2 + 100 and
            SCREEN_HEIGHT//2 + i*(MENU_FONT_SIZE + MENU_ITEM_PADDING)
            <= mouse_pos[1] <=
            SCREEN_HEIGHT//2 + i*(MENU_FONT_SIZE + MENU_ITEM_PADDING) +
            MENU_FONT_SIZE
        )
        
        text = font.render(
            item["text"], 
            True, 
            MENU_HOVER_COLOR if is_hovered else MENU_COLOR
        )
        
        text_rect = text.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i*(MENU_FONT_SIZE +
                                                           MENU_ITEM_PADDING))
        )
        screen.blit(text, text_rect)


def draw_high_scores():
    high_score_image = pygame.image.load("high_score_back.png").convert_alpha()
    high_score_image = pygame.transform.scale(
        high_score_image, 
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    screen.blit(high_score_image, (0, 0))

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                             pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont(None, MENU_TITLE_SIZE)
    title_text = title_font.render("HIGH SCORES", True,
                                   MENU_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2,
                                             SCREEN_HEIGHT//4))
    screen.blit(title_text, title_rect)
    
    font = pygame.font.SysFont(None, MENU_FONT_SIZE)
    score_text = font.render(f"Best: {high_score}",
                             True, MENU_COLOR)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2,
                                             SCREEN_HEIGHT//2))
    screen.blit(score_text, score_rect)
    
    back_font = pygame.font.SysFont(None, MENU_FONT_SIZE - 10)
    back_text = back_font.render("Press ESC to return to menu",
                                 True, MENU_COLOR)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2,
                                           SCREEN_HEIGHT - 50))
    screen.blit(back_text, back_rect)


def draw_instructions():
    instruction_image = pygame.image.load("instruction_background."
                                          "png").convert_alpha()
    instruction_image = pygame.transform.scale(
        instruction_image, 
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    screen.blit(instruction_image, (0, 0))

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                             pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont(None, MENU_TITLE_SIZE)
    title_text = title_font.render("TIPS & INSTRUCTIONS",
                                   True, MENU_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2,
                                             SCREEN_HEIGHT//8))
    screen.blit(title_text, title_rect)
    
    instruction_lines = [
        "CONTROLS:",
        "- W or UP ARROW to accelerate",
        "- S or DOWN ARROW to brake/reverse",
        "- A or LEFT ARROW to steer left",
        "- D or RIGHT ARROW to steer right",
        "",
        "GAMEPLAY TIPS:",
        "- Avoid colliding with other cars",
        "- Braking allows car to go ahead of you but will not be recounted",
        "- Higher speeds make steering more sensitive",
        "- Score points by passing other vehicles",
        "- Holding down on the accelerator button is not recommended",
        "",
        "OBJECTIVE:",
        "- Get the highest score possible by passing",
        " as many cars as you can without crashing!"
    ]
    
    font = pygame.font.SysFont(None, MENU_FONT_SIZE - 10)
    line_height = font.get_linesize()
    start_y = SCREEN_HEIGHT // 4
    
    for i, line in enumerate(instruction_lines):
        if not line.strip():
            start_y += line_height // 2
            continue
            
        if line.endswith(":"):
            text = font.render(line, True, MENU_HOVER_COLOR)
        else:
            text = font.render(line, True, MENU_COLOR)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, start_y + i *
                                          line_height))
        screen.blit(text, text_rect)
    
    back_font = pygame.font.SysFont(None, MENU_FONT_SIZE - 10)
    back_text = back_font.render("Press ESC to return to menu",
                                 True, MENU_COLOR)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2,
                                           SCREEN_HEIGHT - 25))
    screen.blit(back_text, back_rect)


def handle_menu_click(pos):
    global current_state, score, background, player, ai_cars, high_score
    
    for i, item in enumerate(menu_items):
        if (SCREEN_WIDTH//2 - 100 <= pos[0] <= SCREEN_WIDTH//2 + 100 and
            SCREEN_HEIGHT//2 + i*(MENU_FONT_SIZE + MENU_ITEM_PADDING)
                <= pos[1] <=
            SCREEN_HEIGHT//2 + i*(MENU_FONT_SIZE + MENU_ITEM_PADDING) +
                MENU_FONT_SIZE):
            
            if item["action"] == "quit":
                save_high_score(high_score)
                pygame.quit()
                sys.exit()
            else:
                current_state = item["action"]
                
                if current_state == GAME_ACTIVE:
                    score = 0
                    background = Background()
                    player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOR)
                    ai_cars = [AiCar(i) for i in range(4)]


# Create game objects
background = Background()
player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOR)
ai_cars = [AiCar(i) for i in range(4)]
high_score = load_high_score()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score(high_score)
            pygame.quit()
            sys.exit()
            
        if current_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            handle_menu_click(event.pos)
            
        if current_state == GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_state = GAME_ACTIVE
                score = 0
                background = Background()
                player = Player(CAR_WIDTH, CAR_LENGTH, PLAYER_COLOR)
                ai_cars = [AiCar(i) for i in range(4)]
            elif event.key == pygame.K_q:
                current_state = MENU
                
        if (current_state in (HIGH_SCORES, INSTRUCTIONS) and event.type ==
                pygame.KEYDOWN):
            if event.key == pygame.K_ESCAPE:
                current_state = MENU
    
    if current_state == MENU:
        draw_menu()
    elif current_state == HIGH_SCORES:
        draw_high_scores()
    elif current_state == INSTRUCTIONS:
        draw_instructions()
    elif current_state == GAME_ACTIVE:
        keys = pygame.key.get_pressed()
        
        background.update(keys)
        player.movement(keys)
        player.keep_on_screen()

        if score_increment_cooldown > 0:
            score_increment_cooldown -= 1

        player_bottom = player.get_bottom()
        braking = keys[pygame.K_DOWN] or keys[pygame.K_s]

        for car in ai_cars:
            prev_top = car.rect.top
            
            if braking:
                car.y -= car.speed
            else:
                car.y += car.speed + background.speed * 0.1
            
            car.rect.y = car.y
            car.rect.x = car.x
            
            if not car.passed and player_bottom < car.rect.top:
                car.passed = True
                if score_increment_cooldown == 0:
                    score += 1
                    score_increment_cooldown = SCORE_COOLDOWN
            
            if car.y > SCREEN_HEIGHT:
                car.reset_car()
                car.passed = False
            
            if player.rect.colliderect(car.rect):
                current_state = GAME_OVER
                high_score = update_high_score(score, high_score)
                save_high_score(high_score)
        
        background.draw(screen)
        for car in ai_cars:
            car.draw(screen)
        player.draw(screen)
        draw_score(screen)
        
    elif current_state == GAME_OVER:
        show_end_screen()
        
    pygame.display.update()
    clock.tick(60)
