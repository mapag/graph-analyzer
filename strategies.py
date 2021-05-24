import pandas as pd
from numpy import diff
from dataGenerator import init


def rsiStrategy():
    amount = 1000

    minRSI = 30  # Cambio un poco los limites para operar con los datos que vinieron de binance
    maxRSI = 70

    precioCompra = 0
    precioVenta = 0

    for index, row in df.iterrows():
        if(row['RSI'] != 0):
            if (row['RSI'] < minRSI):
                if(precioCompra == 0):
                    precioCompra = row['close']
            if (row['RSI'] > maxRSI):
                precioVenta = row['close']
                if(precioCompra != 0 and precioCompra != precioVenta):
                    print(
                        f'{precioVenta} - {precioCompra} = {precioVenta - precioCompra} ({round(((precioVenta - precioCompra)/precioVenta) * 100,2)})%')
                    amount += amount * \
                        (((precioVenta - precioCompra)/precioVenta) * 100) / 100
                    precioCompra = 0
                    precioVenta = 0
    print('RESULTADO FINAL', amount)


def MexicanStrategy():
    y = []
    count = []
    amount = 1000
    for index, row in df.iterrows():
        y.append(row['Momentum'])
        count.append(1)
    dydx = diff(y)/diff(count)
    hold = [False, 0]
    for index, elem in enumerate(dydx):
        try:
            if(elem > 0 and dydx[index + 1] < 0):
                if(df['ADX'][index] > 23):
                    valAnterior = hold[1]
                    hold[1] = df['close'][index]
                    if(hold[0]):
                        hold[0] = False
                        tradePercentage = (
                            ((valAnterior-hold[1])/max([valAnterior, hold[1]])))
                        diferencia = (amount * tradePercentage)
                        amount += diferencia
                        print(round(
                            amount, 2), f'|| {round(diferencia,2)} ||', f'{round(tradePercentage * 100, 2)}%')
            elif (elem < 0 and dydx[index + 1] > 0):
                if(df['ADX'][index] > 23):
                    hold = [True, df['close'][index]]
        finally:
            continue


try:
    df = pd.read_csv('TA.csv')
except IOError:
    init()
    print("File not accessible")
MexicanStrategy()
