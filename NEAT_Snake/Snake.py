'''
A NEAT-based Snake game where the snake is controlled by a neural network.
Uses concept of Neat-Python library for neuroevolution.
'''
import pygame, random, sys

pygame.init()

CELL_SIZE = 20
GRID_SIZE = 20
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEAT Snake Visualization")
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = (0, -1)  # moving up
        self.spawn_food()
        self.score = 0
        return self.get_state()

    def spawn_food(self):
        while True:
            self.food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if self.food not in self.snake:
                break

    def step(self, action):
        # actions: 0 = straight, 1 = left turn, 2 = right turn
        self.turn(action)
        new_head = (self.snake[0][0] + self.direction[0],
                    self.snake[0][1] + self.direction[1])

        reward = 0
        done = False

        if (new_head in self.snake) or not (0 <= new_head[0] < GRID_SIZE) or not (0 <= new_head[1] < GRID_SIZE):
            done = True
            reward = -10
        else:
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.score += 1
                reward = 10
                self.spawn_food()
            else:
                self.snake.pop()
        return self.get_state(), reward, done

    def turn(self, action):
        dx, dy = self.direction
        if action == 1:   # left
            self.direction = (-dy, dx)
        elif action == 2: # right
            self.direction = (dy, -dx)

    def get_state(self):
        head = self.snake[0]
        dx, dy = self.direction

        # --- 1. Immediate obstacles ---
        def blocked(x, y):
            return (x, y) in self.snake or not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE)

        def step_in_dir(vec):
            return (head[0] + vec[0], head[1] + vec[1])

        left_vec = (-dy, dx)
        right_vec = (dy, -dx)

        danger_straight = int(blocked(*step_in_dir(self.direction)))
        danger_left = int(blocked(*step_in_dir(left_vec)))
        danger_right = int(blocked(*step_in_dir(right_vec)))

        # --- 2. Distances to nearest tail (normalized 1/d) ---
        def tail_distance(vec):
            x, y = head
            dist = 0
            while 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                dist += 1
                x += vec[0]
                y += vec[1]
                if (x, y) in self.snake[1:]:  # ignore head
                    return 1.0 / dist
            return 0.0

        tail_dist_straight = tail_distance(self.direction)
        tail_dist_left = tail_distance(left_vec)
        tail_dist_right = tail_distance(right_vec)

        # --- 3. Food relative position ---
        food_right = int(self.food[0] > head[0])
        food_below = int(self.food[1] > head[1])

        # --- 4. Current direction (one-hot: up, right, down) ---
        dir_up = int((dx, dy) == (0, -1))
        dir_right = int((dx, dy) == (1, 0))
        dir_down = int((dx, dy) == (0, 1))
        # implicit left = all 0s

        return [
            danger_straight, danger_left, danger_right,
            tail_dist_straight, tail_dist_left, tail_dist_right,
            food_right, food_below,
            dir_up, dir_right, dir_down
        ]


import neat

def eval_genome(genome, config):
    net = neat.nn.RecurrentNetwork.create(genome, config)
    game = SnakeGame()
    state = game.reset()
    fitness = 0
    steps = 0
    max_steps = 200

    while True:
        output = net.activate(state)
        action = output.index(max(output))
        state, reward, done = game.step(action)

        # small survival reward
        fitness += 0.1

        # add food reward
        if reward > 0:
            fitness += 10
            steps = 0  # reset time budget
        else:
            steps += 1

        # punish death lightly
        if done:
            fitness -= 5
            break

        # stop if snake is stuck for too long
        if steps > max_steps:
            break
    return fitness

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(eval_genomes, 500)
    print("Best genome:", winner)
    net = neat.nn.RecurrentNetwork.create(winner, config)
    import time

    game = SnakeGame()
    state = game.reset()
    done = False

    while not done:
        # activate network
        output = net.activate(state)
        action = output.index(max(output))  # pick the highest output

        # step game
        state, reward, done = game.step(action)

        # --- visualize using pygame ---
        screen.fill((0, 0, 0))  # black background

        # draw snake
        for segment in game.snake:
            pygame.draw.rect(screen, (0, 255, 0),
                            (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # draw food
        pygame.draw.rect(screen, (255, 0, 0),
                        (game.food[0]*CELL_SIZE, game.food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        time.sleep(0.01)  # 50 ms per frame

if __name__ == "__main__":
    run("config-feedforward")

