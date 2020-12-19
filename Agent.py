import pygame as pg
import math as m
import random as rnd
import A_pathfinding
from abc import abstractmethod

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = pg.color.Color("BLUE")
GREEN = pg.color.Color("GREEN")
RED = pg.color.Color("RED")
YELLOW = pg.color.Color("ORANGE")
BROWN = pg.color.Color("BROWN")
ORANGE = pg.color.Color("ORANGE")
OBSTACLE = (0, 0, 0, 255)
# Speed limit for AI agents.
MAX_SPEED = 5
# Minimum speed for AI agents.
MIN_SPEED = 1
# Limit for the number of times an agent can step on the same position for the third time.
STEP_LIMIT = 5
# The degrees that an agent turns per iteration.
TURN_INCREMENT = 10


# Agent is the parent class, and the other Agents classes inherit from it.
class Agent():
    def __init__(self, starting_position):
        self.position = list(starting_position)
        self.alive = True
        self.winner = False

    # An abstract method that is mandatory for child classes.
    @abstractmethod
    def update_position(self, screen, map):
        pass


class AI_Agent(Agent):
    def __init__(self, starting_position, direction, key, genome, network, options):
        super().__init__(starting_position)
        self.direction = direction
        # ID provided by the population object.
        self.key = key
        # Genome that holds information about nodes and edges.
        self.genome = genome
        # The neural network object that outputs the change in speed and direction.
        self.network = network
        self.die_on_crash = options[0]
        self.stochastic = options[1]
        self.a_star_type = options[2]
        # Boolean value that determines whether fitness path should be displayed on screen.
        self.show_fitness_path = options[3]
        # Fitness score that is accessed by the NEAT algorithm to determine of agent should survive.
        self.genome.fitness = 0
        self.speed = 1
        self.euclidean_fitness = 0
        self.previous_positions = set()
        self.repeated_positions = set()
        self.repeated_step = 0

    # Public method called from simulation object to update agents position.
    def update_position(self, screen, map):
        self.screen = screen
        self.map = map
        # The decision process is done by inputting the sensor data to the neural network.
        dir, speed = self.network.activate(self.__check_paths())
        # If agent is stochastic the output from the neural network determines the probability for an action.
        if self.stochastic:
            if rnd.random() < abs(dir):
                self.direction += TURN_INCREMENT * (m.floor(dir) if dir < 0 else m.ceil(dir))
            if rnd.random() < abs(speed):
                self.speed = max(min(self.speed + m.floor(speed) if speed < 0 else m.ceil(speed), MAX_SPEED), MIN_SPEED)
        else:
            self.speed = max(min(self.speed + round(speed), MAX_SPEED), 1)
            self.direction += TURN_INCREMENT * round(dir)
        self.__check_move()
        self.__update_euclidean_fitness()
        self.__check_repetition()
        self.__create_heat()
        pg.draw.circle(screen, BLUE, self.position, 3)

    # Incrementally checks a move so that an agent stops when hitting a wall.
    def __check_move(self):
        for s in range(self.speed + 1):
            x = 0
            y = 0
            x += round(m.cos(m.radians(self.direction)))
            y += round(m.sin(m.radians(self.direction)))
            if not self.__check_position((self.position[0] + x, self.position[1] + y)):
                if self.winner:
                    self.genome.fitness = 1000
                    return False
                elif self.die_on_crash:
                    self.genome.fitness = self.__get_fitness(self.a_star_type)
                    self.alive = False
                    return False
            else:
                self.position[0] += x
                self.position[1] += y
        return True

    # Checks whether agent has hit an obstacle of reached the goal by checking the 7x7 collision box.
    def __check_position(self, position):
        for x in range(-3,4):
            for y in range(-3, 4):
                if self.map.map_layer.get_at((position[0] + x, position[1] + y)) == OBSTACLE:
                    return False
                elif self.map.map_layer.get_at((position[0] + x, position[1] + y)) == GREEN:
                    self.genome.fitness = 1000
                    self.winner = True
                    return False
        return True

    # Creates a heat map by decrementing the blue and green color channels, resulting in a red color.
    def __create_heat(self):
        pixel = self.map.map_layer.get_at((self.position))
        if pixel != BLACK:
            self.map.map_layer.set_at(self.position, (pixel[0], max(pixel[1] - 50, 0), max(pixel[2] - 50, 0), pixel[3]))

    # Checks if the current position has been visited before.
    def __check_repetition(self):
        if tuple(self.position) in self.repeated_positions:
            self.repeated_step += 1
        elif tuple(self.position) in self.previous_positions:
            self.repeated_positions.add(tuple(self.position))
        else:
            self.previous_positions.add(tuple(self.position))
        if self.repeated_step > STEP_LIMIT:
            self.genome.fitness = self.__get_fitness(self.a_star_type)
            self.alive = False

    # Gets the correct fitness determined by the fitness type selected.
    def __get_fitness(self, type):
        if type:
            fitness = 1000 - A_pathfinding.get_path(self.map, self.position, self.show_fitness_path)
            return fitness
        else:
            fitness = self.euclidean_fitness
            if self.show_fitness_path:
                pg.draw.line(self.screen, BLUE, self.position, self.map.exit)
            return fitness

    # Continuously updates the euclidean fitness score.
    def __update_euclidean_fitness(self):
            self.euclidean_fitness = max(1000 - m.sqrt(m.pow(self.map.exit[0] - self.position[0], 2) + m.pow(self.map.exit[1] - self.position[1], 2)), self.euclidean_fitness)

    # Checks the sensors.
    def __check_paths(self):
        # Inner method that checks one sensor direction.
        def __check_path(direction):
            pos = self.position.copy()
            dir = self.direction + direction
            dis = 0
            while True:
                pos[0] = max(pos[0], 0)
                pos[0] = min(pos[0], self.map.size_x * self.map.difficulty - 1)
                pos[1] = max(pos[1], 0)
                pos[1] = min(pos[1], self.map.size_y * self.map.difficulty - 1)
                if self.map.map_layer.get_at(pos) == GREEN:
                    return 1000
                if self.map.map_layer.get_at(pos) == OBSTACLE:
                    pos[0] -= round(m.cos(m.radians(dir)))
                    pos[1] -= round(m.sin(m.radians(dir)))
                    break
                else:
                    pos[0] += round(m.cos(m.radians(dir)))
                    pos[1] += round(m.sin(m.radians(dir)))
                    dis += 1
            pg.draw.line(self.screen, YELLOW, self.position, pos)
            return dis

        # Sets up all sensor directions and calls the inner method.
        distances = []
        dir_0 = -90
        distances.append(__check_path(dir_0))
        dir_1 = -45
        distances.append(__check_path(dir_1))
        dir_2 = 0
        distances.append(__check_path(dir_2))
        dir_3 = 45
        distances.append(__check_path(dir_3))
        dir_4 = 90
        distances.append(__check_path(dir_4))
        return distances

