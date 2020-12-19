import random
import numpy as np
import pygame as pg
import sys
# UP = 3
# DOWN = 1
# RIGHT = 0
# LEFT = 2

# Seperate left-hand solver.
def run_left_hand_solver():
    SIZE = 100
    NUMBER_OF_SOLUTIONS = 4
    pg.init()
    screen = pg.display.set_mode((1000, 1000))
    # Creates the maze.
    board, start_position = get_board(NUMBER_OF_SOLUTIONS,SIZE)
    COLORS = ("BLACK", "WHITE", "RED", "GREEN", "BLUE")
    pg.draw.rect(screen, pg.Color(COLORS[2]), (start_position[0], start_position[1], 10, 10))
    board, solution, position = solve(board, start_position, SIZE)
    if solution:
        print("SOLUTION FOUND!!!")
    else:
        print("No solution found...")
    print("Coordinates: ", position)
    # Draws the solution.
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        screen.fill((255, 255, 255))
        for i in range(100):
            for j in range(100):
                pg.draw.rect(screen, pg.Color(COLORS[int(board[i][j])]), (j * 10, i * 10, 10, 10))
        pg.display.update()

def solve(board, start_position,size):
    map = board
    position = start_position
    print("Start position: ", start_position)
    direction = 0
    steps = 0
    solution = False
    while check_step(direction, position, map):
        map, position , steps = step(direction, position, map, steps)
    while steps < 10000 and size - 1 > position[0] > 0 and size - 1 > position[1] > 0:
        while not check_step(direction,position,map):
            direction  = (direction + 1) % 4
        map,postition, steps = step(direction,position,map, steps)
        direction = (direction - 1) % 4
    if steps < 1000:
        solution = True
    return map, solution, position

def step(direction,position, map, steps):
    if direction == 1:
        map[position[0]+1][position[1]] = 4
        position[0] += 1
        steps += 1
    if direction == 3:
        map[position[0]-1][position[1]] = 4
        position[0] -= 1
        steps += 1
    if direction == 2:
        map[position[0]][position[1]-1] = 4
        position[1] -= 1
        steps += 1
    if direction == 0:
        map[position[0]][position[1]+1] = 4
        position[1] += 1
        steps += 1
    return map, position, steps


def check_step(direction,position, map):
    if direction == 0:
        if map[position[0]][position[1]+1] != 0:
            return True
        else:
            return False
    if direction == 1:
        if map[position[0]+1][position[1]] != 0:
            return True
        else:
            return False
    if direction == 2:
        if map[position[0]][position[1]-1] != 0:
            return True
        else:
            return False
    if direction == 3:
        if map[position[0]-1][position[1]] != 0:
            return True
        else:
            return False

# Creates map
def get_board(g_solutions, size = 100):
    board = np.zeros(shape=(size,size))
    for i in range(size):
        for j in range(size):
            board[i][j] = random.randint(0,1)
    for at in range(g_solutions):
        board = create_path(board, size)
    board, start_position = get_start_position(board, size)
    for i in range(size):
        for j in range(size):
            if board[i][j] == 2:
                board[i][j] = 1
    return board, start_position

# Creates possible solutions in maze.
def create_path(board, size):
    top_or_left = random.randint(0,1)
    if top_or_left == 0:
        position = [0,random.randint(0, size - 1)]
        board[position[0]][position[1]] = 1
        position[0] = position[0]+1
        board[position[0]][position[1]] = 1
        interval_start = 1
        interval_end = 3
    else:
        position = [random.randint(0, size - 1),0]
        board[position[0]][position[1]] = 1
        position[1] = position[1]+1
        board[position[0]][position[1]] = 1
        interval_start = 0
        interval_end = 2
    # UP = 0
    # DOWN = 1
    # RIGHT = 2
    # LEFT = 3

    while True:
        action = random.randint(interval_start, interval_end)
        if position[0] == size - 1 or position[0] == 0 or position[1] == 0:
            continue
        else:
            if action == 0:
                position[0] -= 1
            if action == 1:
                position[0] += 1
            if action == 2:
                position[1] += 1
            if action == 3:
                position[1] -= 1
            board[position[0]][position[1]] = 2
        if position[0] == size - 1 or position[0] == 0 or position[1] == size - 1 or position[1] == 0:
            break
    return board


def get_start_position(board, size):
    pos = [random.randint(0, size - 1), random.randint(0, size - 1)]
    while board[pos[0]][pos[1]] != 2:
        pos = [random.randint(0, size - 1), random.randint(0, size - 1)]
    board[pos[0]][pos[1]] = 3
    return board, pos

run_left_hand_solver()