import pygame
import random
import asyncio
import math

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Barbie Book Catcher")

# Colors
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
BLONDE = (255, 223, 196)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Game variables
barbie_width = 60
barbie_height = 100
barbie_x = SCREEN_WIDTH // 2 - barbie_width // 2
barbie_y = SCREEN_HEIGHT - barbie_height - 10
barbie_speed = 5
barbie_jump = False
jump_height = 100
jump_speed = 10
original_y = SCREEN_HEIGHT - barbie_height - 10

# Book variables
book_width = 40
book_height = 60
book_speed = 2
caught_books = []

# Boulder variables
boulder_size = 40
boulder_speed = 4
boulders = []

# Game state
score = 0
level = 1
books_caught = 0
books_needed = 5
game_over = False
show_rules = True
showing_ramp_walk = False

# Font
font = pygame.font.SysFont(None, 36)

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_rules():
    screen.fill(WHITE)
    draw_text("Barbie Book Catcher - Rules", PINK, 200, 50)
    rules = [
        "1. Catch falling books to score points",
        "2. Each caught book = 3 points",
        "3. Missing a book = -5 points",
        "4. Catch 5 books to complete each level",
        "5. Jump over boulders (UP arrow)",
        "6. Score < 0 = Game Over",
        "",
        "Press SPACE to start!"
    ]
    for i, rule in enumerate(rules):
        draw_text(rule, BLACK, 200, 150 + i*40)

