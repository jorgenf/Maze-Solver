import Map
import pygame as pg
import pygame_menu as pgm
import sys
import math as m
import numpy as np
import re

BLUE = pg.color.Color("BLUE")
RED = pg.color.Color("RED")
GREEN = pg.color.Color("GREEN")
OBSTACLE = (0, 0, 0, 255)

def show_menu():
    # Global variables so that all methods can access and update values.
    global screen, map, starting_position, direction, difficulty, random_exit, agent_type, number_of_agents, number_of_generations, die_on_crash, stochastic_agent, a_star_fitness, draw_fitness_path, num, gen, col, sto, fit, fitp, btn, last_agt
    last_agt = "AI agent"
    # Runs when user is finished selecting options.
    def start():
        global screen, map, starting_position, direction, options
        size_x.set_value(max(int(size_x.get_value()), 200))
        size_y.set_value(max(int(size_y.get_value()), 200))
        screen, map, starting_position, direction = create_map(int(size_x.get_value()), int(size_y.get_value()), random_exit, difficulty, agent_type)
        menu.disable()

    # Updates values as parameters are changed in menu.
    def change_x(val):
        global starting_position
        starting_position = (val, size_y.get_value())

    def change_y(val):
        global starting_position
        starting_position = (size_x.get_value(), val)

    def change_re(input, val):
        global random_exit
        random_exit = val

    def change_dif(input, val):
        global difficulty
        difficulty = val

    # Removes options if AI agent is not selected. Adds options back if AI agent is selected.
    def change_agt(input, val):
        global agent_type, num, gen, col, sto, fit, fitp, btn, last_agt
        agent_type = val

        if (val == "Tracker agent" or val == "Pledge agent" or val == "A*" or val == "Brute force") and last_agt == "AI agent":
            menu.get_current().remove_widget(num)
            menu.get_current().remove_widget(gen)
            menu.get_current().remove_widget(col)
            menu.get_current().remove_widget(sto)
            menu.get_current().remove_widget(fit)
            menu.get_current().remove_widget(fitp)
        elif val == "AI agent":
            menu.remove_widget(btn)
            num = menu.add_text_input('Number of agents :', default=50, onchange=change_num)
            gen = menu.add_text_input('Number of generations :', default=100, onchange=change_gen)
            col = menu.add_selector('Die on crash :', [('Yes', True), ('No', False)], 0, onchange=change_col)
            sto = menu.add_selector('Stochastic agent :', [('Yes', True), ('No', False)], 1, onchange=change_sto)
            fit = menu.add_selector('Fitness function :', [('Euclidean distance', False), ('A* distance', True)], 0,
                                    onchange=change_fit)
            fitp = menu.add_selector('Draw fitness path :', [('Yes', 1), ('No', 2)], 1, onchange=change_fitp)
            btn = menu.add_button('Choose starting position', start)
        last_agt = val

    def change_num(val):
        global number_of_agents
        number_of_agents = val

    def change_gen(val):
        global number_of_generations
        number_of_generations = val

    def change_col(input, val):
        global die_on_crash
        die_on_crash = val

    def change_sto(input, val):
        global stochastic_agent
        stochastic_agent = val

    def change_fit(input, val):
        global a_star_fitness
        a_star_fitness = val

    def change_fitp(input, val):
        global draw_fitness_path
        draw_fitness_path = val

    # Creates menu object and populates it with options.
    menu_screen = pg.display.set_mode((800,800))
    menu = pgm.Menu(800, 800, 'Labyrinth Solver', theme=pgm.themes.THEME_DARK)
    pg.display.set_caption("Labyrinth solver")
    size_x = menu.add_text_input('Map x-size :', default=1200, onchange=change_x)
    size_y = menu.add_text_input('Map y-size :', default=800, onchange=change_y)
    re = menu.add_selector('Random exit :', [('Yes', True), ('No', False)], 0, onchange=change_re)
    dif = menu.add_selector('Map difficulty :', [('Very easy', 60), ('Easy', 50), ('Medium', 40), ('Hard', 30), ('Very hard', 20)], 1, onchange=change_dif)
    agt = menu.add_selector('Solver :', [('AI agent', "AI agent"), ("Pledge agent", "Pledge agent"), ('Tracker agent', "Tracker agent"), ("A*", "A*"), ("Brute force", "Brute force")], 0, onchange=change_agt)
    num = menu.add_text_input('Number of agents :', default=50, onchange=change_num)
    gen = menu.add_text_input('Number of generations :', default=100, onchange=change_gen)
    col = menu.add_selector('Die on crash :', [('Yes', True), ('No', False)], 1, onchange=change_col)
    sto = menu.add_selector('Stochastic agent :', [('Yes', True), ('No', False)], 1, onchange=change_sto)
    fit = menu.add_selector('Fitness function :', [('Euclidean distance', False), ('A* distance', True)], 0, onchange=change_fit)
    fitp = menu.add_selector('Draw fitness path :', [('Yes', 1), ('No', 2)], 1, onchange=change_fitp)
    btn = menu.add_button('Choose starting position', start)
    if dif.get_value()[0] == "Very easy":
        difficulty = 60
    elif dif.get_value()[0] == "Easy":
        difficulty = 50
    elif dif.get_value()[0] == "Medium":
        difficulty = 40
    elif dif.get_value()[0] == "Hard":
        difficulty = 30
    else:
        difficulty = 20
    random_exit = True if re.get_value()[0] == "Yes" else False

    agent_type = agt.get_value()[0]
    number_of_agents = num.get_value()
    number_of_generations = int(gen.get_value())
    die_on_crash = True if col.get_value()[0] == "Yes" else False
    stochastic_agent = True if sto.get_value()[0] == "Yes" else False
    a_star_fitness = True if fit.get_value()[0] == "A* distance" else False
    draw_fitness_path = True if fitp.get_value()[0] == "Yes" else False

    menu.mainloop(menu_screen)
    number_of_agents = max(5, int(number_of_agents))
    update_config(number_of_agents)
    options = (die_on_crash, stochastic_agent, a_star_fitness, draw_fitness_path)
    return screen, map, starting_position, direction, agent_type, number_of_agents, int(number_of_generations), options

