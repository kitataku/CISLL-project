from bots.abstract import AbstractBot
import python_bitbankcc
import datetime
import statistics


class BollingerBand(AbstractBot):
    def __init__(self, pair, window_size=10, test=True, test_start="20211201"):
        super(BollingerBand, self).__init__(window_size)
        self.bitbank_pub = python_bitbankcc.public()
        self.PAIR = pair
        self.cache = None
        self.SIGMA = 2

        if test:
            self.prepare_price_list(test_start)

    def prepare_price_list(self, start_day):
        today = datetime.datetime.today()
        target_day = datetime.datetime.strptime(start_day, "%Y%m%d")

        while target_day <= today:
            target_day_str = target_day.strftime("%Y%m%d")
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
                    break

            target_day += datetime.timedelta(days=1)

    def calc_values(self):
        """
        戦略に応じた値を計算する
        :return:
        """
        close_std = statistics.stdev(self.close_prices)
        close_mean = statistics.mean(self.close_prices)
        print(close_mean, close_std)

    def get_action(self):
        """
        行動を出力する。形式は次の通り
        [行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        :return:
        """
        print("ok")

