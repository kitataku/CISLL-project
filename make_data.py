import pandas as pd
import python_bitbankcc
import datetime
import numpy as np
import os

bitbank_pub = python_bitbankcc.public()
PATH = os.path.dirname(__file__)


def make_data(pair, start_day, end_day=None, return_window=12):
    """"
    :param pair: 通貨ペア
    :param start_day: データ取得開始日(yyyymmdd)
    :param end_day: データ取得終了日(yyyymmdd)
    :param return_window: returnの計算幅
    """
    str_pattern = "%Y%m%d"
    col_names = ["open", "high", "low", "close", "vol", "timestamp"]
    output_col_names = ["open", "high", "low", "close", "vol", "timestamp", "VWAP", "log_return"]

    # 実行日の時刻を00:00:00に調整
    today_zero = datetime.datetime.today().strftime(str_pattern)
    today_zero = datetime.datetime.strptime(today_zero, str_pattern)

    # end_dayがデータ取得範囲外である場合に実行日に更新
    if end_day is None:
        end_day = today_zero
    else:
        end_day = datetime.datetime.strptime(end_day, str_pattern)
        if end_day >= today_zero:
            end_day = today_zero

    # while条件用に日時型に変更
    target_day = datetime.datetime.strptime(start_day, str_pattern)

    # return_windowが日付をまたがないように調整
    if return_window > 288:
        return_window = 288

    while target_day <= end_day:
        # 取得対象前日のデータを取得
        target_yesterday = target_day - datetime.timedelta(days=1)
        target_yesterday_str = target_yesterday.strftime(str_pattern)

        pre_candles = bitbank_pub.get_candlestick(pair, "5min", target_yesterday_str)["candlestick"][0]["ohlcv"]
        df_pre_candles = pd.DataFrame(np.array(pre_candles, dtype=float), columns=col_names)

        # 取得対象日のデータを取得
        target_day_str = target_day.strftime(str_pattern)
        candles = bitbank_pub.get_candlestick(pair, "5min", target_day_str)["candlestick"][0]["ohlcv"]
        df_candles = pd.DataFrame(np.array(candles, dtype=float), columns=col_names)

        # timestampを変換
        df_output = pd.concat([df_pre_candles, df_candles])
        df_output["timestamp"] = df_output["timestamp"] / 1000
        df_output["timestamp"] = pd.to_datetime(df_output["timestamp"], unit="s")

        # VWAPを計算
        df_output["multiple"] = df_output["close"].multiply(df_output["vol"]).rolling(288).sum().values
        df_output["vol_sum"] = df_output["vol"].rolling(288).sum().values
        df_output["VWAP"] = df_output["multiple"] / df_output["vol_sum"]

        # log return
        # log(P(t)/P(t-window)) ~ P(t) / P(t-window) - 1
        df_output["log_return"] = (df_output["close"] / df_output["close"].shift(periods=return_window)) - 1

        # 出力用DataFrameから前日のデータを削除
        df_output = df_output[df_output["timestamp"] >= target_day]

        # 必要な列のみ抽出
        df_output = df_output[output_col_names]

        # データを出力
        df_output.to_csv(PATH + "/data/" + target_day_str + ".csv")

        # 取得対象日を更新
        target_day += datetime.timedelta(days=1)

