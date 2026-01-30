import pygame
import random
import sys

columns = 10
rows = 20
block_size = 30
ui_height = 100
width = columns * block_size
height = (rows * block_size) + ui_height 

score = 0
high_score = 0
game_over = False
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

shapes = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    'S': [[(1, 1), (2, 1), (0, 2), (1, 2)], [(1, 0), (1, 1), (2, 1), (2, 2)]],
    'Z': [[(0, 1), (1, 1), (1, 2), (2, 2)], [(2, 0), (1, 1), (2, 1), (1, 2)]],
    'J': [[(0, 1), (1, 1), (2, 1), (2, 2)], [(1, 0), (1, 1), (1, 2), (0, 2)], [(0, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (2, 0), (1, 1), (1, 2)]],
    'L': [[(0, 1), (1, 1), (2, 1), (0, 2)], [(0, 0), (1, 0), (1, 1), (1, 2)], [(2, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (1, 2), (2, 2)]],
    'T': [[(0, 1), (1, 1), (2, 1), (1, 2)], [(1, 0), (0, 1), (1, 1), (1, 2)], [(1, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (2, 1), (1, 2)]]
}

shape_colors = {
    'I': (0, 255, 255), 'O': (255, 255, 0), 'S': (0, 255, 0),
    'Z': (255, 0, 0), 'J': (0, 0, 255), 'L': (255, 165, 0), 'T': (128, 0, 128)
}

class Piece:
    """
    Represents a single Tetris piece (Tetromino).
     Attributes:
        x (int): Horizontal grid position.
        y (int): Vertical grid position.
        shape (str): The key from the shapes dictionary.
        color (3-tuple): RGB color of the piece (taken from the shape_colors dicitonary).
        rotation (int): Current rotation index.
    """
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shape]
        self.rotation = 0

    def get_offsets(self):
        """Returns the local block offsets for the current rotation."""
        return shapes[self.shape][self.rotation % len(shapes[self.shape])]

    def draw(self, surface, offset_y=ui_height):
        """Renders the piece to the provided surface with a vertical UI offset."""
        for dx, dy in self.get_offsets():
            px, py = (self.x + dx) * block_size, (self.y + dy) * block_size + offset_y
            pygame.draw.rect(surface, self.color, (px, py, block_size, block_size))
            pygame.draw.rect(surface, white, (px, py, block_size, block_size), 1)

def draw_next(surface, piece):
    """Draws the 'Next Piece' preview in the top-right of the UI."""
    label = label_font.render('NEXT', True, white)
    surface.blit(label, (width - 80, 10))
    for dx, dy in piece.get_offsets():
        px = (width - 85) + (dx * 20)
        py = 35 + (dy * 20)
        pygame.draw.rect(surface, piece.color, (px, py, 20, 20))
        pygame.draw.rect(surface, white, (px, py, 20, 20), 1)

def draw_hold(surface, piece):
    """Draws the 'Hold Piece' preview in the top-left of the UI."""
    label = label_font.render('HOLD', True, white)
    surface.blit(label, (20, 10)) 
    for dx, dy in piece.get_offsets():
        px = 25 + (dx * 20)
        py = 35 + (dy * 20)
        pygame.draw.rect(surface, piece.color, (px, py, 20, 20))
        pygame.draw.rect(surface, white, (px, py, 20, 20), 1)

def valid_space(piece, grid):
    """Checks if the piece's current position is within bounds and not colliding."""
    for dx, dy in piece.get_offsets():
        new_x, new_y = piece.x + dx, piece.y + dy
        if not (0 <= new_x < columns and new_y < rows):
            return False
        if new_y >= 0 and grid[new_y][new_x] != 0:
            return False
    return True

def clear_rows(grid):
    """Identifies full rows, removes them, and updates the global score."""
    global score
    full_rows = [i for i, row in enumerate(grid) if 0 not in row]
    count = 1
    for row_index in full_rows:
        del grid[row_index]
        grid.insert(0, [0 for _ in range(columns)])
        score += 100 * count
        count += 1

def draw_grid_lines(surface):
    """Draws the static grid lines on the board."""
    for r in range(rows + 1):
        pygame.draw.line(surface, gray, (0, r * block_size + ui_height), (width, r * block_size + ui_height))
    for c in range(columns + 1):
        pygame.draw.line(surface, gray, (c * block_size, ui_height), (c * block_size, height))

def draw_locked_blocks(surface, grid):
    """Draws all blocks that have already landed and are part of the grid."""
    for y, row in enumerate(grid):
        for x, cell_color in enumerate(row):
            if cell_color != 0:
                px, py = x * block_size, y * block_size + ui_height
                pygame.draw.rect(surface, cell_color, (px, py, block_size, block_size))
                pygame.draw.rect(surface, white, (px, py, block_size, block_size), 1)

def draw_game_over(surface):
    """Draws the Game Over screen."""
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    surface.blit(overlay, (0, 0))
    msg = score_font.render('GAME OVER', True, (255, 0, 0))
    retry_msg = label_font.render('Press "R" to Restart', True, white)
    score_msg = label_font.render(f'Current score: {score}', True, white)
    high_score_msg = label_font.render(f'High score: {high_score}', True, white)
    surface.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 50))
    surface.blit(score_msg, (width // 2 - score_msg.get_width() // 2, height // 2))
    surface.blit(high_score_msg, (width // 2 - high_score_msg.get_width() // 2, height // 2 + 50))
    surface.blit(retry_msg, (width // 2 - retry_msg.get_width() // 2, height // 2 + 100))

def reset_game():
    """Resets the game state."""
    global grid, current_piece, next_piece, hold_piece, score, game_over, fall_speed, hold_used
    grid = [[0 for _ in range(columns)] for _ in range(rows)]
    current_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    next_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    hold_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    score = 0
    fall_speed = 500
    game_over = False
    hold_used = 0

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
score_font = pygame.font.SysFont('Roboto', 40, bold=True)
label_font = pygame.font.SysFont('Roboto', 20, bold=True)


reset_game()

fall_time = 0
running = True

while running:
    dt = clock.tick(60)
    
    if not game_over:
        fall_time += dt
        if fall_time > fall_speed:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                for dx, dy in current_piece.get_offsets():
                    grid[current_piece.y + dy][current_piece.x + dx] = current_piece.color
                
                clear_rows(grid)
                
                current_piece = next_piece
                next_piece = Piece(3, 0, random.choice(list(shapes.keys())))
                hold_used = 0
                
                if not valid_space(current_piece, grid):
                    if score > high_score:
                        high_score = score
                    game_over = True
                if fall_speed > 200:
                    fall_speed -= 5
            fall_time = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_ESCAPE:
                running = False
                
            if not game_over:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid): current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid): current_piece.x -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid): current_piece.rotation -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid): current_piece.y -= 1
                if event.key == pygame.K_e:
                    if not hold_used:
                        current_piece, hold_piece = hold_piece, current_piece
                        hold_piece.x, hold_piece.y, hold_piece.rotation = 3, 0, 0
                        hold_used = 1
                if event.key == pygame.K_s:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

    screen.fill(black)
    draw_locked_blocks(screen, grid)
    draw_grid_lines(screen)
    current_piece.draw(screen)
    
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, width, ui_height))
    lbl_score = label_font.render('SCORE', True, gray)
    screen.blit(lbl_score, (width // 2 - 20, 15))
    score_surf = score_font.render(f'{score}', True, white)
    screen.blit(score_surf, (width // 2 - (score_surf.get_width() // 2), 35))
    
    draw_next(screen, next_piece)
    draw_hold(screen, hold_piece)
    pygame.draw.line(screen, (100, 100, 100), (0, ui_height), (width, ui_height), 2)
    
    if game_over:
        draw_game_over(screen)
        
    pygame.display.flip()

pygame.quit()
sys.exit()