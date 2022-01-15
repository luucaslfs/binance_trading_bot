import pandas as pd 
#from tdqm import tdqm
from sqlalchemy import create_engine
from binance import Client
from binance import BinanceSocketManager

client = Client()

coins = ('BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','ADAUSDT','XRPUSDT','DOTUSDT','LUNAUSDT',
  'DOGEUSDT','AVAXUSDT','SHIBUSDT','MATICUSDT','LTCUSDT','UNIUSDT','ALGOUSDT','TRXUSDT',
         'LINKUSDT','MANAUSDT','ATOMUSDT','VETUSDT')



# bsm = BinanceSocketManager(client)
# socket = bsm.trade_socket('BTCUSDT')



def getminutedata(symbol, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', lookback + ' days ago UTC'))
    frame = frame.iloc[:,5]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    frame[['Open', 'High', 'Low', 'Close']] = frame[['Open', 'High', 'Low', 'Close']].astype(float)
    frame.Time = pd.to_datetime(frame.Time, unit='ms')
    return frame

getminutedata('BTCUSDT', '1')
    # await socket.__aenter__()
    # msg = await socket.recv()
    # frame = createframe(msg)
    # frame.to_sql('BTCUSDT')
    # print(msg)
