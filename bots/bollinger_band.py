from bots.abstract import AbstractBot
import statistics


class BollingerBand(AbstractBot):
    def __init__(self, pair, window_size=20, test=True, test_start="20211201", start_jpy=1000):
        """
        Bollinger Bandによる取引Botクラス
        テストモードではtest_startで指定した日から実行日前日までのデータを使用
        :param pair: 取引通貨ペア
        :param window_size: 価格データをいくつ保持するか
        :param test: テストモード
        :param test_start: 検証日
        """
        super(BollingerBand, self).__init__(window_size, test, start_jpy, test_start, pair)
        self.transaction_amount = 3.0  # 取引仮想通貨量

        # Bollinger Band判断用
        self.SIGMA = 2

    def calc_values(self):
        """
        戦略に応じた値を計算して売買判断を行う
        Bollinger Bandに使用する値を計算

        :return: [移動平均, 標準偏差]
        """
        close_std = statistics.stdev(self.close_prices)
        close_mean = statistics.mean(self.close_prices)

        return [close_std, close_mean]

    def get_action(self, items):
        """
        :param items: 売買判断に使用する値
        - std: 標準偏差
        - mean: 移動平均

        逆張りBollinger Band
        以下の条件に基づいて行動を出力する
        (MA - (SIGMA * STD) > price) -> 買う
        (MA + (SIGMA * STD) < price) -> 売る

        :return: 配列[行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        """
        std = items[0]
        mean = items[1]
        # 売買判断用の値を計算
        lower_bundle = mean - std * self.SIGMA
        upper_bundle = mean + std * self.SIGMA
        # 最新の価格を取得
        price = self.close_prices[-1]

        if lower_bundle > price:
            return ["buy", self.transaction_amount]
        elif upper_bundle < price:
            return ["sell", self.transaction_amount]
        else:
            return ["pass", self.transaction_amount]
