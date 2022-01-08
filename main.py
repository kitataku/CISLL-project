from getbot import get_bot


if __name__ == "__main__":
    # parameters
    params = {
        "pair": "bat_jpy",
        "test_start": "20220101",
        "start_jpy": 10000
    }
    episode_num = 20

    # テスト実行
    bot = get_bot(bot_name="A2C", params=params)
    bot.test_run(episode=episode_num)  # テスト実行
    print("Test Mode finish!")
