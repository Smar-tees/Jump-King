import pandas as pd
import keyboard
import time
import threading
import game
import level_loader
import ast
import pygame

clock = pygame.time.Clock
desired_ticks = 6
is_pressing = False
df = pd.read_csv('paths.csv')
best_row = df.loc[df['reward'].idxmax()]
print(best_row)

pattern = ast.literal_eval(best_row['pattern'])


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
level = level_loader.load_level()

game_thread = threading.Thread(target=game.game_loop, args=(start_state, level))
game_thread.daemon = True
game_thread.start()

for key in pattern:  
    if not is_pressing:
        keyboard.press(key)
        is_pressing = True
        press_ticks = 0
    elif is_pressing:
        press_ticks += 1
        if press_ticks >= desired_ticks:
            keyboard.release(key)
            is_pressing = False

    clock.tick(60)