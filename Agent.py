import random
import csv

class Agent():
    def __init__(self, agent_id):
        self.pattern = []
        self.reward = 0
        self.id = agent_id
    
    def pick_move(self):
        keys = ['a', 'd', 'space']
        key = random.choice(keys)
        self.pattern.append(key)

        return key

    def save_pattern(self):
        with open('paths.csv', mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            pattern_str = str(self.pattern)
            writer.writerow([self.id, pattern_str, self.reward])
            print(f'Saved Agent {self.id} pattern to paths.csv')



# Every 15 sec it restarts