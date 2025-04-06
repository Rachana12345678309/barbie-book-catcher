CREATE A SIMPLE BARBIE GAME IN PYTHON - Create a Python file named barbie_book_catcher.py where:  
1. Barbie moves left/right with arrow keys  
2. Books fall from top  
3. 5 levels with speed *= 1.2 each level  
import pygame
import random
import sys
import asyncio

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Barbie Book Catcher")

# Colors
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Barbie settings
barbie_width = 80
barbie_height = 100
barbie_x = WIDTH // 2 - barbie_width // 2
barbie_y = HEIGHT - barbie_height - 10
barbie_speed = 8

# Book settings
book_width = 40
book_height = 60
book_speed = 3
books = []

# Game settings
score = 0
level = 1
max_level = 5
books_to_next_level = 10
caught_books = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images (placeholder rectangles for now)
barbie_img = pygame.Surface((barbie_width, barbie_height))
barbie_img.fill(PINK)
book_img = pygame.Surface((book_width, book_height))
book_img.fill(BLUE)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def spawn_book():
    x = random.randint(0, WIDTH - book_width)
    return [x, -book_height]

async def main():
    global barbie_x, score, level, caught_books, book_speed, books
    
    running = True
    spawn_timer = 0
    spawn_delay = 1000  # milliseconds
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        
        # Barbie movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and barbie_x > 0:
            barbie_x -= barbie_speed
        if keys[pygame.K_RIGHT] and barbie_x < WIDTH - barbie_width:
            barbie_x += barbie_speed
        
        # Spawn books
        if current_time - spawn_timer > spawn_delay:
            books.append(spawn_book())
            spawn_timer = current_time
        
        # Update book positions and check collisions
        for book in books[:]:
            book[1] += book_speed
            
            # Check if Barbie caught the book
            barbie_rect = pygame.Rect(barbie_x, barbie_y, barbie_width, barbie_height)
            book_rect = pygame.Rect(book[0], book[1], book_width, book_height)
            
            if barbie_rect.colliderect(book_rect):
                books.remove(book)
                score += 10
                caught_books += 1
                
                # Check for level up
                if caught_books >= books_to_next_level and level < max_level:
                    level += 1
                    caught_books = 0
                    book_speed *= 1.2  # Increase speed for next level
            
            # Remove books that fall off screen
            elif book[1] > HEIGHT:
                books.remove(book)
        
        # Drawing
        screen.fill(WHITE)
        
        # Draw Barbie
        barbie_rect = pygame.Rect(barbie_x, barbie_y, barbie_width, barbie_height)
        screen.blit(barbie_img, barbie_rect)
        
        # Draw books
        for book in books:
            book_rect = pygame.Rect(book[0], book[1], book_width, book_height)
            screen.blit(book_img, book_rect)
        
        # Draw UI
        draw_text(f"Score: {score}", font, BLACK, 10, 10)
        draw_text(f"Level: {level}/5", font, BLACK, 10, 50)
        draw_text(f"Books: {caught_books}/{books_to_next_level}", font, BLACK, 10, 90)
        
        # Check for game win
        if level >= max_level and caught_books >= books_to_next_level:
            draw_text("You Win! Barbie is the Book Queen!", font, PINK, WIDTH // 2 - 200, HEIGHT // 2)
            pygame.display.flip()
            await asyncio.sleep(3)
            running = False
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())

