#!/usr/bin/python2.7
import sys
import requests
import time
from pprint import pprint
import numpy
import os
import pickle
import gzip
import datetime
from binance.client import Client
import json
import math
from urlparse import urlparse
from threading import Thread
import threading
import httplib
from Queue import Queue
import re
import linecache
import sys
import functions_financial as fn
import utility as ut
import socket
import random

# A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark
from binance.client import Client
from binance.websockets import BinanceSocketManager
api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)
global bm
bm = BinanceSocketManager(client)

# get symbols & update if older than 1 hour
symbol_path = './botfarming/Development/binance_btc_symbols.pklz'
last_modified_stamp = int(os.path.getmtime(symbol_path))
if last_modified_stamp < int(time.time()) - 60 * 60:
    ut.update_symbol_list()

# limit symbols by 24hr volume
symbols = ut.pickle_read(symbol_path)
total_btc_coins = 0
symbols_trimmed = {}
for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol

global socket_list
socket_list = []
symbol_list = []
for s in symbols_trimmed:
    symbol = symbols_trimmed[s]
    # reset current_state 'status' to 'monitoring' (not 'buying_and_selling')
    # state_path = './botfarming/Development/program_state_1m/program_state_1m_1000_' + s + '.pklz'
    # current_state = ut.pickle_read(state_path)
    # if current_state is False:
    #     ut.pickle_write(state_path, {'status': 'monitoring'}, '******could not write state superbot 1******')
    # else:
    #     current_state['status'] = 'monitoring'
    #     ut.pickle_write(state_path, current_state, '******could not write state superbot 2******')
    # add orderbook symbol params to socket_params
    socket_list.append(s.lower()+'@depth20')
    symbol_list.append(s)

print('symbols with volume > 450 =', len(symbol_list))
# start order_book web socket > call back saves most recent data to disk
conn_key = bm.start_multiplex_socket(socket_list, ut.process_socket_pushes_order_book)
bm.start()
# start worker_get_klines_on_the_minute() thread
t = Thread(target=ut.worker_get_klines_on_the_minute, args=['1m', symbol_list, 230])
t.start()

# delay to start 5s past the minute (when we have candles)
secs = time.localtime().tm_sec
delay = 65 - secs
print('start superbot in', delay, 'seconds')
time.sleep(delay)
print('starting super bot now', ut.get_time())

# if current_state == dict, some sort of buying & selling >> always starts with buy(), always needs to end thread with sys.exit()
# if current_state == False, monitoring


# while True:
#     for s in symbols_trimmed:
#         # if s == 'ETCBTC':
#         #     print(ut.get_time()) # >> it is plenty fast  (10 per sec or so)
#         # current_state = load_current_state(symbol=s, file_number=1000, length='1m')
#         # if isinstance(current_state, dict):
#         #     print('loading state to sell coin..', current_state['symbol'])
#         #     ut.buy_coin_from_state(current_state)
#         #     continue
#         current_state = { 'status': 'monitoring' }
#         if current_state['status'] == 'monitoring':
#             # get order book & candles from disk (kept up to date)
#             order_book_path = './botfarming/Development/recent_order_book/'+s+'.pklz'
#             order_book = ut.pickle_read(order_book_path)
#             if order_book != False:
#                 current_price = float(order_book['bids'][0][0])
#                 candles_path = './botfarming/Development/recent_klines/'+s+'_1m.pklz'
#                 trailing_candles = ut.pickle_read(candles_path)
#                 buy_params = ut.evaluate_buy(s, trailing_candles, current_price)
#                 if buy_params['do_buy'] == True:
#                       print('buy', s, '!')
#                 #     t = ut.new_buy_and_sell_thread(buy_params) # TODO ryan
#                 #     t.start() # thread saves current state and exits() itself
#     time.sleep(.1)

# emerging architecure
# web socket to update prices / order_book
# thread update klines every min on the min (via spawning other threads)
# main loop # cancels threads when coin is free again
# >>> thread per buy initiated through sold # always frees coin eventually
