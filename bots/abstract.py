from abc import ABCMeta, abstractmethod
import python_bitbankcc

import datetime

# TODO: candleから各値を計算する箇所をジェネレータに
# TODO: 入力値に関するエラー処理を追加


class AbstractBot(metaclass=ABCMeta):
    """
    Bot用抽象クラス
    """
    def __init__(self, window_size, test, start_jpy, test_start, pair):
        self.FEE = 0.0012
        self.window_size = window_size
        self.bitbank_pub = python_bitbankcc.public()

        self.crypto_name = None
        self.cache = None
        self.PAIR = pair

        self.TEST = test

        self.open_prices = []
        self.high_prices = []
        self.low_prices = []
        self.close_prices = []

        # 資産
        self.jpy = 0.0
        self.crypto = 0.0

        self.data_id = 0

        # 取引対象の仮想通貨の名前をセット
        self.set_crypto_name(self.PAIR)

        self.target_day = None
        self.last_test_day = False

        self.START_JPY = start_jpy
        self.TEST_START = test_start

    def reset_params(self):
        """
        パラメータのリセット
        """
        self.open_prices = []
        self.high_prices = []
        self.close_prices = []
        self.low_prices = []

        self.data_id = 0

        if self.TEST:
            self.target_day = datetime.datetime.strptime(self.TEST_START, "%Y%m%d")
            self.prepare_price_list()
            self.last_test_day = False
            self.jpy = self.START_JPY

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
                return True
            else:
                # 次の日のロウソク足を取得
                self.set_data()
                return False
        else:
            return False

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

    def set_crypto_name(self, pair):
        """
        :param pair: 仮想通貨ペア
        仮想通貨の名前をセットする
        """
        self.crypto_name = pair.split("_")[0].upper()

    def print_asset(self):
        asset_jpy = self.jpy + self.crypto * self.close_prices[-1]
        print("="*10 + "資産状況" + "="*10)
        print("日本円\t:{:.3f}".format(self.jpy), "円")
        print("仮想通貨\t:{}".format(self.crypto), self.crypto_name)
        print("想定資産\t:{:.3f}".format(asset_jpy), "円")
        print("="*26)

    def test_run(self, episode=1):
        """
        テストモード開始
        """
        for i in range(episode):
            done = False
            self.reset_params()  # パラメータのリセット
            while not done:
                done = self.step()
                # テストモードが無効の場合
                if done is None:
                    break

            if episode != 1:
                print("Episode {}".format(i))

            self.print_asset()  # 最終結果を出力
