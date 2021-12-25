from abc import ABCMeta, abstractmethod


# 抽象クラス
class AbstractBot(metaclass=ABCMeta):
    def __init__(self, window_size):
        self.FEE = 0.0012
        self.window_size = window_size

        self.crypto_name = None

        self.open_prices = []
        self.high_prices = []
        self.low_prices = []
        self.close_prices = []

        self.jpy = 0.0
        self.crypto = 0.0

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
    def get_action(self, items):
        """
        行動を出力する。形式は次の通り
        [行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        """
        pass

    def update_assets(self, action):
        """
        行動内容に従って資産を更新する
        :param action:
        :return:
        """
        # 最新の価格を取得
        latest_price = self.close_prices[-1]

        buy_sell = action[0]
        amount = action[1]

        if buy_sell == "buy":
            # 取引価格
            transaction_price = amount*latest_price*(1+self.FEE)
            # 購入可能チェック
            if self.jpy >= transaction_price:
                # 資産更新
                self.jpy -= transaction_price
                self.crypto += amount

        elif buy_sell == "sell":
            # 取引価格
            transaction_price = amount*latest_price*(1-self.FEE)
            if self.crypto >= amount:
                # 資産更新
                self.jpy += transaction_price
                self.crypto -= amount

    def print_asset(self):
        print("="*10 + "資産状況" + "="*10)
        print("日本円\t:{:.3f}".format(self.jpy), "円")
        print("仮想通貨\t:{}".format(self.crypto), self.crypto_name)
        print("="*26)
