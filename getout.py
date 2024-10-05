import pygame
import sys
import random
import time
import os

# Function to get resource path (for PyInstaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize Pygame
pygame.init()

# Set up the game icon
icon = pygame.image.load(resource_path('logo.ico'))
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (255, 0, 0)
END_COLOR = (0, 255, 0)  
PAUSE_COLOR = (0, 0, 255)

# Fonts
FONT = pygame.font.Font(resource_path("fonts/Montserrat-Light.ttf"), 40)
SMALL_FONT = pygame.font.Font(resource_path("fonts/Montserrat-Light.ttf"), 24)

# Set up display for 1366x768 resolution
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("GET OUT!")

# Directions for maze generation
DIRS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

# Maze constants
CELL_SIZE = 50
WALL_THICKNESS = 2  # Thickness of maze lines
BORDER_THICKNESS = 6  # Thickness of the border (now thicker than maze lines)

def generate_maze(width, height):
    maze = [[{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(width)] for _ in range(height)]
    visited = [[False for _ in range(width)] for _ in range(height)]

    def carve_passages(cx, cy):
        directions = list(DIRS.keys())
        random.shuffle(directions)
        visited[cy][cx] = True

        for direction in directions:
            nx, ny = cx + DIRS[direction][0], cy + DIRS[direction][1]
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                maze[cy][cx][direction] = False
                # Remove opposite wall
                opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
                maze[ny][nx][opposite[direction]] = False
                carve_passages(nx, ny)

    carve_passages(0, 0)
    return maze

def draw_maze(maze, width, height, maze_x_offset, maze_y_offset):
    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            px, py = x * CELL_SIZE + maze_x_offset, y * CELL_SIZE + maze_y_offset
            if cell['N']:
                pygame.draw.line(screen, BLACK, (px, py), (px + CELL_SIZE, py), WALL_THICKNESS)
            if cell['S']:
                pygame.draw.line(screen, BLACK, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE), WALL_THICKNESS)
            if cell['E']:
                pygame.draw.line(screen, BLACK, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE), WALL_THICKNESS)
            if cell['W']:
                pygame.draw.line(screen, BLACK, (px, py), (px, py + CELL_SIZE), WALL_THICKNESS)

