from datetime import datetime
from bots.bollinger_band import BollingerBand

bot = BollingerBand(pair="bat_jpy")
print(bot.high_prices)
bot.calc_values()