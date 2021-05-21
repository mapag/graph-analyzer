from typing_extensions import final
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
from pandas import DataFrame as df

import os

load_dotenv()

# connection

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")


def binance_price(interval = Client.KLINE_INTERVAL_1HOUR):
    client = Client(API_KEY, API_SECRET)

    # account & balance

    # account = client.get_account()
    # balance = account['balances']

    # for bal in balance:
    #     if(float(bal['free']) > 0):
    #         print(bal)

    # candles

    candles = client.get_klines(symbol='LTCUSDT', interval=interval)

    candles_data_frame = df(candles)

    # dates parsing

    candles_data_frame_date = candles_data_frame[0]
    final_date = []

    for time in candles_data_frame_date.unique():
        readable = datetime.fromtimestamp(int(time/1000))
        final_date.append(readable)

    candles_data_frame.pop(0)
    candles_data_frame.pop(11)

    dataframe_final_date = df(final_date)
    dataframe_final_date.columns = ['date']

    final_data_frame = candles_data_frame.join(dataframe_final_date)

    final_data_frame.set_index('date', inplace=True)
    final_data_frame.columns = ['open', 'high', 'low', 'close', 'volume', 'close_time',
                                'asset_volume', 'trade_number', 'taker_buy_base', 'taker_buy_quote']

    return final_data_frame


# print(binance_price(Client.KLINE_INTERVAL_1HOUR))
