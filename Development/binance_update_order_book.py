#!/usr/bin/python2.7

# binance_update_order_book.py

import sys
import utility as ut
import requests
import time
import socket
from pprint import pprint
from binance.client import Client
from binance.websockets import BinanceSocketManager

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
s.close()

api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)
global bm
bm = BinanceSocketManager(client)

# limit symbols by 24hr volume
min_volume = 0 # 450
ut.update_symbol_list()
symbol_path = '/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz'
symbols = ut.pickle_read(symbol_path)
total_btc_coins = 0
symbols_trimmed = {}
global socket_list
socket_list = []
for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > min_volume:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol
        socket_list.append(s.lower()+'@depth20')
        ut.pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+s+'.pklz', False)

print('symbols with volume > ', min_volume, '=', len(socket_list))

# start order_book web socket > call back saves most recent data to disk
conn_key = bm.start_multiplex_socket(socket_list, ut.process_socket_pushes_order_book)
bm.start()
