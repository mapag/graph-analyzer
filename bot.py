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

KLINESURL = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m'

def recognize_candlestick(df):
    amount = 1000
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

    candle_names = [candle for candle in candle_names if candle not in exclude_items]

    # create columns for each candle
    for candle in candle_names:
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)

    for index, row in df.iterrows():
        #  no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
              # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            try:
              diff = float(df['close'][index]) - float(df['close'][index+1])
              percentage = diff / float(df['close'][index]) * 100
              amount += amount * percentage / 100
            finally:
              continue
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
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
                try:
                  diff = float(df['close'][index]) - float(df['close'][index+1])
                  percentage = diff / float(df['close'][index]) * 100
                  amount += amount * percentage / 100
                finally: 
                  continue
    # clean up candle columns
    cols_to_drop = candle_names
    df.drop(cols_to_drop, axis = 1, inplace = True)

    # print(amount)
    # print(f'{((amount - 1000) / 1000) * 100}% de ganancia')
    return df

candles = requests.get(KLINESURL).json()

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
df.pop('openTime')
df.pop('closeTime')
df.pop('')

recognize_candlestick(df)

o = df['open'].astype(float)
h = df['high'].astype(float)
l = df['low'].astype(float)
c = df['close'].astype(float)
p = df['candlestick_pattern'].map(lambda x: x.replace('CDL','').replace('_Bull',' ALZA').replace('_Bear',' BAJA').replace('NO_PATTERN','NO HAY PATRON').replace('2','').replace('3',''))

traceCandle = go.Candlestick(
            open=o,
            high=h,
            low=l,
            close=c,
            text=p)

traceADX = px.line(df['ADX'], title='ADX')
          
dataCandle = [traceCandle]
dataADX = [traceADX]

layoutCandle = {
    'title': 'Pattern recognition',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},
}

fig = dict(data=dataCandle, layout=layoutCandle)

plot(fig, filename='candlePatrons.html')
traceADX.show()

df.to_csv('TA.csv')
print('Archivo generado.')


