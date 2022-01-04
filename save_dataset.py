import os


def save_dataset(data, crypto_name, yymmdd):
    """
    :param data: 保存対象データ
    :param crypto_name: 仮想通貨名
    :param yymmdd: データ日付
    """
    file_name = crypto_name + "_" + yymmdd  # ファイル名

    try:
        os.mkdir(os.path.dirname(__file__) + "/../data")
    except FileExistsError:
        pass
    finally:
        data.to_csv(os.path.dirname(__file__) + "/../data/"+file_name+".csv")
