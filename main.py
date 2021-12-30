from getbot import get_bot

if __name__ == "__main__":
    params = {"pair": "bat_jpy", "test_start": "20211224", "start_jpy": 10000}
    bot = get_bot(bot_name="ADX", params=params)
    bot.test_run()  # テスト実行
    bot.print_asset()  # 最終結果を出力
