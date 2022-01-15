import pandas as pd 
from binance.client import Client
import asyncio
from binance import BinanceSocketManager, AsyncClient
nest_asyncio.apply()

from sqlalchemy import create_engine

client = Client()
engine = create_engine('sqlite:///CryptoDB.db')

info = client.get_exchange_info()
symbols = [x['symbol'] for x in info['symbols']]
exclude = ['UP','DOWN','BEAR','BULL']
non_lev = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]
relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')]
multi = [i.lower + '@trade' for i in relevant]

def createframe(msg):
    df = pd.DataFrame([msg['data']])
    df = df.loc[:, ['s','E','p']]
    df.columns = ['symbol', 'Time', 'Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    return df

async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ms = bm.multiplex_socket(multi)
    async with ms as tcsm:
        while True:
            res = await tcsm.recv()
            if res:
                frame = createframe(res)
                frame.to_sql(frame.symbol[0], engine, if_exists='append', index=False)
    
    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

coins = ('BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','ADAUSDT')

def getminutedata(symbol, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', lookback + ' days ago UTC'))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    frame[['Open', 'High', 'Low', 'Close']] = frame[['Open', 'High', 'Low', 'Close']].astype(float)
    frame.Time = pd.to_datetime(frame.Time, unit='ms')
    return frame



    # await socket.__aenter__()
    # msg = await socket.recv()
    # frame = createframe(msg)
    # frame.to_sql('BTCUSDT')
    # print(msg)
