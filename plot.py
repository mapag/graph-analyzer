import pandas as pd
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px

df = pd.read_csv('TA.csv')

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
traceMomentum = px.line(df['Momentum'], title='Momentum')
traceRSI = px.line(df['RSI'], title='RSI')

dataCandle = [traceCandle]
dataADX = [traceADX]
dataMomentum = [traceMomentum]
dataRSI = [traceRSI]

layoutCandle = {
    'title': 'Pattern recognition',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},
}

fig = dict(data=dataCandle, layout=layoutCandle)

plot(fig, filename='candlePatrons.html')
traceADX.show()
traceMomentum.show()
traceRSI.show()

df.to_csv('TA.csv')
print('Archivo generado.')


