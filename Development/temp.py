#!/usr/bin/python2.7
import sys
print('python', sys.version)

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime
import utility as ut
import functions_financial as fn

# A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark
from binance.client import Client
from binance.websockets import BinanceSocketManager
api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)
bm = BinanceSocketManager(client)

socket_list = ['neobtc@kline_1m', 'neobtc@depth20', 'wingsbtc@kline_1m', 'wingsbtc@depth20']
def process_socket_pushes(msg):
    if 'e' in msg and msg['e'] == 'error':
        # close and restart the socket, if socket can't reconnect itself
        print('restarting process_socket_pushes(msg)')
        bm.close()
        conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes)
        bm.start()
    else:
        # if 'kline_1m' in msg['stream']:
        #     print('--------------------------------------', msg['stream'], ut.get_time())
        #     pprint(msg['data'])
        #     print('--------------------------------------')
        if 'depth' in msg['stream']:
            # print('--------------------------------------', msg['stream'], ut.get_time())
            # # pprint(msg['data'])
            # # available: asks + bids
            # # 'asks': [[u'0.01264000', u'18.92000000', []],
            # #          [u'0.01265300', u'0.20000000', []],
            # print('--------------------------------------')
            symbol = msg['stream'].split('@')[0].upper()
            ut.pickle_write('./recent_order_book/'+symbol+'.pklz', msg['data'])

conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes)
bm.start()
time.sleep(15)
bm.close()














































#########################check if symbols are in our list
# symbols = ut.pickle_read('./binance_btc_symbols.pklz')
# symbol_list = []
# for s in symbols:
#     symbol = symbols[s]
#     symbol_list.append(s)
#     if float(symbol['24hourVolume']) > 450:
#         if s == 'ASTBTC':
#             print('----', s)
# print('symbol_count', len(symbol_list))
# i = 0
# symbols2 = ut.pickle_read('./binance_btc_symbols.pklz')
# for s in symbols2:
#     if symbol_list[i] != s:
#         print('wtf!', s)
#     i += 1
#
# sys.exit()
# ####################################################

print('done')