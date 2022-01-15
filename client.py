from cmath import sin
import sqlalchemy
import pandas as pd
from binance.client import Client

client = Client(api_key, api_secret)
engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')
df = pd.read_sql('BTCUSDT', engine)

#trendfollowing
#if the crypto was rising by x % -> BUY
#exit when profit is abone 0.15% or loss is crossing -0.15%

def strategy(entry, lookback, qty, open_position=False):
    while True:
        df = pd.read_sql('BTCUSDT', engine)
        lookbackperiod = df.iloc[-lookback:]
        cumret = (lookbackperiod.Price.pct_change() +1).cumprod() -1
        if not open_position:
            if cumret[cumret.last_valid_index()] > entry:
                order = client.create_order(symbol='BTCUDST', side='BUY', type='MARKET', quantity=qty)
                print(order)
                open_position = True
                break
    
    if open_position:
        while True:
            df = pd.read_sql('BTCUSDT', engine)
            sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit='ms')]

            if len(sincebuy) > 1:
                sincebuyret = (sincebuy.Price.pct_change()+1).cumprod() - 1
                last_entry = sincebuyret[sincebuyret.last_valid_indes()]
                if last_entry > 0.0015 or last_entry < -0.0015:
                    order = client.create_order(symbol='BTCUSDT', side='SELL', type='MARKET', quantity=qty)
                    print(order)
                    break

# Testing

strategy(0.001, 60, 0.001)
