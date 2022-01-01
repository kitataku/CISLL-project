import torch
import torch.nn as nn
from torch import optim

from bots.abstract import AbstractBot
from bots.rainforcement.A2C.agent import AdvantageActorCriticAgent
from bots.technical.technical_index import AverageDirectionalMovement

import numpy as np


class A2C(AbstractBot):
    def __init__(self, pair, window_size=20, test=True, test_start="20211201", start_jpy=1000):
        super().__init__(window_size, test, start_jpy, test_start, pair)
        self.ACTION_NUM = 3  # 行動の数
        self.transaction_amount = 3.0  # 取引仮想通貨量
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.agent = AdvantageActorCriticAgent()
        self.adx_ins = AverageDirectionalMovement()

        self.model = None
        self.optim = None

    def calc_values(self):
        """
        戦略に応じた値を計算する
        """
        ohlc = [
            self.open_prices[-1],
            self.high_prices[-1],
            self.low_prices[-1],
            self.close_prices[-1]
        ]
        adx = self.adx_ins.get_index(ohlc)
        if adx is not None:
            features = [self.close_prices[-1], adx]
            if self.model is None:
                self.model = self.agent.make_model(len(features), self.ACTION_NUM)
                self.optim = optim.Adam(self.model.parameters())

            return features

    def get_action(self, items):
        if self.model is not None:
            # 特徴量
            features = torch.tensor(np.array(items), dtype=torch.float).to(self.device)

            # 学習
            self.optim.zero_grad()

            action, action_logit, value = self.model(features)
            action_tmp = action.unsqueeze(0)
            action_logit = action_logit.unsqueeze(0)
            neg_loss = nn.CrossEntropyLoss()(action_logit, action_tmp)
            advantage = action_logit - value
            policy_loss = torch.mean(neg_loss * advantage)
            policy_loss.backward()
            self.optim.step()

            action_num = action.item()
            if action_num == 0:
                return ["buy", self.transaction_amount]
            elif action_num == 1:
                return ["sell", self.transaction_amount]
            else:
                return["pass", self.transaction_amount]
        else:
            return ["pass", self.transaction_amount]

    def set_features(self):
        """
        特徴量をセット
        - 最新の終値
        - ADX
        """
        ohlc = [
            self.open_prices[-1],
            self.high_prices[-1],
            self.low_prices[-1],
            self.close_prices[-1]
        ]
        adx = self.adx_ins.get_index(ohlc)
        if adx is not None:
            features = [self.close_prices[-1], adx]
            if self.model is None:
                self.model = self.agent.make_model(len(features), self.ACTION_NUM)
                self.optim = optim.Adam(self.model.parameters())

            return features
