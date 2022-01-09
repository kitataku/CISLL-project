import os
import python_bitbankcc

# 環境変数にキーを設定しておく
API_KEY = os.environ["API"]  # API key
API_SEC = os.environ["SECRET"]  # Secret key

private_api = python_bitbankcc.private(API_KEY, API_SEC)
assets = private_api.get_asset()["assets"]

type_dic = {"limit": "指値注文", "market": "成行注文"}

for asset in assets:
    asset_name = asset["asset"]  # 資産名
    asset_amount = asset["free_amount"]  # 利用可能量
    locked_amount = asset["locked_amount"]  # ロックされている量

    if float(asset_amount) != 0 or float(locked_amount) != 0:
        print("="*20)
        print("資産名:\t\t", asset_name)
        print("利用可能量:\t", asset_amount)
        print("ロック量:\t", locked_amount)

    if float(locked_amount) != 0:
        pair = asset_name + "_jpy"
        active_order = private_api.get_active_orders(pair)["orders"]

        print("\n注文があります！")
        for i, ao in enumerate(active_order):
            order_id = ao["order_id"]
            order_type = type_dic[ao["type"]]
            start_amount = ao["start_amount"]  # 注文時の数量
            executed_amount = ao["executed_amount"]  # 約定済数量
            order_price = ao["price"]  # 注文価格

            print("||No.", i + 1)
            print("||注文ID:\t\t", order_id)
            print("||注文数量:\t\t", start_amount)
            print("||約定済数量:\t", executed_amount)
            print("||注文価格:\t\t", order_price)
