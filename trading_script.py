import asyncio
from tkinter import Frame
from binance import BinanceSocketManager, AsyncClient
import datetime as dt
from sqlalchemy import create_engine
import pandas as pd
from binance.client import Client
from api_keys import api_key, secret_key

client = Client(api_key, secret_key)
engine = create_engine('sqlite:///CryptoDB.db')
symbols = pd.read_sql('SELECT name FROM sqlite_master WHERE type ="table"', engine).name.to_list()

# Pulling prices from last n minutes
def qry(symbol, lookback:int):
    now = dt.datetime.now() - dt.timedelta(hours=1) # binance time
    before = now - dt.timedelta(minutes=lookback)
    qry_str = f"""SELECT * FROM '{symbol}' WHERE TIME >= '{before}'"""
    return pd.read_sql(qry_str, engine)

print(qry('BTCUSDT', 5))

# Calculating acumulative return/losses
rets = []
for symbol in symbols:
    prices = qry(symbol,3).Price
    cumret = (prices.pct_change() + 1).prod() - 1
    rets.append(cumret)

# Calculating LOT_SIZES based in investment_amt and top_coin prize
investment_amt = 300
top_coin = symbols[rets.index(max(rets))]
info = client.get_symbol_info(symbol=top_coin)
Lotsize = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
prize = float(client.get_symbol_ticker(symbol=top_coin)['price'])
buy_quantity = round(investment_amt/prize, len(str(Lotsize).split('.')[1]))

# Buying condition
free_usd = [i for i in client.get_account()['balances'] if i['asset'] == 'USDT'][0]['free']
if float(free_usd) > investment_amt:
    order = client.create_order(symbol=top_coin,side='BUY',
    type='MARKET',quantity=buy_quantity)
else:
    print('order has not been executed. You are already invested')
    quit()

buyprice = float(order['fills'][0]['price'])

def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['s','E','p']]
    df.columns = ['symbol', 'Time', 'Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    return df

# Trading strategy, stop loss, etc
async def main(coin):
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket(coin)
    async with ts as tcsm:
        while True:
            res = await tcsm.recv()
            if res:
                frame = createframe(res)
                if frame.Price[0] < buyprice * 0.97 or frame.Price[0] > 1.005 * buyprice:
                    order = client.create_order(symbol=coin,
                    side='SELL',
                    type='MARKET',
                    quantity=buy_quantity)
                    print(order)
                    loop.stop()
    await client.close_connection()

    if __name__ == "__main__":

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(top_coin))


# In order to run this script as cronjob(linux) you must follow these steps:
#   $ where python3 (local do interpreter)
#   $ env EDITOR=nano crontab -e
#