def show_ramp_walk():
    """Display a ramp walk animation when Barbie completes a level"""
    # Save current screen state
    old_screen = screen.copy()
    
    # Load ramp walk images (assuming you have these assets)
    try:
        ramp_images = []
        for i in range(1, 6):  # Assuming you have 5 frames of animation
            img = pygame.image.load(f"assets/barbie_ramp_walk_{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(WIDTH * 0.5), int(HEIGHT * 0.7)))
            ramp_images.append(img)
    except pygame.error:
        # Fallback if images don't exist
        ramp_images = [barbie_img] * 5
    
    # Create book stack image for Barbie's head
    book_stack = pygame.Surface((book_width, book_height * 3), pygame.SRCALPHA)
    for i in range(3):
        book_stack.blit(book_img, (0, i * book_height * 0.5))
    
    # Animation loop
    start_time = pygame.time.get_ticks()
    animation_duration = 3000  # 3 seconds
    
    while pygame.time.get_ticks() - start_time < animation_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Calculate animation progress (0.0 to 1.0)
        progress = (pygame.time.get_ticks() - start_time) / animation_duration
        
        # Clear screen with gradient background
        screen.fill(PINK)
        
        # Draw congratulation text
        draw_text(f"Level {level} Complete!", font, BLACK, WIDTH // 2 - 150, 50)
        draw_text(f"+{books_to_next_level * 10} points!", font, BLACK, WIDTH // 2 - 100, 100)
        
        # Draw Barbie walking
        frame_index = int(progress * len(ramp_images)) % len(ramp_images)
        barbie_pose = ramp_images[frame_index]
        
        # Calculate position for walking across screen
        walk_x = int(WIDTH * 0.1 + progress * WIDTH * 0.8)
        walk_y = HEIGHT - barbie_pose.get_height() - 50
        
        # Draw Barbie with books on head
        screen.blit(barbie_pose, (walk_x, walk_y))
        
        # Position books on Barbie's head
        head_offset_x = barbie_pose.get_width() // 2 - book_stack.get_width() // 2
        head_offset_y = -book_stack.get_height() + 20  # Adjust as needed
        screen.blit(book_stack, (walk_x + head_offset_x, walk_y + head_offset_y))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Restore previous screen
    screen.blit(old_screen, (0, 0))
    pygame.display.flip()
    # Note: Python games like this one (using Pygame) cannot be directly hosted on a website
    # They need to be converted to web-compatible technologies like JavaScript
    # Here's code to export instructions for web deployment:
    
    def export_web_instructions():
        """Provides instructions for web deployment of the game"""
        instructions = """
        To host this Pygame game on a website, you'll need to:
        
        Option 1: Use Pygbag (recommended for Pygame)
        1. Install pygbag: pip install pygbag
        2. Create a simple HTML wrapper in the same folder as your game
        3. Run: python -m pygbag gamefile.py
        4. Upload the generated web folder to a hosting service like GitHub Pages, Vercel, or Netlify
        
        Option 2: Convert to JavaScript using Pyodide/Pygame web port
        1. Visit https://pygame-web.github.io/ for documentation
        2. Follow their instructions for porting Pygame to web
        
        Option 3: Rewrite using web technologies
        1. Convert the game to JavaScript using a canvas-based library like Phaser.js
        2. Host the JavaScript version on any web hosting platform
        """
        
        # Print instructions to console
        print(instructions)
        
        # Also save instructions to a file
        with open("web_deployment_instructions.txt", "w") as f:
            f.write(instructions)
        
        return "Instructions saved to 'web_deployment_instructions.txt'"
    
    # Call the function to show deployment options
    export_web_instructions()
    def convert_to_phaser_js():
        """
        Generates a basic Phaser.js template that mimics the Barbie balancing game functionality
        """
        phaser_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Barbie Balancing Game</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.55.2/dist/phaser.min.js"></script>
    <style>
        body { margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f8e1f4; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script>
        class BalancingGame extends Phaser.Scene {
            constructor() {
                super('BalancingGame');
                this.books = 0;
                this.walkSpeed = 5;
                this.gameOver = false;
            }
            
            preload() {
                this.load.image('barbie', 'assets/barbie_pose.png');
                this.load.image('book', 'assets/book.png');
                this.load.image('background', 'assets/background.png');
                // Load other necessary assets
            }
            
            create() {
                // Add background
                this.add.image(400, 300, 'background');
                
                // Add Barbie character
                this.barbie = this.add.sprite(400, 500, 'barbie');
                
                // Create book stack group
                this.bookStack = this.add.group();
                
                // Add UI elements
                this.scoreText = this.add.text(16, 16, 'Books: 0', { fontSize: '32px', fill: '#000' });
                
                // Add keyboard controls
                this.cursors = this.input.keyboard.createCursorKeys();
                
                // Add timer for adding books
                this.time.addEvent({
                    delay: 3000,
                    callback: this.addBook,
                    callbackScope: this,
                    loop: true
                });
            }
            
            addBook() {
                if (this.gameOver) return;
                
                this.books++;
                this.scoreText.setText('Books: ' + this.books);
                
                // Add book to stack
                const bookY = 500 - (this.books * 20);
                const book = this.add.image(this.barbie.x, bookY, 'book');
                this.bookStack.add(book);
                
                // Increase difficulty
                if (this.books > 5) {
                    this.walkSpeed = 7;
                }
                if (this.books > 10) {
                    this.walkSpeed = 9;
                }
                
                // Check for win condition
                if (this.books >= 15) {
                    this.gameOver = true;
                    this.add.text(200, 250, 'YOU WIN!', { fontSize: '64px', fill: '#ff0' });
                }
            }
            
            update() {
                if (this.gameOver) return;
                
                // Handle movement
                if (this.cursors.left.isDown) {
                    this.barbie.x -= this.walkSpeed;
                } else if (this.cursors.right.isDown) {
                    this.barbie.x += this.walkSpeed;
                }
                
                // Keep Barbie within bounds
                this.barbie.x = Phaser.Math.Clamp(this.barbie.x, 50, 750);
                
                // Update book stack positions
                let i = 0;
                this.bookStack.getChildren().forEach(book => {
                    book.x = this.barbie.x;
                    book.y = 500 - ((i + 1) * 20);
                    i++;
                });
                
                // Simple physics - if Barbie moves too fast, books fall
                if (this.books > 3 && 
                    (this.cursors.left.isDown || this.cursors.right.isDown) && 
                    Phaser.Math.Between(0, 100) < this.books) {
                    this.gameOver = true;
                    this.add.text(200, 250, 'BOOKS FELL!', { fontSize: '64px', fill: '#f00' });
                }
            }
        }
        
        const config = {
            type: Phaser.AUTO,
            width: 800,
            height: 600,
            physics: {
                default: 'arcade',
                arcade: {
                    gravity: { y: 300 },
                    debug: false
                }
            },
            scene: [BalancingGame]
        };
        
        const game = new Phaser.Game(config);
    </script>
</body>
</html>
"""
        
        # Save the Phaser.js template to a file
        with open("barbie_game_phaser.html", "w") as f:
            f.write(phaser_template)
        
        print("Phaser.js template saved to 'barbie_game_phaser.html'")
        print("Note: You'll need to create an 'assets' folder with the necessary images.")
        
        return "Phaser.js conversion template created"
    
    # Generate the Phaser.js template
    convert_to_phaser_js()
def launch_game():
    """
    Function to provide instructions on how to run the Phaser.js game
    """
    import webbrowser
    import os
    import http.server
    import socketserver
    import threading
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the HTML file
    html_file = os.path.join(current_dir, "barbie_game_phaser.html")
    
    if not os.path.exists(html_file):
        print("Error: Game file 'barbie_game_phaser.html' not found!")
        return "Game file not found"
    
    # Start a simple HTTP server
    PORT = 8000
    
    def start_server():
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started at http://localhost:{PORT}")
            httpd.serve_forever()
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the game in the default web browser
    game_url = f"http://localhost:{PORT}/barbie_game_phaser.html"
    webbrowser.open(game_url)
    
    print(f"Game launched at: {game_url}")
    print("To stop the server, press Ctrl+C in this terminal")
    
    return game_url

# Launch the game
if __name__ == "__main__":
    game_url = launch_game()
    print(f"You can access the game at: {game_url}")

def get_game_link():
    """
    Returns the URL where the game can be accessed
    """
    import socket
    
    # Get the local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Default port used by the HTTP server
    PORT = 8000
    
    # Generate both localhost and network links
    localhost_link = f"http://localhost:{PORT}/barbie_game_phaser.html"
    network_link = f"http://{local_ip}:{PORT}/barbie_game_phaser.html"
    
    print("\nGame Access Links:")
    print(f"Local access: {localhost_link}")
    print(f"Network access (for other devices): {network_link}")
    print("\nNote: The game server must be running for these links to work.")
    
    return {
        "local": localhost_link,
        "network": network_link
    }
