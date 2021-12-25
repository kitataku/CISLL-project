from bots.bollinger_band import BollingerBand

if __name__ == "__main__":
    bot = BollingerBand(pair="bat_jpy", test_start="20211224", start_jpy=10000)
    bot.test_run()  # テスト実行
    bot.print_asset()  # 最終結果を出力
