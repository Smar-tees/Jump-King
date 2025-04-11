import pygame
import os
import time
import threading
import game
from shared_data import king_state
from Agent import agent
import level_loader
import pandas as pd
import ast

pygame.init()

def start_agent(id, move_des, best_pattern):
    print('inside start_agent func')
    player = agent(id, move_des, best_pattern)
    while not stop_agent:
        player.pick_move()
        if king_state['vy'] == 0:
            player.update_heights(king_state)

    print('agent loop stopped')
    player.calc_reward(king_state['y'])
    player.save_pattern()

if __name__ == "__main__":
    agent_num = 100
    generation_num = 10
    names = ['Prof Ellis', 'Logan', 'Walter', 'Chris', 'Josh', 'Michael', 'Kevin', 'John']
    move_des = 'random'
    best_pattern = []
    level = level_loader.load_level()
    start_state = {
    "x": 300,
    "y": 500,
    "vx": 0,
    "vy": 0,
    "time_elapsed": 0,
    "jumps_made": 0,
    "distance_traveled": 0,
    "color": (255, 0, 0)  # Red
}

    for generation in range(generation_num):
        name = names[generation]
        for num in range(agent_num):
            stop_agent = False
            if generation > 0:
                move_des = 'scripted'

                df = pd.read_csv('paths.csv')
                best_row = df.loc[df['reward'].idxmax()]
                best_pattern = ast.literal_eval(best_row['pattern'])

            game_thread = threading.Thread(target=game.game_loop, args=(start_state, level))
            game_thread.daemon = True
            game_thread.start()

            king_name = name + str(num)

            king_thread = threading.Thread(target=start_agent, args=(king_name, move_des, best_pattern))
            king_thread.daemon = True
            king_thread.start()



            time.sleep(5*(generation+1))
            stop_agent = True
            game.running = False
            king_thread.join()
            game_thread.join()

    # Here I want the code to start the agent loop, but stop it after 5 seconds, so the loop will start the thread, and join the thread after 5 seconds