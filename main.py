import pygame
import random
import asyncio
import math

# Initialize Pygame with minimal settings
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
BARBIE_SIZE = (50, 70)
BOOK_SIZE = (40, 30)
WITCH_SIZE = (40, 40)
BOULDER_SIZE = 40
GROUND_HEIGHT = 50

# Colors
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
LIGHT_PINK = (255, 223, 228)

# Create window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Barbie Book Catcher")

# Fast image loading
def load_image(path, size):
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(PINK)
        return surf

# Load images immediately
barbie_head = load_image("barbie_head.png", BARBIE_SIZE)
witch_image = load_image("witch.png", WITCH_SIZE)
book_vertical = load_image("book_vertical.png", BOOK_SIZE)
book_horizontal = load_image("book_horizontal.png", BOOK_SIZE)

# Game variables
barbie_x = WINDOW_WIDTH // 2
barbie_y = WINDOW_HEIGHT - GROUND_HEIGHT - BARBIE_SIZE[1]
velocity_y = 0
gravity = 0.8
jump_count = 2
score = 0
level = 1
game_state = "rules"
base_speed = 4

# Game objects
books = []
witches = []
boulders = []
stacked_books = []

# Mobile controls
BUTTON_SIZE = 60
LEFT_BUTTON = pygame.Rect(10, WINDOW_HEIGHT - 90, BUTTON_SIZE, BUTTON_SIZE)
RIGHT_BUTTON = pygame.Rect(80, WINDOW_HEIGHT - 90, BUTTON_SIZE, BUTTON_SIZE)
JUMP_BUTTON = pygame.Rect(WINDOW_WIDTH - 70, WINDOW_HEIGHT - 90, BUTTON_SIZE, BUTTON_SIZE)