def draw_barbie(x, y):
    # Draw dress
    pygame.draw.polygon(screen, PINK, [
        (x + barbie_width//2, y + 40),
        (x + barbie_width + 10, y + barbie_height),
        (x - 10, y + barbie_height)
    ])
    # Draw hair
    pygame.draw.ellipse(screen, BLONDE, (x - 5, y, barbie_width + 10, 50))
    # Draw hair locks
    for i in range(4):
        wave_x = x + i * 15
        offset = 5 * math.sin(i * 0.8)
        pygame.draw.line(screen, BLONDE, 
                        (wave_x + offset, y + 20),
                        (wave_x + 10, y + 50), 4)

def draw_book(x, y, horizontal=False):
    if horizontal:
        pygame.draw.rect(screen, BROWN, (x, y, 40, 15))
    else:
        pygame.draw.rect(screen, BROWN, (x, y, book_width, book_height))

def draw_boulder(x, y):
    pygame.draw.circle(screen, GRAY, (x + boulder_size//2, y + boulder_size//2), boulder_size//2)

async def show_ramp_walk():
    global showing_ramp_walk
    showing_ramp_walk = True
    scale = 0.5  # Start small (far away)
    progress = 0
    
    for frame in range(180):  # 3 seconds
        screen.fill(WHITE)
        
        # Draw runway
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 20))
        
        # Calculate snake path
        progress += 0.02
        walk_x = SCREEN_WIDTH//2 + math.sin(progress * 6) * 100
        walk_y = SCREEN_HEIGHT//4 + frame * 2
        
        # Increase size as Barbie comes closer
        scale = min(1.5, 0.5 + frame/180)
        current_width = int(barbie_width * scale)
        current_height = int(barbie_height * scale)
        
        # Draw Barbie
        draw_barbie(int(walk_x - current_width//2), 
                   int(walk_y - current_height//2))
        
        # Draw stacked books
        for i in range(len(caught_books)):
            draw_book(walk_x + current_width//2 - 20, 
                     walk_y - 20 - (i * 15),
                     horizontal=True)
        
        draw_text(f"Level {level} Complete!", PINK, SCREEN_WIDTH//2 - 150, 50)
        draw_text(f"Score this level: {score}", PINK, SCREEN_WIDTH//2 - 100, 100)
        
        pygame.display.flip()
        await asyncio.sleep(0.016)
    
    showing_ramp_walk = False

async def main():
    global barbie_x, barbie_y, score, level, books_caught, book_speed, caught_books
    global game_over, show_rules, barbie_jump
    
    running = True
    spawn_timer = 0
    boulder_timer = 0
    spawn_delay = 1500
    boulder_delay = 2000
    falling_books = []
    boulders = []
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if show_rules:
                        show_rules = False
                    elif game_over:
                        game_over = False
                        score = 0
                        level = 1
                        books_caught = 0
                        book_speed = 2
                        caught_books = []
                        falling_books = []
                        boulders = []
                        barbie_y = original_y
                elif event.key == pygame.K_UP and not barbie_jump and not show_rules:
                    barbie_jump = True
        
        screen.fill(WHITE)
        
        if show_rules:
            draw_rules()
        elif game_over:
            draw_text("GAME OVER!", RED, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2)
            draw_text("Press SPACE to play again", BLACK, SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50)
        else:
            # Handle keyboard input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and barbie_x > 0:
                barbie_x -= barbie_speed
            if keys[pygame.K_RIGHT] and barbie_x < SCREEN_WIDTH - barbie_width:
                barbie_x += barbie_speed
            
            # Handle jumping
            if barbie_jump:
                if barbie_y > original_y - jump_height:
                    barbie_y -= jump_speed
                else:
                    barbie_jump = False
            elif barbie_y < original_y:
                barbie_y += jump_speed
                if barbie_y > original_y:
                    barbie_y = original_y
            
            # Spawn books
            if current_time - spawn_timer > spawn_delay:
                falling_books.append([random.randint(0, SCREEN_WIDTH - book_width), -book_height])
                spawn_timer = current_time
            
            # Spawn boulders in level 2+
            if level >= 2 and current_time - boulder_timer > boulder_delay:
                boulder_x = -boulder_size if random.random() < 0.5 else SCREEN_WIDTH
                boulders.append([boulder_x, SCREEN_HEIGHT - boulder_size - 20])
                boulder_timer = current_time
            
            # Draw Barbie
            draw_barbie(barbie_x, barbie_y)
            
            # Draw caught books stack
            for i in range(len(caught_books)):
                draw_book(barbie_x + barbie_width//2 - 20,
                         barbie_y - 20 - (i * 15),
                         horizontal=True)
            
            # Update falling books
            for book in falling_books[:]:
                book[1] += book_speed
                draw_book(book[0], book[1])
                
                # Check collision
                if (barbie_x < book[0] + book_width and 
                    barbie_x + barbie_width > book[0] and 
                    barbie_y < book[1] + book_height and 
                    barbie_y + barbie_height > book[1]):
                    falling_books.remove(book)
                    score += 3
                    books_caught += 1
                    caught_books.append(book)
                    
                    # Level up
                    if books_caught >= books_needed:
                        await show_ramp_walk()
                        level += 1
                        books_caught = 0
                        score = 0  # Reset score for new level
                        book_speed += 0.5
                        caught_books = []
                        falling_books = []
                        boulders = []
                
                # Remove books that fall off screen
                elif book[1] > SCREEN_HEIGHT:
                    falling_books.remove(book)
                    score -= 5
                    if score < 0:
                        game_over = True
            
            # Update boulders
            for boulder in boulders[:]:
                if boulder[0] < SCREEN_WIDTH//2:
                    boulder[0] += boulder_speed
                else:
                    boulder[0] -= boulder_speed
                draw_boulder(boulder[0], boulder[1])
                
                # Check collision with boulder (only if not jumping)
                if not barbie_jump:
                    if (barbie_x < boulder[0] + boulder_size and
                        barbie_x + barbie_width > boulder[0] and
                        barbie_y + barbie_height > boulder[1]):
                        game_over = True
                
                # Remove boulders that go off screen
                if (boulder[0] < -boulder_size or 
                    boulder[0] > SCREEN_WIDTH):
                    boulders.remove(boulder)
            
            # Draw UI
            draw_text(f"Score: {score}", BLACK, 10, 10)
            draw_text(f"Level: {level}", BLACK, 10, 40)
            draw_text(f"Books: {books_caught}/{books_needed}", BLACK, 10, 70)
        
        pygame.display.flip()
        await asyncio.sleep(0.016)

asyncio.run(main())
