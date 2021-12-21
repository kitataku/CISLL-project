from datetime import datetime
from bots.bollinger_band import BollingerBand

bot = BollingerBand(pair="bat_jpy", test_start="20211219")
print(bot.high_prices)
bot.calc_values()
bot.test_run()
