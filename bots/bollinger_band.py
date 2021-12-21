from bots.abstract import AbstractBot
import python_bitbankcc
import datetime
import statistics

# TODO: candleから各値を計算する箇所をジェネレータに


class BollingerBand(AbstractBot):
    def __init__(self, pair, window_size=20, test=True, test_start="20211201"):
        """

        :param pair:
        :param window_size:
        :param test:
        :param test_start:
        """
        super(BollingerBand, self).__init__(window_size)
        self.bitbank_pub = python_bitbankcc.public()

        self.PAIR = pair
        self.cache = None
        self.SIGMA = 2

        self.data_id = 0

        self.TEST = test
        if self.TEST:
            self.target_day = datetime.datetime.strptime(test_start, "%Y%m%d")
            self.prepare_price_list(test_start)
            self.last_test_day = False

    def prepare_price_list(self, start_day):
        """

        :param start_day:
        :return:
        """
        preparing = True
        while self.target_day <= datetime.datetime.today() and preparing:
            target_day_str = self.target_day.strftime("%Y%m%d")
            candles = self.bitbank_pub.get_candlestick(self.PAIR, "5min", target_day_str)
            candles = candles["candlestick"][0]["ohlcv"]

            for i, candle in enumerate(candles):
                open_price = float(candle[0])
                high_price = float(candle[1])
                low_price = float(candle[2])
                close_price = float(candle[3])

                self.update_info(open_price, high_price, low_price, close_price)

                if len(self.high_prices) >= self.window_size and len(candles) != i-1:
                    self.cache = candles[i+1:]
                    self.data_id = 0
                    preparing = False
                    break

            if preparing:
                self.target_day += datetime.timedelta(days=1)

    def set_data(self):
        """

        :return:
        """
        self.data_id = 0
        self.target_day += datetime.timedelta(days=1)

        # 実行日の時刻を00:00:00に調整
        today_zero = datetime.datetime.today().strftime("%Y%m%d")
        today_zero = datetime.datetime.strptime(today_zero, "%Y%m%d")

        # テストは実行日前日までを対象とする
        if self.target_day < today_zero:
            print(self.target_day)
            target_day_str = self.target_day.strftime("%Y%m%d")
            candles = self.bitbank_pub.get_candlestick(self.PAIR, "5min", target_day_str)
            self.cache = candles["candlestick"][0]["ohlcv"]
        else:
            self.last_test_day = True

    def calc_values(self):
        """
        戦略に応じた値を計算する
        :return:
        """
        close_std = statistics.stdev(self.close_prices)
        close_mean = statistics.mean(self.close_prices)

        r = self.get_action(close_std, close_mean)
        if r is not None:
            print(r)

    def get_action(self, std, mean):
        """
        行動を出力する。形式は次の通り
        [行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        :return:
        """
        lower_bundle = mean - std * self.SIGMA
        upper_bundle = mean + std * self.SIGMA
        price = self.close_prices[-1]

        if lower_bundle > price:
            return ["buy", 10]
        elif upper_bundle < price:
            return ["sell", 10]

    def step(self):
        """
        次のstepに進める
        """
        if not self.TEST:
            print("not TEST MODE!")
            return None

        ohlc = self.cache[self.data_id][0:4]
        ohlc = list(map(float, ohlc))
        self.update_info(*ohlc)

        self.calc_values()

        self.data_id += 1
        if self.data_id == len(self.cache):
            if self.last_test_day:
                # テスト終了
                print("Test Mode finish!")
                return True
            else:
                # 次の日のロウソク足を取得
                self.set_data()

    def test_run(self):
        done = False
        while not done:
            done = self.step()