def draw_rules():
    screen.fill(LIGHT_PINK)
    
    # Draw title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render("Barbie Book Catcher", True, PURPLE)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))

    # Draw Barbie and books illustration
    screen.blit(barbie_head, (WINDOW_WIDTH//2 - BARBIE_SIZE[0]//2, 100))
    screen.blit(book_horizontal, (WINDOW_WIDTH//2 - BOOK_SIZE[0]//2, 90))
    screen.blit(witch_image, (WINDOW_WIDTH//2 + 80, 100))

    # Draw rules
    font = pygame.font.Font(None, 32)
    rules = [
        "How to Play:",
        "",
        "→ Stack 5 books to complete level",
        "→ Use arrows or buttons to move",
        "→ Double jump to avoid boulders",
        "→ Avoid the witches!",
        "→ Books stack automatically",
        "→ Speed increases each level",
        "",
        "Tap or Click to Start!"
    ]

    y_pos = 220
    for rule in rules:
        if rule.startswith("→"):
            color = PURPLE
        else:
            color = BLACK
        text = font.render(rule, True, color)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
        y_pos += 35

    # Draw decorative elements
    pygame.draw.rect(screen, GOLD, (20, 40, WINDOW_WIDTH-40, 3))
    pygame.draw.rect(screen, GOLD, (20, WINDOW_HEIGHT-40, WINDOW_WIDTH-40, 3))

def reset_game():
    global barbie_x, barbie_y, velocity_y, jump_count, score, books, witches, boulders, stacked_books
    barbie_x = WINDOW_WIDTH // 2
    barbie_y = WINDOW_HEIGHT - GROUND_HEIGHT - BARBIE_SIZE[1]
    velocity_y = 0
    jump_count = 2
    score = 0
    books.clear()
    witches.clear()
    boulders.clear()
    stacked_books.clear()

def handle_jump():
    global velocity_y, jump_count
    if jump_count > 0:
        velocity_y = -12
        jump_count -= 1

def draw_controls():
    for button, text in [
        (LEFT_BUTTON, "←"),
        (RIGHT_BUTTON, "→"),
        (JUMP_BUTTON, "↑")
    ]:
        pygame.draw.rect(screen, PINK, button, border_radius=10)
        font = pygame.font.Font(None, 40)
        text = font.render(text, True, BLACK)
        screen.blit(text, (button.centerx - 10, button.centery - 10))

def check_button(pos):
    x, y = pos
    if LEFT_BUTTON.collidepoint(x, y): return "left"
    if RIGHT_BUTTON.collidepoint(x, y): return "right"
    if JUMP_BUTTON.collidepoint(x, y): return "jump"
    return None

def draw_stacked_books(x, y, wobble=False):
    for i, _ in enumerate(stacked_books):
        offset = 0
        if wobble:
            # Enhanced wobble effect
            time = pygame.time.get_ticks()
            offset = math.sin((time + i * 200) * 0.003) * (i + 1) * 2
            y_offset = math.cos((time + i * 100) * 0.002) * 2
        else:
            y_offset = 0
        screen.blit(book_horizontal, (x + offset, y - (i + 1) * 20 + y_offset))

def get_top_book_height():
    return barbie_y - (len(stacked_books) * 20) if stacked_books else barbie_y

async def main():
    global barbie_x, barbie_y, velocity_y, jump_count, score, level, game_state

    clock = pygame.time.Clock()
    running = True
    spawn_timer = 0

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "rules":
                    game_state = "playing"
                    reset_game()
                elif game_state == "ramp_walk":
                    game_state = "playing"
                    reset_game()
                else:
                    button = check_button(event.pos)
                    if button == "jump":
                        handle_jump()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_state in ["rules", "ramp_walk"]:
                    game_state = "playing"
                    reset_game()
                else:
                    handle_jump()

        # Handle continuous button press
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            pos = pygame.mouse.get_pos()
            button = check_button(pos)
            if button == "left":
                barbie_x = max(barbie_x - 5, 0)
            elif button == "right":
                barbie_x = min(barbie_x + 5, WINDOW_WIDTH - BARBIE_SIZE[0])

        # Game logic
        if game_state == "playing":
            # Keyboard controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                barbie_x = max(barbie_x - 5, 0)
            if keys[pygame.K_RIGHT]:
                barbie_x = min(barbie_x + 5, WINDOW_WIDTH - BARBIE_SIZE[0])

            # Gravity
            velocity_y += gravity
            barbie_y += velocity_y
            if barbie_y > WINDOW_HEIGHT - GROUND_HEIGHT - BARBIE_SIZE[1]:
                barbie_y = WINDOW_HEIGHT - GROUND_HEIGHT - BARBIE_SIZE[1]
                velocity_y = 0
                jump_count = 2

            # Calculate current speed based on level
            current_speed = base_speed + (level - 1) * 0.5

            # Spawn objects
            spawn_timer += 1
            if spawn_timer >= 60:
                spawn_timer = 0
                if random.random() < 0.7:
                    books.append([random.randint(0, WINDOW_WIDTH - BOOK_SIZE[0]), -BOOK_SIZE[1]])
                if random.random() < 0.3:
                    witches.append([random.randint(0, WINDOW_WIDTH - WITCH_SIZE[0]), -WITCH_SIZE[1]])
                if level >= 2 and random.random() < 0.2:
                    side = random.choice([-1, 1])
                    x = WINDOW_WIDTH if side == -1 else -BOULDER_SIZE
                    boulders.append([x, WINDOW_HEIGHT - GROUND_HEIGHT - BOULDER_SIZE, side])

            # Update objects
            for book in books[:]:
                book[1] += current_speed
                if book[1] > WINDOW_HEIGHT:
                    books.remove(book)
                else:
                    # Check collision with top book or Barbie
                    top_height = get_top_book_height()
                    if (barbie_x < book[0] + BOOK_SIZE[0] and 
                        barbie_x + BARBIE_SIZE[0] > book[0] and 
                        top_height - BOOK_SIZE[1] < book[1] + BOOK_SIZE[1] and 
                        top_height > book[1]):
                        books.remove(book)
                        score += 1
                        if len(stacked_books) < 5:  # Changed from 10 to 5
                            stacked_books.append(1)

            for witch in witches[:]:
                witch[1] += current_speed * 0.75
                if witch[1] > WINDOW_HEIGHT:
                    witches.remove(witch)
                elif (barbie_x < witch[0] + WITCH_SIZE[0] and 
                      barbie_x + BARBIE_SIZE[0] > witch[0] and 
                      barbie_y < witch[1] + WITCH_SIZE[1] and 
                      barbie_y + BARBIE_SIZE[1] > witch[1]):
                    game_state = "rules"
                    level = 1

            for boulder in boulders[:]:
                boulder[0] += boulder[2] * current_speed
                if boulder[0] < -BOULDER_SIZE or boulder[0] > WINDOW_WIDTH:
                    boulders.remove(boulder)
                elif (barbie_x < boulder[0] + BOULDER_SIZE and 
                      barbie_x + BARBIE_SIZE[0] > boulder[0] and 
                      barbie_y + BARBIE_SIZE[1] > boulder[1]):
                    game_state = "rules"
                    level = 1

            if score >= 5:  # Changed from 10 to 5
                level += 1
                game_state = "ramp_walk"

        # Drawing
        if game_state == "rules":
            draw_rules()

        elif game_state == "ramp_walk":
            screen.fill(WHITE)
            # Draw ramp walk scene with enhanced wobble
            pygame.draw.rect(screen, GOLD, (50, 300, WINDOW_WIDTH - 100, 20))
            walk_x = 50 + ((pygame.time.get_ticks() // 20) % (WINDOW_WIDTH - 150))
            screen.blit(barbie_head, (walk_x, 220))
            draw_stacked_books(walk_x, 220, wobble=True)
            
            font = pygame.font.Font(None, 48)
            text = font.render(f"Level {level-1} Complete!", True, PURPLE)
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 50))
            text = font.render("Tap to continue", True, PURPLE)
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT - 100))

        else:
            # Draw game elements
            screen.fill(WHITE)
            pygame.draw.rect(screen, BROWN, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))
            screen.blit(barbie_head, (barbie_x, barbie_y))
            draw_stacked_books(barbie_x, barbie_y)

            for book in books:
                screen.blit(book_vertical, (book[0], book[1]))
            for witch in witches:
                screen.blit(witch_image, (witch[0], witch[1]))
            for boulder in boulders:
                pygame.draw.rect(screen, BLACK, (boulder[0], boulder[1], BOULDER_SIZE, BOULDER_SIZE))

            # Draw UI
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Books: {score}/5", True, BLACK)
            level_text = font.render(f"Level: {level}", True, BLACK)
            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (WINDOW_WIDTH - 100, 10))
            
            # Draw jump indicators
            for i in range(jump_count):
                pygame.draw.circle(screen, PURPLE, (30 + i*20, 30), 5)
            
            draw_controls()

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(30)

    pygame.quit()

asyncio.run(main())
