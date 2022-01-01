import torch
from bots.rainforcement.A2C.network import Network


class AdvantageActorCriticAgent:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = None

    def make_model(self, feature_shape, action_shape):
        """
        :param feature_shape: 特徴量の次元数
        :param action_shape: 行動の数
        """
        # モデル作成
        self.model = Network(feature_shape, action_shape)
        self.model.to(self.device)

        return self.model
