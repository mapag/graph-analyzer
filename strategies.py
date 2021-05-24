import pandas as pd
from numpy import diff
from dataGenerator import init
import datetime

df = pd.read_csv('TA.csv')

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
                    amount += amount * \
                        (((precioVenta - precioCompra)/precioVenta) * 100) / 100
                    precioCompra = 0
                    precioVenta = 0

def MexicanStrategy():
    y = []
    countExitoso = 0
    countFallido = 0
    tradeHistory = pd.DataFrame(columns=['fecha', 'amount', 'diferencia', 'tradePercentage'])
    amount = 10
    dydx = diff(df['Momentum'])
    hold = [False, 0]
    for index, elem in enumerate(dydx):
        try:
            if(elem > 0 and dydx[index + 1] < 0):
                if(df['ADX'][index] > 23 and df['close'][index] > hold[1]):
                    valCompra = hold[1]
                    valVenta = df['close'][index]
                    if(hold[0]):
                        tradePercentage = (((valVenta-valCompra)/max([valCompra, valVenta])))
                        diferencia = (amount * tradePercentage)
                        if(diferencia > 0):
                          countExitoso += 1
                        else:
                          countFallido += 1
                        amount += diferencia
                        new_row = pd.DataFrame([[round(amount, 2), round(diferencia,2), round(tradePercentage * 100, 2)]], columns=['amount', 'diferencia', 'tradePercentage'])
                        tradeHistory = tradeHistory.append(new_row, ignore_index=True)
                        hold[0] = False
                        hold[1] = 0
            elif (elem < 0 and dydx[index + 1] > 0):
                if(df['ADX'][index] > 23 and not hold[0]):
                    hold = [True, df['close'][index]]
        finally:
            continue
    fecha = str(datetime.datetime.now()).replace("-", "_").replace(":", "_").split(".")[0]
    tradeHistory.to_excel( fr'./out/{fecha}.xlsx', sheet_name= 'tradeHistory')
    print('Operaciones positivas', countExitoso)
    print('Operaciones negativas', countFallido)

MexicanStrategy()