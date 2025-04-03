import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),  # First layer
            nn.ReLU(),
            nn.Linear(128, 128),  # Second hidden layer
            nn.ReLU(),
            nn.Linear(128, output_dim)  # Output layer
        )
    
    def forward(self, state):
        return self.network(state)