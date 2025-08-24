'''
Conway's Game of Life implementation using Pygame.
Controls:
- Arrow Up/Down: Increase/Decrease speed
- Space: Pause/Unpause
- R: Reset grid with random cells
- C: Clear grid
- Mouse Click: Toggle cell state
- Escape: Exit the program
'''

import random
import pygame
ROWS = 20
COLS = 20
CELL_SIZE = 30


def count_neighbors(row, col, Grid):
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    count = 0
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            count += Grid[r][c]
    return count

def update_grid(Grid):
    new_grid = [row[:] for row in Grid]
    for r in range(ROWS):
        for c in range(COLS):
            neighbors = count_neighbors(r, c, Grid)
            if Grid[r][c] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[r][c] = 0
                else:
                    new_grid[r][c] = 1
            else:
                if neighbors == 3:
                    new_grid[r][c] = 1
                else:
                    new_grid[r][c] = 0
    return new_grid

def print_grid(Grid, screen):
    screen.fill((0, 0, 0))
    for r in range(ROWS):
        for c in range(COLS):
            color = (0, 200, 0) if Grid[r][c] == 1 else (0, 0, 0)
            pygame.draw.rect(screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2))
    pygame.display.flip()

def main():
    Grid = [[1 if random.random() < 0.25 else 0 for _ in range(COLS)] for _ in range(ROWS)]
    pygame.init()
    pygame.display.set_caption("Conway's Game of Life")
    screen = pygame.display.set_mode((COLS*CELL_SIZE, ROWS*CELL_SIZE))
    delay = 100
    paused = False
    while True:
        delay = max(10, min(delay, 5000))
        print_grid(Grid, screen)
        if not paused:
            Grid = update_grid(Grid)
        pygame.time.delay(delay)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Exit on ESC
                    pygame.quit()
                    return
                if event.key == pygame.K_DOWN: # Decrease speed
                    delay += 10
                elif event.key == pygame.K_UP: # Increase speed
                    delay -= 10
                if event.key == pygame.K_SPACE:# Pause/Unpause
                    paused = not paused
                if event.key == pygame.K_r: # Reset grid
                    Grid = [[1 if random.random() < 0.25 else 0 for _ in range(COLS)] for _ in range(ROWS)]
                if event.key == pygame.K_c: # Clear grid
                    Grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            if event.type == pygame.MOUSEBUTTONDOWN: #Draw cells
                x, y = event.pos
                col, row = x // CELL_SIZE, y // CELL_SIZE
                if 0 <= row < ROWS and 0 <= col < COLS:
                    Grid[row][col] = 1 - Grid[row][col]
if __name__ == "__main__":
    main()
    
