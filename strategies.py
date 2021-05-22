import pandas as pd

df = pd.read_csv('TA.csv')

def rsiStrategy():
  amount = 1000 

  minRSI = 60
  maxRSI = 40

  precioCompra = 0
  precioVenta = 0

  for index, row in df.iterrows():
    if(row['RSI'] != 0): 
      if (row['RSI'] < minRSI):
        if(precioCompra == 0):
          precioCompra = row['close']
      if (row['RSI'] > maxRSI):
        precioVenta = row['close']
        if(precioCompra != 0):
          print(f'{precioVenta} - {precioCompra} = {precioVenta - precioCompra} ({round(((precioVenta - precioCompra)/precioVenta) * 100,2)})%')
          amount += amount * (((precioVenta - precioCompra)/precioVenta) * 100) / 100
          precioCompra = 0
          precioVenta = 0
  print('RESULTADO FINAL', amount)

rsiStrategy()