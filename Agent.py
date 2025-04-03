import random
import csv
import keyboard
import time

class agent():
    def __init__(self, agent_id):
        self.pattern = []
        self.reward = 0
        self.id = agent_id
        self.min_val = 0
        self.max_val = 1000000
    
    def update_heights(self, king_state):
        self.min_val = max(self.min_val, king_state['y'])
        self.max_val = min(self.max_val, king_state['y'])
    
    def calc_reward(self, end_y):
        if end_y < self.min_val:
            self.min_val = end_y
        self.reward = 10 * (self.min_val - self.max_val)
    
    def pick_move(self):
        keys = ['a', 'd', 'w']
        key = random.choice(keys)
        self.pattern.append(key)
        keyboard.press(key)
        time.sleep(0.1)
        keyboard.release(key)
        

    def save_pattern(self):
        with open('paths.csv', mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            pattern_str = str(self.pattern)
            writer.writerow([self.id, pattern_str, self.reward])
            print(f'Saved Agent {self.id} pattern to paths.csv')



# Every 15 sec it restarts