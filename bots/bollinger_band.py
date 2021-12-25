from bots.abstract import AbstractBot
import python_bitbankcc
import datetime
import statistics

# TODO: candleから各値を計算する箇所をジェネレータに
# TODO: 入力値に関するエラー処理を追加


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
        super(BollingerBand, self).__init__(window_size)
        self.bitbank_pub = python_bitbankcc.public()

        self.PAIR = pair
        self.transaction_amount = 3.0  # 取引仮想通貨量
        self.cache = None
        self.SIGMA = 2

        self.data_id = 0

        self.TEST = test
        if self.TEST:
            self.target_day = datetime.datetime.strptime(test_start, "%Y%m%d")
            self.prepare_price_list()
            self.last_test_day = False
            self.jpy = start_jpy

        # 取引対象の仮想通貨の名前をセット
        self.set_crypto_name(self.PAIR)

    def set_crypto_name(self, pair):
        """
        :param pair: 仮想通貨ペア
        仮想通貨の名前をセットする
        """
        self.crypto_name = pair.split("_")[0].upper()

    def prepare_price_list(self):
        """
        OHLCデータ配列それぞれの長さがwindow_sizeになるようデータを取得する
        """
        preparing = True  # 準備中フラグ

        # 実行日の時刻を00:00:00に調整
        today_zero = datetime.datetime.today().strftime("%Y%m%d")
        today_zero = datetime.datetime.strptime(today_zero, "%Y%m%d")
        # データ取得対象はプログラム実行日前日まで
        while self.target_day <= today_zero and preparing:
            # ロウソク足取得
            target_day_str = self.target_day.strftime("%Y%m%d")
            candles = self.bitbank_pub.get_candlestick(self.PAIR, "5min", target_day_str)
            candles = candles["candlestick"][0]["ohlcv"]

            for i, candle in enumerate(candles):
                open_price = float(candle[0])
                high_price = float(candle[1])
                low_price = float(candle[2])
                close_price = float(candle[3])

                # OHLCデータを追加
                self.update_info(open_price, high_price, low_price, close_price)

                # データ取得完了
                if len(self.high_prices) >= self.window_size:
                    # データ追加に使用していないロウソク足がある場合は退避させておく
                    if i-1 != len(candles):
                        self.cache = candles[i+1:]
                    preparing = False
                    break

            # 準備完了していない場合は対象日を次の日へ
            if preparing:
                self.target_day += datetime.timedelta(days=1)

    def set_data(self):
        """
        新しいOHLCデータを取得
        """
        self.data_id = 0
        self.target_day += datetime.timedelta(days=1)

        # 実行日の時刻を00:00:00に調整
        today_zero = datetime.datetime.today().strftime("%Y%m%d")
        today_zero = datetime.datetime.strptime(today_zero, "%Y%m%d")

        # テストは実行日前日までを対象とする
        if self.target_day < today_zero:
            # ロウソク足取得
            target_day_str = self.target_day.strftime("%Y%m%d")
            candles = self.bitbank_pub.get_candlestick(self.PAIR, "5min", target_day_str)
            self.cache = candles["candlestick"][0]["ohlcv"]
        else:
            self.last_test_day = True

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

    def step(self):
        """
        次のstepに進める
        """
        # テストモードでない場合は処理を終了
        if not self.TEST:
            print("not TEST MODE!")
            return None

        # OHLCデータを取得してリストを更新する
        ohlc = self.cache[self.data_id][0:4]
        ohlc = list(map(float, ohlc))
        self.update_info(*ohlc)

        # 売買判断用の値を計算
        items = self.calc_values()
        # 行動を出力する
        action = self.get_action(items)
        # 資産を更新
        self.update_assets(action)

        # 取得したデータの読み込みインデックスを更新
        self.data_id += 1
        if self.data_id == len(self.cache):
            if self.last_test_day:
                # テスト終了
                print("Test Mode finish!")
                return True
            else:
                # 次の日のロウソク足を取得
                self.set_data()
                return False
        else:
            return False

    def test_run(self):
        """
        テストモード開始
        """
        done = False
        while not done:
            done = self.step()
            # テストモードが無効の場合
            if done is None:
                break
