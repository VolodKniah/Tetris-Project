import pygame
import random
import sys
import re

COLUMNS = 10
ROWS = 20
BLOCK_SIZE = 30
UI_HEIGHT = 100
WIDTH = COLUMNS * BLOCK_SIZE
HEIGHT = (ROWS * BLOCK_SIZE) + UI_HEIGHT 

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

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

class Game:

    def __init__(self):
        self.high_score = 0
        self.score = 0
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = Piece(3, 0, random.choice(list(shapes.keys())))
        self.next_piece = Piece(3, 0, random.choice(list(shapes.keys())))
        self.hold_piece = Piece(3, 0, random.choice(list(shapes.keys())))
        self.score = 0
        self.fall_speed = 500
        self.game_over = False
        self.hold_used = 0
        self.fall_time = 0


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

    def draw(self, surface, offset_y=UI_HEIGHT):
        """Renders the piece to the provided surface with a vertical UI offset."""
        for dx, dy in self.get_offsets():
            px, py = (self.x + dx) * BLOCK_SIZE, (self.y + dy) * BLOCK_SIZE + offset_y
            pygame.draw.rect(surface, self.color, (px, py, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(surface, WHITE, (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_next(surface, piece):
    """Draws the 'Next Piece' preview in the top-right of the UI."""
    label = label_font.render('NEXT', True, WHITE)
    surface.blit(label, (WIDTH - 80, 10))
    for dx, dy in piece.get_offsets():
        px = (WIDTH - 85) + (dx * 20)
        py = 35 + (dy * 20)
        pygame.draw.rect(surface, piece.color, (px, py, 20, 20))
        pygame.draw.rect(surface, WHITE, (px, py, 20, 20), 1)

def draw_hold(surface, piece):
    """Draws the 'Hold Piece' preview in the top-left of the UI."""
    label = label_font.render('HOLD', True, WHITE)
    surface.blit(label, (20, 10)) 
    for dx, dy in piece.get_offsets():
        px = 25 + (dx * 20)
        py = 35 + (dy * 20)
        pygame.draw.rect(surface, piece.color, (px, py, 20, 20))
        pygame.draw.rect(surface, WHITE, (px, py, 20, 20), 1)

def valid_space(piece, grid):
    """Checks if the piece's current position is within bounds and not colliding."""
    for dx, dy in piece.get_offsets():
        new_x, new_y = piece.x + dx, piece.y + dy
        if not (0 <= new_x < COLUMNS and new_y < ROWS):
            return False
        if new_y >= 0 and grid[new_y][new_x] != 0:
            return False
    return True

def clear_rows(grid):
    """Identifies full ROWS, removes them, and updates the global score."""
    full_rows = [i for i, row in enumerate(grid) if 0 not in row]
    count = 1
    for row_index in full_rows:
        del grid[row_index]
        grid.insert(0, [0 for _ in range(COLUMNS)])
        game.score += 100 * count
        count += 1

def draw_grid_lines(surface):
    """Draws the static grid lines on the board."""
    for r in range(ROWS + 1):
        pygame.draw.line(surface, GRAY, (0, r * BLOCK_SIZE + UI_HEIGHT), (WIDTH, r * BLOCK_SIZE + UI_HEIGHT))
    for c in range(COLUMNS + 1):
        pygame.draw.line(surface, GRAY, (c * BLOCK_SIZE, UI_HEIGHT), (c * BLOCK_SIZE, HEIGHT))

def draw_locked_blocks(surface, grid):
    """Draws all blocks that have already landed and are part of the grid."""
    for y, row in enumerate(grid):
        for x, cell_color in enumerate(row):
            if cell_color != 0:
                px, py = x * BLOCK_SIZE, y * BLOCK_SIZE + UI_HEIGHT
                pygame.draw.rect(surface, cell_color, (px, py, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, WHITE, (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_game_over(surface):
    """Draws the Game Over screen."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    surface.blit(overlay, (0, 0))
    msg = score_font.render('GAME OVER', True, (255, 0, 0))
    retry_msg = label_font.render('Press "R" to Restart', True, WHITE)
    score_msg = label_font.render(f'Current score: {game.score}', True, WHITE)
    high_score_msg = label_font.render(f'High score: {game.high_score}', True, WHITE)
    surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2))
    surface.blit(high_score_msg, (WIDTH // 2 - high_score_msg.get_width() // 2, HEIGHT // 2 + 50))
    surface.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 100))

def reset_game():
    """Resets the game state."""
    game.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
    game.current_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    game.next_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    game.hold_piece = Piece(3, 0, random.choice(list(shapes.keys())))
    game.score = 0
    game.fall_speed = 500
    game.game_over = False
    game.hold_used = 0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
score_font = pygame.font.SysFont('Roboto', 40, bold=True)
label_font = pygame.font.SysFont('Roboto', 20, bold=True)
game = Game()

reset_game()
running = True

while running:
    dt = clock.tick(60)
    
    if not game.game_over:
        game.fall_time += dt
        if game.fall_time > game.fall_speed:
            game.current_piece.y += 1
            if not valid_space(game.current_piece, game.grid):
                game.current_piece.y -= 1
                for dx, dy in game.current_piece.get_offsets():
                    game.grid[game.current_piece.y + dy][game.current_piece.x + dx] = game.current_piece.color
                
                clear_rows(game.grid)
                game.current_piece = game.next_piece
                game.next_piece = Piece(3, 0, random.choice(list(shapes.keys())))
                game.hold_used = 0
                
                if not valid_space(game.current_piece, game.grid):
                    if game.score > game.high_score:
                        game.high_score = game.score
                    game.game_over = True
                if game.fall_speed > 200:
                    game.fall_speed -= 5
            game.fall_time = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_ESCAPE:
                running = False
                
            if not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.current_piece.x -= 1
                    if not valid_space(game.current_piece, game.grid): game.current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    game.current_piece.x += 1
                    if not valid_space(game.current_piece, game.grid): game.current_piece.x -= 1
                if event.key == pygame.K_UP:
                    game.current_piece.rotation += 1
                    if not valid_space(game.current_piece, game.grid): game.current_piece.rotation -= 1
                if event.key == pygame.K_DOWN:
                    game.current_piece.y += 1
                    if not valid_space(game.current_piece, game.grid): game.current_piece.y -= 1
                if event.key == pygame.K_e:
                    if not game.hold_used:
                        game.current_piece, game.hold_piece = game.hold_piece, game.current_piece
                        game.hold_piece.x, game.hold_piece.y, game.hold_piece.rotation = 3, 0, 0
                        game.hold_used = 1
                if event.key == pygame.K_s:
                    while valid_space(game.current_piece, game.grid):
                        game.current_piece.y += 1
                    game.current_piece.y -= 1

    screen.fill(BLACK)
    draw_locked_blocks(screen, game.grid)
    draw_grid_lines(screen)
    game.current_piece.draw(screen)
    
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, UI_HEIGHT))
    lbl_score = label_font.render('SCORE', True, GRAY)
    screen.blit(lbl_score, (WIDTH // 2 - 20, 15))
    score_surf = score_font.render(f'{game.score}', True, WHITE)
    screen.blit(score_surf, (WIDTH // 2 - (score_surf.get_width() // 2), 35))

    draw_next(screen, game.next_piece)
    draw_hold(screen, game.hold_piece)
    pygame.draw.line(screen, (100, 100, 100), (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 2)
    
    if game.game_over:
        draw_game_over(screen)
        
    pygame.display.flip()
pygame.quit()
sys.exit()