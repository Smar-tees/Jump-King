import random
import csv
import keyboard
import time

class agent():
    def __init__(self, agent_id, move_des, best_pattern):
        self.pattern = []
        self.reward = 0
        self.id = agent_id
        self.min_val = 0
        self.max_val = 1000000
        self.move_des = move_des
        self.script = best_pattern

    
    def update_heights(self, king_state):
        self.min_val = max(self.min_val, king_state['y'])
        # This value is should be the lowest it starts, so on this level it will be 570
        self.max_val = min(self.max_val, king_state['y'])
        # This value is how high it climbs, so it will start at 570, but it will be 510 if it reaches the first platform
    
    def calc_reward(self, end_y):
        if end_y > self.max_val:
            self.max_val = end_y
        self.reward = self.min_val - self.max_val
    
    def pick_move(self):
        if self.move_des == 'random':
            keys = ['a', 'd', 'w']
            key = random.choice(keys)
            self.pattern.append(key)
            keyboard.press(key)
            time.sleep(0.1)
            keyboard.release(key)
        
        elif self.move_des == 'scripted':
            self.pattern = self.script
            for key in self.pattern:
                keyboard.press(key)
                time.sleep(0.1)
                keyboard.release(key)
            self.move_des = 'random'
        

    def save_pattern(self):
        with open('paths.csv', mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            pattern_str = str(self.pattern)
            writer.writerow([self.id, pattern_str, self.reward])
            print(f'Saved Agent {self.id} pattern to paths.csv')



# Every 15 sec it restarts