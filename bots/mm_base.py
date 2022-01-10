from bots.abstract import AbstractBot


class MMBase(AbstractBot):
    def __init__(self, pair, window_size=20, test=True, test_start="20211201", start_jpy=1000):
        super().__init__(window_size, test, start_jpy, test_start, pair)

        self.LOT = 3.0  # 取引量

        self.SPREAD_ENTRY = 0.0005
        self.SPREAD_CANCEL = 0.0003
        self.AMOUNT_THREAD = 10.0
        self.DELTA = 1.0

        self.pos = False  # positionを持っているか
        self.aks_pos = 0.0
        self.bid_pos = 0.0

    def calc_values(self):
        """
        戦略に応じた値を計算する
        """
        depth = self.bitbank_pub.get_depth(self.PAIR)
        asks = depth["asks"]
        bids = depth["bids"]

        ask_idx = 0
        ask_amount = 0
        while ask_amount < self.AMOUNT_THREAD:
            ask_amount += float(asks[ask_idx][1])
            ask_idx += 1

        bid_idx = 0
        bid_amount = 0
        while bid_amount < self.AMOUNT_THREAD:
            bid_amount += float(bids[bid_idx][1])
            bid_idx += 1

        return [float(asks[ask_idx][0]), float(bids[bid_idx][0])]

    def get_action(self, items):
        """

        :param items:
        :return:
        """
        # スプレッドを計算
        ask_price = items[0]
        bid_price = items[1]
        spread = (ask_price - bid_price) / bid_price

        ask_id = None
        bid_id = None

        print("ポジションチェック")
        print("売り注文チェック")
        print("買い注文チェック")

        print("SPREAD: ", spread)

        # 売り注文と買い注文のいずれか一方のポジションがある場合
        # self.pos=True
        # ask_id = 売り注文ID
        # bid_id = 買い注文ID

        # positionを持っている場合
        if self.pos:
            if ask_id is not None:
                print("売り注文をキャンセル")

            if bid_id is not None:
                print("買い注文をキャンセル")

        if spread > self.SPREAD_ENTRY:
            ask_price -= self.DELTA
            bid_price += self.DELTA
            print("売り注文:", ask_price)
            print("買い注文:", bid_price)


bot = MMBase("bat_jpy")
items_loc = bot.calc_values()
bot.get_action(items_loc)
