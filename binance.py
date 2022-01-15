import pandas as pd 
import sqlalchemy
from binance.client import Client
from binance import BinanceSocketManager

client = Client(api_key, api_secret)

bsm = BinanceSocketManager(client)
socket = bsm.trade_socket('BTCUSDT')

while True:
    await socket.__aenter__()
    msg = await socket.recv()
    frame = createframe(msg)
    frame.to_sql('BTCUSDT')
    print(msg)
