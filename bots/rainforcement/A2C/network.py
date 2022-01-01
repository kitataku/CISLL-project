import torch
import torch.nn as nn
import torch.nn.functional as F


class Network(nn.Module):
    def __init__(self, feature_shape, action_shape):
        """
        :param feature_shape: 特徴量の次元数
        :param action_shape: 行動の数
        """
        super(Network, self).__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.fc1 = nn.Linear(feature_shape, 10)
        self.fc2 = nn.Linear(10, 20)
        self.fc3 = nn.Linear(20, 20)

        self.actor_layer = nn.Linear(20, action_shape)
        self.critic_layer = nn.Linear(20, 1)

    def forward(self, x):
        h1 = F.relu(self.fc1(x))
        h2 = F.relu(self.fc2(h1))
        h3 = F.relu(self.fc3(h2))

        action_values = self.actor_layer(h3)  # Q(s,a)
        value = self.critic_layer(h3)  # V(s)

        # Gumbel Max Trick
        noise = torch.rand(action_values.shape).to(self.device)
        action = torch.argmax(action_values - torch.log(-torch.log(noise)))

        return action, action_values, value
