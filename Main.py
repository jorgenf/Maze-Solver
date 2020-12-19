import neat
import Simulation
import pygame as pg
import Menu
import A_pathfinding
import time

# The entry point for the program.
if __name__ == "__main__":
    # Used to track simulation time.
    start_t = time.time()
    pg.init()
    # Displays menu and gets selected options.
    screen, map, starting_position, direction, agent_type, number_of_agents, number_of_generations, options = Menu.show_menu()
    # Creates a simulation object with options.
    sim = Simulation.Simulation(screen, map, starting_position, direction, agent_type, options)
    if agent_type == "AI agent":
        config_path = "./neat-config.txt"
        # Creates of configuration object based on the neat-config file.
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
        # Creates population object using the config object.
        population = neat.Population(config)
        # Adds reporters to get information in the console during simulation.
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())
        # Runs NEAT by passing in the simulation and number of generations.
        population.run(sim.run_simulation, number_of_generations)
    elif agent_type == "Tracker agent" or agent_type == "Brute force" or agent_type == "Pledge agent":
        sim.run_simulation(False, False)
    elif agent_type == "A*":
        # Runs the A* algorithm. Bypasses the simulation object.
        A_pathfinding.get_path(map, starting_position, True)
    end_t = time.time()
    print("Total time:", end_t - start_t)