from numpy.core.fromnumeric import trace
import pandas as pd
import talib
import requests
from itertools import compress
import numpy as np
from candle_rankings import candle_rankings
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import os
from datetime import datetime, timedelta
from termcolor import colored
import time

SYMBOL = 'BTCUSDT'
INTERVAL = '4h'

def recognize_candlestick(df):
    op = df['open'].astype(float)
    hi = df['high'].astype(float)
    lo = df['low'].astype(float)
    cl = df['close'].astype(float)

    candle_names = talib.get_function_groups()['Pattern Recognition']

    exclude_items = ('CDLCOUNTERATTACK',
                     'CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN',
                     'CDLKICKINGBYLENGTH')

    candle_names = [
        candle for candle in candle_names if candle not in exclude_items]

    # create columns for each candle
    for candle in candle_names:
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    df['openTime'] = pd.to_datetime(df['openTime'], unit='ms')
    df['closeTime'] = pd.to_datetime(df['closeTime'], unit='ms')
    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['Momentum'] = talib.MOM(df['close'], timeperiod=14)
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)

    for index, row in df.iterrows():
        #  no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index, 'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(
                ), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
              # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(
                ), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(
                compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    cols_to_drop = candle_names
    df.drop(cols_to_drop, axis=1, inplace=True)

    # print(amount)
    # print(f'{((amount - 1000) / 1000) * 100}% de ganancia')
    return df


def init():
    dfs = []
    DIAS_PARA_ATRAS = 3
    for index in range(1,DIAS_PARA_ATRAS):
      
      startTime = int((datetime.now() - timedelta(days=index+1)).timestamp()*1000)
      endTime = int((datetime.now() - timedelta(days=index)).timestamp()*1000)
      
      KLINESURL = f'https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=1000&startTime={startTime}&endTime={endTime}'
      candles = requests.get(KLINESURL).json()

      print(f'Esperando un momento para que binance no nos banee. Quedan {DIAS_PARA_ATRAS - index} días restantes...')
      time.sleep(2)

      df = pd.DataFrame(candles, columns=(
          'openTime',
          'open',
          'high',
          'low',
          'close',
          'volume',
          'closeTime',
          'quoteAssetVolume',
          'numberOfTrades',
          'takerBuyBaseAssetVolume',
          'takerBuyQuoteAssetVolume',
          ''
      ))

      df.pop('volume')
      df.pop('quoteAssetVolume')
      df.pop('numberOfTrades')
      df.pop('takerBuyBaseAssetVolume')
      df.pop('takerBuyQuoteAssetVolume')
      df.pop('')

      recognize_candlestick(df)

      o = df['open'].astype(float)
      h = df['high'].astype(float)
      l = df['low'].astype(float)
      c = df['close'].astype(float)
      p = df['candlestick_pattern'].map(lambda x: x.replace('CDL', '').replace('_Bull', ' ALZA').replace(
          '_Bear', ' BAJA').replace('NO_PATTERN', 'NO HAY PATRON').replace('2', '').replace('3', ''))

      dfs.append(df)

    dfs = reversed(dfs)
    finaldf = pd.concat(dfs)

    finaldf.to_csv('TA.csv')
    print('Archivo generado con exito')


probando = 'Probando ' + SYMBOL + ' en intervalos de '+ INTERVAL
init()