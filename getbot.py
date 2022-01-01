from bots.bollinger_band import BollingerBand
from bots.adx import ADX
from bots.a2c import A2C


def get_bot(bot_name, params):
    """
    :param bot_name: BOT class name
    - BollingerBand: 逆張りボリンジャーバンド
    - ADX: ADXによる判断
    :param params: parameters of bot
    """
    bot = None

    # Botの設定
    if bot_name == "BollingerBand":
        bot = BollingerBand
    elif bot_name == "ADX":
        bot = ADX
    elif bot_name == "A2C":
        bot = A2C
        
    # パラメータの設定
    bot = bot(**params)
    return bot
