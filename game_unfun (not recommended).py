import pygame
import random
from time import sleep

COLUMN_COUNT = 10
ROW_COUNT = 20
BLOCK_SIZE = 30
SCREEN_WIDTH = COLUMN_COUNT * BLOCK_SIZE
SCREEN_HEIGHT = ROW_COUNT * BLOCK_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

SHAPES = {
    'U': [[(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)],
          [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)],
          [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (2, 1), (2, 2)],
          [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]],
    'N': [[(0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (2, 2)],
          [(0, 0), (0, 2), (1, 0,), (1, 1), (1, 2), (2, 0), (2, 2)]],
    'F': [[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (2, 2)],
          [(2, 2), (2, 1), (2, 0), (1, 2), (1, 1), (0, 2)],
          [(2, 2), (1, 2), (0, 2), (0, 1), (1, 1), (0, 0)]],
    'A': [[(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (1, 1)],
          [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2), (1, 1)],
          [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (2, 1), (2, 2), (1, 1)],
          [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2), (1, 1)]],
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(2, 0), (2, 1), (2, 2), (2, 3)]],
    'R': [[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 2)],
          [(2, 0), (1, 0), (0, 0), (2, 1), (1, 1), (0, 2)],
          [(2, 2), (2, 1), (2, 0), (1, 2), (1, 1), (0, 0)],
          [(0, 2), (1, 2), (2, 2), (0, 1), (1, 1), (2, 0)]],
    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    'S': [[(1, 1), (2, 1), (0, 2), (1, 2)],
          [(1, 0), (1, 1), (2, 1), (2, 2)]],
    'Z': [[(0, 1), (1, 1), (1, 2), (2, 2)],
          [(2, 0), (1, 1), (2, 1), (1, 2)]],
    'J': [[(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (1, 2), (0, 2)], 
          [(0, 0), (0, 1), (1, 1), (2, 1)], 
          [(1, 0), (2, 0), (1, 1), (1, 2)]],
    'L': [[(0, 1), (1, 1), (2, 1), (0, 2)], 
          [(0, 0), (1, 0), (1, 1), (1, 2)], 
          [(2, 0), (0, 1), (1, 1), (2, 1)], 
          [(1, 0), (1, 1), (1, 2), (2, 2)]],
    'T': [[(0, 1), (1, 1), (2, 1), (1, 2)], 
          [(1, 0), (0, 1), (1, 1), (1, 2)], 
          [(1, 0), (0, 1), (1, 1), (2, 1)], 
          [(1, 0), (1, 1), (2, 1), (1, 2)]]

}

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = (random.randrange(256), random.randrange(256), random.randrange(256))
        self.rotation = 0

    def get_offsets(self):
        return SHAPES[self.shape][self.rotation % len(SHAPES[self.shape])]

    def draw(self, surface):
        for dx, dy in self.get_offsets():
            px, py = (self.x + dx) * BLOCK_SIZE, (self.y + dy) * BLOCK_SIZE
            pygame.draw.rect(surface, self.color, (px, py, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(surface, WHITE, (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

def valid_space(piece, grid):
    for dx, dy in piece.get_offsets():
        new_x, new_y = piece.x + dx, piece.y + dy
        if not (0 <= new_x < COLUMN_COUNT and new_y < ROW_COUNT):
            return False
        if new_y >= 0 and grid[new_y][new_x] != 0:
            return False
    return True

def clear_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if 0 not in row]
    for row_index in full_rows:
        del grid[row_index]
        grid.insert(0, [0 for _ in range(COLUMN_COUNT)])

def draw_grid_lines(surface):
    for r in range(ROW_COUNT):
        pygame.draw.line(surface, GRAY, (0, r * BLOCK_SIZE), (SCREEN_WIDTH, r * BLOCK_SIZE))
    for c in range(COLUMN_COUNT):
        pygame.draw.line(surface, GRAY, (c * BLOCK_SIZE, 0), (c * BLOCK_SIZE, SCREEN_HEIGHT))

def draw_locked_blocks(surface, grid):
    for y, row in enumerate(grid):
        for x, cell_color in enumerate(row):
            if cell_color != 0:
                px, py = x * BLOCK_SIZE, y * BLOCK_SIZE
                pygame.draw.rect(surface, cell_color, (px, py, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, WHITE, (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

grid = [[0 for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
current_piece = Piece(3, 0, random.choice(list(SHAPES.keys())))
fall_time = 0
fall_speed = 500

running = True
while running:
    dt = clock.tick(60)
    fall_time += dt
    if fall_time > fall_speed:
        current_piece.y += 1
        if not valid_space(current_piece, grid):
            current_piece.y -= 1
            for dx, dy in current_piece.get_offsets():
                grid[current_piece.y + dy][current_piece.x + dx] = current_piece.color
            
            clear_rows(grid)
            
            current_piece = Piece(3, 0, random.choice(list(SHAPES.keys())))
            if not valid_space(current_piece, grid):
                running = False
            fall_speed = random.randrange(100, 500)
        fall_time = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_piece.x -= 1
                if not valid_space(current_piece, grid): current_piece.x += 1
                if random.randrange(10) == 0:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid): current_piece.x += 1
            if event.key == pygame.K_RIGHT:
                current_piece.x += 1
                if not valid_space(current_piece, grid): current_piece.x -= 1
                if random.randrange(10) == 0:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid): current_piece.x -= 1
            if event.key == pygame.K_UP:
                current_piece.rotation += 1
                if not valid_space(current_piece, grid): current_piece.rotation -= 1
                if random.randrange(10) == 0:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid): current_piece.rotation -= 1
            if event.key == pygame.K_DOWN:
                current_piece.y += 1
                if not valid_space(current_piece, grid): current_piece.y -= 1
                if random.randrange(10) == 0:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid): current_piece.y -= 1

    screen.fill(BLACK)
    draw_locked_blocks(screen, grid)
    draw_grid_lines(screen)
    current_piece.draw(screen)
    pygame.display.flip()

pygame.quit()