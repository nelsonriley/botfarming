#!/usr/bin/python2.7
import sys
import utility as ut
import utility_2 as ut2
import requests
import time
import socket
from pprint import pprint
from binance.client import Client
from binance.websockets import BinanceSocketManager

api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)
bm = BinanceSocketManager(client)

min_volume_btc = 0
datapoints_trailing = 0
minutes = 1
interval = str(minutes)+'m'

# limit symbols by 24hr volume
ut.update_symbol_list()
symbol_path = '/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz'
symbols_dict = ut.pickle_read(symbol_path)
symbols_filtered, symbol_list = ut2.get_trimmed_symbols(symbols_dict, min_volume_btc)
socket_list = []
for s in symbol_list:
    socket_list.append(s.lower()+'@ticker')
    ut.pickle_write('/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz', False)

print('symbols with volume > ', min_volume_btc, '=', len(socket_list))

def process_socket_pushes_tickers(msg):
    # close and restart the socket, if socket can't reconnect itself
    if 'e' in msg and msg['e'] == 'error':
        print('restarting socket in process_socket_pushes_tickers()')
        bm.close()
        conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes_tickers)
        bm.start()
    else:
        if 'stream' in msg and 'data' in msg:
            s = msg['stream'].split('@')[0].upper()
            ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
            current_price = float(msg['data']['c'])
            # ut.pickle_write(ticker_path, msg['data'])
            ut.pickle_write(ticker_path, current_price)

            if s == 'ETHBTC' and time.localtime().tm_sec == 0:
                current_price = float(msg['data']['c'])
                print('STILL ALIVE process_socket_pushes_tickers()', s, current_price, ut.get_time())
        else:
            print('ERROR: unexpected socket response in process_socket_pushes_tickers(), printing msg so we know what is going on')
            pprint(msg)

# start web socket > call back saves most recent data to disk
conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes_tickers)
bm.start()

# REFERENCE MSG SCHEMA

# {u'data': {u'A': u'480.00000000',
#           u'B': u'33.00000000',
#           u'C': 1517975250045,
#           u'E': 1517975250045,
#           u'F': 1209502,
#           u'L': 1231412,
#           u'P': u'16.579',
#           u'Q': u'841.00000000',
#           u'a': u'0.00028795',
#           u'b': u'0.00028683',
#           u'c': u'0.00028795',
#           u'e': u'24hrTicker',
#           u'h': u'0.00034857',
#           u'l': u'0.00023109',
#           u'n': 21911,
#           u'o': u'0.00024700',
#           u'p': u'0.00004095',
#           u'q': u'644.59358790',
#           u's': u'ENGBTC',
#           u'v': u'2184786.00000000',
#           u'w': u'0.00029504',
#           u'x': u'0.00024700'},
#  u'stream': u'engbtc@ticker'}