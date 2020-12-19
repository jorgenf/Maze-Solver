import numpy as np
import random as rnd
import pygame as pg
import sys

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = pg.color.Color("BLUE")
GREEN = pg.color.Color("GREEN")
RED = pg.color.Color("RED")
WALL_THICKNESS = 1

class Map:
    def __init__(self, size_x, size_y, difficulty, random_exit):
        self.map_layer = pg.Surface([size_x, size_y])
        self.difficulty = difficulty
        self.size_x = round(size_x / self.difficulty)
        self.size_y = round(size_y / self.difficulty)
        self.random_exit = random_exit
        self.__create_map()
        pg.init()

    def __create_map(self):
        # Recursive method that creates map by continuously splitting the map and calling itself.
        def __split(x_int, y_int, horizontal):
            # Runs until the remaining sections are a certain size.
            if (abs(x_int[0] - x_int[1]) > 1 * self.difficulty and abs(y_int[0] - y_int[1]) > 2 * self.difficulty) or (abs(x_int[0] - x_int[1]) > 2 * self.difficulty and abs(y_int[0] - y_int[1]) > 1 * self.difficulty):
                if abs(y_int[0] - y_int[1]) <= 2 * self.difficulty and horizontal:
                    horizontal = False
                elif abs(x_int[0] - x_int[1]) <= 2 * self.difficulty and not horizontal:
                    horizontal = True
                # Splits map at a random point.
                sp = rnd.randrange(y_int[0] if horizontal else x_int[0], y_int[1] if horizontal else x_int[1], self.difficulty)
                # Creates a hole in the wall section at a random point.
                hole = rnd.randrange(x_int[0] if horizontal else y_int[0], x_int[1] if horizontal else y_int[1], self.difficulty)
                if horizontal:
                    pg.draw.line(self.map_layer, BLACK, (x_int[0], sp), (x_int[1], sp), WALL_THICKNESS)
                    pg.draw.line(self.map_layer, WHITE, (hole + 1, sp), (hole + self.difficulty - 1, sp), WALL_THICKNESS)
                    __split(x_int, (y_int[0], sp), False)
                    __split(x_int, (sp, y_int[1]), False)
                else:
                    pg.draw.line(self.map_layer, BLACK, (sp, y_int[0]), (sp, y_int[1]), WALL_THICKNESS)
                    pg.draw.line(self.map_layer, WHITE, (sp, hole + 1), (sp, hole + self.difficulty - 1), WALL_THICKNESS)
                    __split((x_int[0], sp), y_int, True)
                    __split((sp, x_int[1]), y_int, True)
            else:
                return None

        self.map_layer.fill(pg.color.Color("WHITE"))
        x = (self.difficulty, (self.size_x - 1) * self.difficulty)
        y = (self.difficulty, (self.size_y - 1) * self.difficulty)
        __split(x, y, True)
        # Draws border of maze.
        pg.draw.line(self.map_layer, BLACK, (0 + self.difficulty, 0 + self.difficulty), (0 + self.difficulty, self.size_y * self.difficulty - self.difficulty), 2)
        pg.draw.line(self.map_layer, BLACK, (self.size_x * self.difficulty - self.difficulty, 0 + self.difficulty), (self.size_x * self.difficulty - self.difficulty, self.size_y * self.difficulty - self.difficulty), 2)
        pg.draw.line(self.map_layer, BLACK, (0 + self.difficulty, 0 + self.difficulty), (self.size_x * self.difficulty - self.difficulty, 0 + self.difficulty), 2)
        pg.draw.line(self.map_layer, BLACK, (0 + self.difficulty, self.size_y * self.difficulty - self.difficulty), (self.size_x * self.difficulty - self.difficulty, self.size_y * self.difficulty - self.difficulty), 2)
        if self.random_exit:
            self.__create_random_exit()

    def __create_random_exit(self):
        choices = [(rnd.randrange(self.difficulty, (self.size_x - 1) * self.difficulty, self.difficulty), self.difficulty, True), (rnd.randrange(self.difficulty, (self.size_x - 1) * self.difficulty, self.difficulty), (self.size_y - 1) * self.difficulty, True), (self.difficulty, rnd.randrange(self.difficulty, (self.size_y - 1) * self.difficulty, self.difficulty), False), ((self.size_x - 1) * self.difficulty, rnd.randrange(self.difficulty, (self.size_y - 1) * self.difficulty, self.difficulty), False)]
        exit = rnd.choice(choices)
        pg.draw.line(self.map_layer, GREEN, (exit[0], exit[1]), (exit[0] + self.difficulty, exit[1]) if exit[2] else (exit[0], exit[1] + self.difficulty), 2)
        self.exit = (exit[0] + round(self.difficulty / 2), exit[1])  if exit[2] else (exit[0], exit[1] + round(self.difficulty / 2))