def home_screen():
    screen.fill(WHITE)
    title = FONT.render("GET OUT!", True, BLACK)
    easy_text = FONT.render("1. Easy", True, BLACK)
    medium_text = FONT.render("2. Medium", True, BLACK)
    hard_text = FONT.render("3. Hard", True, BLACK)
    quit_text = FONT.render("Q. Quit", True, BLACK)
    
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
    screen.blit(easy_text, (SCREEN_WIDTH//2 - easy_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
    screen.blit(medium_text, (SCREEN_WIDTH//2 - medium_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(hard_text, (SCREEN_WIDTH//2 - hard_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 120))
    
    pygame.display.flip()

def get_difficulty():
    while True:
        home_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'Easy'
                elif event.key == pygame.K_2:
                    return 'Medium'
                elif event.key == pygame.K_3:
                    return 'Hard'
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def display_timer(time_left):
    timer_text = SMALL_FONT.render(f"Time Left: {time_left//60}:{time_left%60:02d}", True, BLACK)
    screen.blit(timer_text, (10, 10))

def draw_buttons():
    pause_button = SMALL_FONT.render("Pause (P)", True, BLACK)
    home_button = SMALL_FONT.render("Home (H)", True, BLACK)
    screen.blit(pause_button, (SCREEN_WIDTH // 2 - pause_button.get_width() // 2, 10))
    screen.blit(home_button, (SCREEN_WIDTH - home_button.get_width() - 10, 10))

def pause_game():
    pause_text = FONT.render("Paused", True, PAUSE_COLOR)
    screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))
    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

def main_game(difficulty):
    # Set maze size and timer based on difficulty
    if difficulty == 'Easy':
        maze_width, maze_height = 15, 15
        time_limit = 300  # 5 minutes
    elif difficulty == 'Medium':
        maze_width, maze_height = 25, 25
        time_limit = 600  # 10 minutes
    else:
        maze_width, maze_height = 35, 35
        time_limit = 900  # 15 minutes

    global CELL_SIZE
    screen_width, screen_height = pygame.display.get_surface().get_size()

    # Calculate offsets to position the maze in the center of the screen
    CELL_SIZE = min((screen_width - 100) // maze_width, (screen_height - 150) // maze_height)
    maze_x_offset = (screen_width - maze_width * CELL_SIZE) // 2
    maze_y_offset = (screen_height - maze_height * CELL_SIZE) // 2 + 25  # Add some space for the top UI

    maze = generate_maze(maze_width, maze_height)
    player_x, player_y = 0, 0  # Start position
    end_x, end_y = maze_width - 1, maze_height - 1  # End position

    clock = pygame.time.Clock()
    start_time = time.time()

    paused = False
    move_cooldown = 0.2  # Cooldown time in seconds
    last_move_time = 0

    while True:
        clock.tick(60)  # 60 FPS
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_left = time_limit - int(elapsed_time)

        if time_left <= 0:
            display_timer(0)
            pygame.display.flip()
            win_screen(difficulty, victory=False)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused  # Toggle pause state
                    if paused:
                        pause_game()
                    start_time = current_time - elapsed_time  # Adjust timer after pause
                if event.key == pygame.K_h:
                    return  # Go back to home screen

        if not paused and current_time - last_move_time >= move_cooldown:
            keys = pygame.key.get_pressed()
            current_cell = maze[player_y][player_x]
            moved = False
            
            # Check for both arrow keys and WASD
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and not current_cell['N'] and player_y > 0:
                player_y -= 1
                moved = True
            elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not current_cell['S'] and player_y < maze_height - 1:
                player_y += 1
                moved = True
            elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not current_cell['W'] and player_x > 0:
                player_x -= 1
                moved = True
            elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not current_cell['E'] and player_x < maze_width - 1:
                player_x += 1
                moved = True

            if moved:
                last_move_time = current_time

        # Check for win
        if player_x == end_x and player_y == end_y:
            win_screen(difficulty)
            return

        # Draw everything
        screen.fill(WHITE)
        
        # Draw the thicker border
        pygame.draw.rect(screen, BLACK, (maze_x_offset - BORDER_THICKNESS // 2, 
                                         maze_y_offset - BORDER_THICKNESS // 2, 
                                         maze_width * CELL_SIZE + BORDER_THICKNESS, 
                                         maze_height * CELL_SIZE + BORDER_THICKNESS), BORDER_THICKNESS)
        
        draw_maze(maze, maze_width, maze_height, maze_x_offset, maze_y_offset)
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x * CELL_SIZE + CELL_SIZE//4 + maze_x_offset, 
                                                player_y * CELL_SIZE + CELL_SIZE//4 + maze_y_offset, 
                                                CELL_SIZE//2, CELL_SIZE//2))
        pygame.draw.rect(screen, END_COLOR, (end_x * CELL_SIZE + maze_x_offset, 
                                             end_y * CELL_SIZE + maze_y_offset, 
                                             CELL_SIZE, CELL_SIZE))  # Green square at the endpoint

        # Draw UI elements
        display_timer(time_left)
        draw_buttons()

        pygame.display.flip()

def win_screen(difficulty, victory=True):
    screen.fill(WHITE)
    if victory:
        msg = FONT.render("You Escaped!", True, BLACK)
    else:
        msg = FONT.render("Time's Up!", True, BLACK)

    retry = FONT.render("Press R to Retry or Q to Quit", True, BLACK)
    screen.blit(msg, (screen.get_width()//2 - msg.get_width()//2, screen.get_height()//3))
    screen.blit(retry, (screen.get_width()//2 - retry.get_width()//2, screen.get_height()//2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main_game(difficulty)
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def game_loop():
    pygame.display.toggle_fullscreen()
    while True:
        difficulty = get_difficulty()
        main_game(difficulty)

if __name__ == "__main__":
    game_loop()