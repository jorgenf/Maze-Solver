import math as m
import pygame as pg
import numpy as np
import sys
import time

# Constant variables
OBSTACLE = (0, 0, 0, 255)
PURPLE = pg.color.Color("PURPLE")
GREY = pg.color.Color("GREY")
RED = pg.color.Color("RED")
GREEN = pg.color.Color("GREEN")
BLUE = pg.color.Color("BLUE")
# The diagonal cost or distance
DIAGONAL_COST = 1.4

# The main method that runs the A* algorithm
def get_path(map, starting_position, show_path):
    open_dict = {}
    closed_dict = {}
    map_layer_copy = map.map_layer.copy()


    def check_closed(x,y):
        if(x,y) in closed_dict:
            return True
        else:
            return False

    def check_open(x,y):
        if (x,y) in open_dict:
            return True
        else:
            return False

    # Iterates through a nodes neighborhood and assigns or updates scores.
    def update_neighbors(node):
        for x in range(-1, 2):
            for y in range(-1, 2):
                # Avoids checking pixels outside of the map.
                if (x == 0 and y == 0) or map.size_x * map.difficulty - 1 <= node.pos_x + x < 0 or map.size_y * map.difficulty - 1 <= node.pos_y + y < 0:
                    continue
                # Avoids checking walls.
                elif map.map_layer.get_at((node.pos_x + x, node.pos_y + y)) == OBSTACLE or check_closed(node.pos_x + x, node.pos_y + y):
                    continue
                # Updates score if node is already explored.
                elif check_open(node.pos_x + x, node.pos_y + y):
                    n = open_dict.get((node.pos_x + x,node.pos_y + y))
                    if n.g_cost > node.g_cost + 1:
                        n.update_g_cost(node.g_cost + 1, node)
                # Adds node if not present.
                else:
                    open_dict[(node.pos_x + x, node.pos_y + y)] = Node(node.pos_x + x, node.pos_y + y, map.exit, node.g_cost + (DIAGONAL_COST if abs(x) + abs(y) == 2 else 1), node)
                    if show_path:
                        map_layer_copy.set_at((node.pos_x + x, node.pos_y + y), GREEN)

    # Selects the initial node.
    current = Node(starting_position[0], starting_position[1], map.exit, 0, False)
    open_dict[(current.pos_x,current.pos_y)] = current

    # Runs if the process should be displayed on the screen.
    if show_path:
        screen = pg.display.set_mode((map.size_x * map.difficulty, map.size_y * map.difficulty))
        clock = pg.time.Clock()

    # Main loop. Runs until exit is reached.
    while current.pos_x != map.exit[0] or current.pos_y != map.exit[1]:
        # Sorts dictionary and selects best node.
        current = sorted(open_dict.values(), key=lambda node: node.f_cost)[0]
        update_neighbors(current)
        del open_dict[(current.pos_x, current.pos_y)]
        closed_dict[(current.pos_x, current.pos_y)] = current
        if show_path:
            map_layer_copy.set_at((current.pos_x, current.pos_y), RED)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
            screen.blit(map_layer_copy, (0, 0))
            pg.display.flip()
            clock.tick(600)

    distance = 0
    # Backtracks through each nodes parent and returns the count.
    while current.parent:
        current = current.parent
        if show_path:
            map_layer_copy.set_at((current.pos_x,current.pos_y), BLUE)
            screen.blit(map_layer_copy, (0, 0))
            pg.display.flip()
            clock.tick(240)
        distance += 1
    return distance

# f_cost : total node score
# g_cost : distance from starting node
# h_cost : distance from goal
class Node:
    def __init__(self, pos_x, pos_y, goal_position, g_cost, parent):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.parent = parent
        self.g_cost = g_cost
        self.h_cost = m.sqrt(m.pow(goal_position[0] - pos_x, 2) + m.pow(goal_position[1] - pos_y, 2))
        self.f_cost = self.g_cost + self.h_cost

    def update_g_cost(self, g_cost, parent):
        self.parent = parent
        self.g_cost = g_cost
        self.f_cost = self.g_cost + self.h_cost
