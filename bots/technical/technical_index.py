class AverageDirectionalMovement:
    def __init__(self, window_size=14, dx_widow_size=14):
        # 指標のリスト
        self.plus_dm_list = []
        self.minus_dm_list = []
        self.tr_list = []
        self.dx_list = []

        # ひとつ前のロウソク足
        self.pre_ohlc = None

        self.plus_di = 0.0
        self.minus_di = 0.0

        # 計算幅
        self.window_size = window_size
        self.dx_window_size = dx_widow_size

    def calc_dm(self, ohlc):
        """
        DM(Directional Movement)を計算する
        :param ohlc: 最新のロウソク足
        """
        # +DM = high_t - high_{t-1}
        plus_dm = ohlc[1] - self.pre_ohlc[1]
        # -DM = low_t - low_{t-1}
        minus_dm = ohlc[2] - self.pre_ohlc[2]

        # 方向性が負である場合は0にする
        if plus_dm < 0:
            plus_dm = 0.0
        if minus_dm < 0:
            minus_dm = 0.0

        # 方向性が小さいほうは0にする
        if plus_dm > minus_dm:
            minus_dm = 0.0
        elif minus_dm > plus_dm:
            plus_dm = 0.0
        else:
            plus_dm = 0.0
            minus_dm = 0.0

        self.plus_dm_list.append(plus_dm)
        self.minus_dm_list.append(minus_dm)

    def calc_tr(self, ohlc):
        """
        TR(True Range)を計算する
        TRは変動幅の増加分を表す
        - candle _height: ロウソク足の長さ(high_t - low_t)
        - close2high: 終値から高値(high_t - close_{t-1})
        - close2low: 終値から低値(close_{t-1} - low_t)
        :param ohlc: 最新のロウソク足
        """
        # TR計算用の値
        candle_height = ohlc[1] - ohlc[2]
        close2high = ohlc[1] - self.pre_ohlc[3]
        close2low = self.pre_ohlc[3] - ohlc[2]

        # TR(True Range)を計算
        self.tr_list.append(max([candle_height, close2high, close2low]))

    def calc_adx(self):
        """
        ADX(Average Directional Movement Index)を計算する
        - plus_di: 上昇の強さ
        - minus_di: 下落の強さ
        :return adx: ADX(Average Directional Movement Index)
        """
        # DI(Directional Indicator)を計算
        self.plus_di = sum(self.plus_dm_list) / sum(self.tr_list) * 100
        self.minus_di = sum(self.minus_dm_list) / sum(self.tr_list) * 100

        # DX(Directional Movement Index)を計算
        self.dx_list.append(abs(self.plus_di - self.minus_di) / (self.plus_di + self.minus_di))
        # DXのリストの準備ができたらADXを計算する
        if len(self.dx_list) >= self.dx_window_size:
            return sum(self.dx_list) / len(self.dx_list)
        else:
            return None

    def get_index(self, ohlc):
        """
        :param ohlc: 最新のロウソク足
        :return:
        """
        if self.pre_ohlc is not None:
            self.calc_dm(ohlc)
            # TR(True Range)を計算
            self.calc_tr(ohlc)

        adx = None
        # TR, +DM, -DMのリストの準備ができたらTRの計算を行う
        if len(self.tr_list) >= self.window_size:
            adx = self.calc_adx()

        # ロウソク足を更新
        self.pre_ohlc = ohlc

        return adx
