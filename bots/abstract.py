from abc import ABCMeta, abstractmethod


# 抽象クラス
class AbstractBot(metaclass=ABCMeta):
    def __init__(self, window_size=10):
        self.window_size = window_size

        self.open_prices = []
        self.high_prices = []
        self.low_prices = []
        self.close_prices = []

    def update_info(self, open_price, high, low, close_price):
        """
        OHLCデータを取り込み、情報を更新する
        :param open_price: 始値
        :param high: 高値
        :param low: 低値
        :param close_price: 終値
        """
        self.open_prices.append(open_price)
        self.high_prices.append(high)
        self.low_prices.append(low)
        self.close_prices.append(close_price)

        if len(self.high_prices) > self.window_size:
            # window sizeになったら最初の値は捨てる
            self.high_prices = self.high_prices[1:]
            self.low_prices = self.low_prices[1:]
            self.open_prices = self.open_prices[1:]
            self.close_prices = self.close_prices[1:]

    @abstractmethod
    def calc_values(self):
        """
        戦略に応じた値を計算する
        """
        pass

    @abstractmethod
    def get_action(self):
        """
        行動を出力する。形式は次の通り
        [行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        """
        pass