# Updates the config file.
def update_config(population_size):
    config = open("neat-config.txt", "rt")
    new_text = re.sub(r'(pop_size +=)( [0-9]+)', rf'\1 {population_size}', config.read())
    config.close()
    new_config = open("neat-config.txt", "wt")
    new_config.write(new_text)
    new_config.close()


def create_map(size_x, size_y, random_exit, difficulty, agent):
    screen = pg.display.set_mode((size_x, size_y))
    map = Map.Map(size_x, size_y, difficulty, random_exit)
    position_chosen = False
    start_position = False
    # Can't be boolean as False equates to 0 which is a valid direction.
    if agent == "A*" or agent == "Brute force":
        direction = True
    else:
        direction = None
    exit = random_exit
    pg.font.init()
    font = pg.font.SysFont('Calibri', 15)
    # Runs while loop until position, direction and exit is chosen. Includes code to display text and figures to make
    # process more intuitive.
    while not position_chosen or direction == None or not exit:
        map_copy = map.map_layer.copy()
        if not position_chosen:
            pg.draw.circle(map_copy, BLUE, pg.mouse.get_pos(), 3)
            text = font.render('Select position', False, (0, 0, 0))
        if position_chosen and direction == None:
            pg.draw.circle(map_copy, BLUE, start_position, 3)
            pg.draw.line(map_copy, BLUE, start_position, pg.mouse.get_pos())
            pg.draw.circle(map_copy, RED, pg.mouse.get_pos(), 3)
            text = font.render('Select direction', False, (0, 0, 0))
        if position_chosen and direction != None and not exit:
            pg.draw.circle(map_copy, BLUE, start_position, 3)
            text = font.render('Select exit', False, (0, 0, 0))
            if pg.mouse.get_pos()[0] in (map.difficulty, (map.size_x - 1) * map.difficulty) and map.difficulty <= pg.mouse.get_pos()[1] <= map.size_y * map.difficulty + 1:
                pg.draw.line(map_copy, GREEN, pg.mouse.get_pos(), (pg.mouse.get_pos()[0], min(pg.mouse.get_pos()[1] + round(map.difficulty / 2), (map.size_y - 1) * map.difficulty)), 2)
                pg.draw.line(map_copy, GREEN, pg.mouse.get_pos(), (pg.mouse.get_pos()[0], max(pg.mouse.get_pos()[1] - round(map.difficulty / 2), map.difficulty)), 2)
            if pg.mouse.get_pos()[1] in (map.difficulty, (map.size_y - 1) * map.difficulty) and map.difficulty <= pg.mouse.get_pos()[0] <= map.size_x * map.difficulty + 1:
                pg.draw.line(map_copy, GREEN, pg.mouse.get_pos(), (min(pg.mouse.get_pos()[0] + round(map.difficulty / 2), (map.size_x - 1) * map.difficulty), pg.mouse.get_pos()[1]), 2)
                pg.draw.line(map_copy, GREEN, pg.mouse.get_pos(), (max(pg.mouse.get_pos()[0] - round(map.difficulty / 2), map.difficulty), pg.mouse.get_pos()[1]), 2)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.MOUSEBUTTONUP and start_position and direction == None:
                temp_pos = pg.mouse.get_pos()
                direction = np.degrees(m.atan2((temp_pos[1] - start_position[1]),(temp_pos[0] - start_position[0])))
                direction = round(direction/45)*45

            if event.type == pg.MOUSEBUTTONUP and not start_position:
                start_position = pg.mouse.get_pos()
                obs = False
                for x in range(-3, 4):
                    for y in range(-3, 4):
                        if map_copy.get_at((start_position[0] + x, start_position[1] + y)) == OBSTACLE:
                            obs = True
                            break
                if map.difficulty > start_position[0] or start_position[0] > size_x - map.difficulty or map.difficulty > start_position[1] or start_position[1] > size_y - map.difficulty:
                    obs = True
                if not obs:
                    position_chosen = True
            if event.type == pg.MOUSEBUTTONUP and start_position and direction != None:
                if pg.mouse.get_pos()[0] in (map.difficulty, (map.size_x - 1) * map.difficulty) and map.difficulty <= pg.mouse.get_pos()[1] <= map.size_y * map.difficulty + 1:
                    pg.draw.line(map.map_layer, GREEN, pg.mouse.get_pos(), (pg.mouse.get_pos()[0], min(pg.mouse.get_pos()[1] + round(map.difficulty / 2), (map.size_y - 1) * map.difficulty)), 2)
                    pg.draw.line(map.map_layer, GREEN, pg.mouse.get_pos(), (pg.mouse.get_pos()[0], max(pg.mouse.get_pos()[1] - round(map.difficulty / 2), map.difficulty)), 2)
                    map.exit = pg.mouse.get_pos()
                    exit = True
                if pg.mouse.get_pos()[1] in (map.difficulty, (map.size_y - 1) * map.difficulty) and map.difficulty <= pg.mouse.get_pos()[0] <= map.size_x * map.difficulty + 1:
                    pg.draw.line(map.map_layer, GREEN, pg.mouse.get_pos(), (min(pg.mouse.get_pos()[0] + round(map.difficulty / 2), (map.size_x - 1) * map.difficulty), pg.mouse.get_pos()[1]), 2)
                    pg.draw.line(map.map_layer, GREEN, pg.mouse.get_pos(), (max(pg.mouse.get_pos()[0] - round(map.difficulty / 2), map.difficulty), pg.mouse.get_pos()[1]), 2)
                    map.exit = pg.mouse.get_pos()
                    exit = True
        screen.blit(map_copy, (0, 0))
        screen.blit(text, (pg.mouse.get_pos()[0] + 20, pg.mouse.get_pos()[1] - 20))
        pg.display.flip()
    return screen, map, start_position, direction
