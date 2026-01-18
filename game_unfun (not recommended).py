import pygame
import random
from time import sleep

columns = 10
rows = 20
block_size = 30
width = columns * block_size
height = rows * block_size

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

shapes = {
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
        return shapes[self.shape][self.rotation % len(shapes[self.shape])]

    def draw(self, surface):
        for dx, dy in self.get_offsets():
            px, py = (self.x + dx) * block_size, (self.y + dy) * block_size
            pygame.draw.rect(surface, self.color, (px, py, block_size, block_size))
            pygame.draw.rect(surface, white, (px, py, block_size, block_size), 1)

def valid_space(piece, grid):
    for dx, dy in piece.get_offsets():
        new_x, new_y = piece.x + dx, piece.y + dy
        if not (0 <= new_x < columns and new_y < rows):
            return False
        if new_y >= 0 and grid[new_y][new_x] != 0:
            return False
    return True

def clear_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if 0 not in row]
    for row_index in full_rows:
        del grid[row_index]
        grid.insert(0, [0 for _ in range(columns)])

def draw_grid_lines(surface):
    for r in range(rows):
        pygame.draw.line(surface, gray, (0, r * block_size), (width, r * block_size))
    for c in range(columns):
        pygame.draw.line(surface, gray, (c * block_size, 0), (c * block_size, height))

def draw_locked_blocks(surface, grid):
    for y, row in enumerate(grid):
        for x, cell_color in enumerate(row):
            if cell_color != 0:
                px, py = x * block_size, y * block_size
                pygame.draw.rect(surface, cell_color, (px, py, block_size, block_size))
                pygame.draw.rect(surface, white, (px, py, block_size, block_size), 1)

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

grid = [[0 for _ in range(columns)] for _ in range(rows)]
current_piece = Piece(3, 0, random.choice(list(shapes.keys())))
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
            
            current_piece = Piece(random.randrange(0, 6), 0, random.choice(list(shapes.keys())))
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

    screen.fill(black)
    draw_locked_blocks(screen, grid)
    draw_grid_lines(screen)
    current_piece.draw(screen)
    pygame.display.flip()

pygame.quit()