class Tracker_Agent(Agent):
    def __init__(self, starting_position, direction):
        super().__init__(starting_position)
        self.direction = direction
        self.at_wall = False

    def update_position(self, screen, map):
        self.screen = screen
        self.map = map
        # The agent continues in a straight line until a wall is encountered.
        if not self.at_wall:
            check_position = (round(self.position[0] + m.cos(m.radians(self.direction))), round(self.position[1] + m.sin(m.radians(self.direction))))
            if self.__check_move(check_position):
                self.position = check_position
            else:
                self.at_wall = True
                if self.direction % 90 != 0:
                    self.direction += 45
        else:
            # Turns to the right until a valid move is found.
            while not self.__check_move((round(self.position[0] + m.cos(m.radians(self.direction))), round(self.position[1] + m.sin(m.radians(self.direction))))):
                self.direction += 90
            self.position = (round(self.position[0] + m.cos(m.radians(self.direction))),
                             round(self.position[1] + m.sin(m.radians(self.direction))))
            if self.at_wall:
                # Turns into the wall in case the wall turns.
                self.direction -= 90
                self.map.map_layer.set_at(self.position, RED)
        pg.draw.circle(screen, BLUE, self.position, 3)


    def __check_move(self, move):
        # Agent turns away from wall if it encounters it own tracks.
        if self.map.map_layer.get_at((move[0], move[1])) == RED:
            if self.at_wall:
                self.direction += 90
            else:
                self.direction += 90
            self.at_wall = False
            return True
        # Checks for obstacles and exit.
        for x in range(-3, 4):
            for y in range(-3, 4):
                if self.map.map_layer.get_at((move[0] + x, move[1] + y)) == OBSTACLE:
                    return False
                elif self.map.map_layer.get_at((move[0] + x, move[1] + y)) == GREEN:
                    self.winner = True
        return True

class Pledge_Agent(Agent):
    def __init__(self, starting_position, direction):
        super().__init__(starting_position)
        self.direction = direction if direction % 90 == 0 else direction + 45
        # Variable to keep track of turns.
        self.turn_counter = 0
        self.at_wall = False

    def update_position(self, screen, map):
        self.screen = screen
        self.map = map
        # If counter is zero the agent continues in a straight line.
        if self.turn_counter == 0:
            if self.__check_move(self.direction):
                self.__make_move()
            else:
                # Turns to the right when a wall is encountered.
                self.turn_counter += 1
                self.direction += 90
        else:
            # Temporary direction for checking move.
            temp_dir = self.direction - 90
            self.turn_counter -= 1
            while not self.__check_move(temp_dir):
                temp_dir += 90
                self.turn_counter += 1
            self.direction = temp_dir
            self.__make_move()

    # Checks for obstacles and the exit.
    def __check_move(self, direction):
        move = [round(self.position[0] + m.cos(m.radians(direction))), round(self.position[1] + m.sin(m.radians(direction)))]
        for x in range(-3, 4):
            for y in range(-3, 4):
                if self.map.map_layer.get_at((move[0] + x, move[1] + y)) == OBSTACLE:
                    return False
                elif self.map.map_layer.get_at((move[0] + x, move[1] + y)) == GREEN:
                    self.winner = True
        return True

    def __make_move(self):
        self.position = [round(self.position[0] + m.cos(m.radians(self.direction))), round(self.position[1] + m.sin(m.radians(self.direction)))]
        pg.draw.circle(self.screen, BLUE, self.position, 3)

class Brute_Force(Agent):
    def __init__(self, starting_position):
        super().__init__(starting_position)
        # Keeps track of active nodes.
        self.edge_node = set()

    def update_position(self, screen, map):
        self.screen = screen
        self.map = map
        self.__update_neighbourhood()

    # Iterates through neighborhood and adds new nodes to list.
    def __update_neighbourhood(self):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if self.map.map_layer.get_at((self.position[0] + x, self.position[1] + y)) == GREEN:
                    self.winner = True
                    return
                elif self.map.map_layer.get_at((self.position[0] + x, self.position[1] + y)) == OBSTACLE:
                    continue
                elif self.map.map_layer.get_at((self.position[0] + x, self.position[1] + y)) != RED:
                    self.map.map_layer.set_at((self.position[0] + x, self.position[1] + y), RED)
                    self.edge_node.add((self.position[0] + x, self.position[1] + y))
        self.edge_node.remove((self.position[0], self.position[1]))
        sample = rnd.sample(self.edge_node, 1)[0]
        self.position[0] = sample[0]
        self.position[1] = sample[1]


