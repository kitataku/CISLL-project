from bots.abstract import AbstractBot
from bots.technical.technical_index import AverageDirectionalMovement


class ADX(AbstractBot):
    def __init__(self, pair, window_size=20, test=True, test_start="20211201", start_jpy=1000):
        """
        ADXによる取引Botクラス
        テストモードではtest_startで指定した日から実行日前日までのデータを使用
        :param pair: 取引通貨ペア
        :param window_size: 価格データをいくつ保持するか
        :param test: テストモード
        :param test_start: 検証日
        """
        super(ADX, self).__init__(window_size, test, start_jpy, test_start, pair)
        self.transaction_amount = 3.0  # 取引仮想通貨量

        self.adx_ins = AverageDirectionalMovement()
        self.first_dx = 0.0

        self.penetrate_plus_di = True
        self.penetrate_minus_di = True

    def calc_values(self):
        """
        戦略に応じた値を計算して売買判断を行う
        ADXを計算

        :return: [移動平均, 標準偏差]
        """
        ohlc = [
            self.open_prices[-1],
            self.high_prices[-1],
            self.low_prices[-1],
            self.close_prices[-1]
        ]
        adx = self.adx_ins.get_index(ohlc)
        if adx is not None:
            # adx上昇確認用
            self.first_dx = self.adx_ins.dx_list[0]

        return adx

    def get_action(self, items):
        """
        :param items: 売買判断に使用する値
        - adx: ADX(Average Directional Movement Index)

        買いシグナル
        +DIが-DIを下から上に突き抜けたとき
        ADXが上昇している
        +DI > ADX > -DI

        売りシグナル
        -DIが+DIを下から上に突き抜けたとき
        ADXが上昇している
        -DI > ADX > +DI

        :return: 配列[行動, 数量]
        行動は"buy", "sell", "pass"のいずれか
        """
        plus_di = self.adx_ins.plus_di
        minus_di = self.adx_ins.minus_di
        adx = items
        # ADX計算の準備ができていない、もしくはADXが上昇していない場合
        if items is None or self.first_dx > self.adx_ins.dx_list[-1]:
            return ["pass", self.transaction_amount]
        else:
            # +DIが-DIを下から上に突き抜けたフラグを更新
            if plus_di > minus_di and not self.penetrate_plus_di:
                self.penetrate_plus_di = True
            else:
                self.penetrate_plus_di = False

            # -DIが+DIを下から上に突き抜けたフラグを更新
            if minus_di > plus_di and not self.penetrate_minus_di:
                self.penetrate_minus_di = True
            else:
                self.penetrate_minus_di = False

            # 売買判断
            if plus_di > adx > minus_di and self.penetrate_minus_di:
                return ["buy", self.transaction_amount]
            elif minus_di > adx > plus_di and self.penetrate_plus_di:
                return ["sell", self.transaction_amount]
            else:
                return ["pass", self.transaction_amount]
