import pygame as pg
import sys
import Map
import Agent
import neat
import Main

RED = pg.color.Color("RED")
BLACK = pg.color.Color("BLACK")

class Simulation:

    def __init__(self, screen, map, start_position, direction, agent_type, options):
        self.screen = screen
        self.map = map
        self.start_position = start_position
        self.direction = direction
        self.agent_type = agent_type
        self.options = options

    # Method that runs the simulation based on type of agent.
    def run_simulation(self, genomes, config):
        pg.font.init()
        font = pg.font.SysFont('Calibri', 20)
        clock = pg.time.Clock()
        agents = []
        # Adds agents based on agent type.
        if self.agent_type == "AI agent":
            for key, g in genomes:
                agents.append(Agent.AI_Agent(self.start_position, self.direction, key, g, neat.nn.FeedForwardNetwork.create(g, config), self.options))
        elif self.agent_type == "Tracker agent":
            agents.append(Agent.Tracker_Agent(self.start_position, self.direction))
        elif self.agent_type == "Brute force":
            agents.append(Agent.Brute_Force(self.start_position))
        elif self.agent_type == "Pledge agent":
            agents.append(Agent.Pledge_Agent(self.start_position, self.direction))
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
            self.screen.blit(self.map.map_layer, (0, 0))
            alive = 0
            winner = False
            for a in agents:
                if a.winner:
                    winner = True
                if a.alive:
                    alive += 1
                    a.update_position(self.screen, self.map)
            if alive == 0:
                break
            if winner:
                print("Found solution!")
                return True
            self.screen.blit(font.render('Agents: ' + str(alive), False, BLACK), (int(self.map.size_x*self.map.difficulty/2), 0))
            pg.display.flip()
            clock.tick(600 if self.agent_type == "Brute force" else 60)




