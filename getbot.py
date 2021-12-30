from bots.bollinger_band import BollingerBand
from bots.adx import ADX


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
        
    # パラメータの設定
    bot = bot(**params)
    return bot
