#!/usr/bin/python2.7
import sys
print 'python', sys.version

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import utility as ut
import json
import math

length = '1m'

file_path = './binance_1m_trades/1m_trade_data'
f = gzip.open(file_path,'rb')
data_points = pickle.load(f)
pprint(data_points)
f.close()



# file_path = './program_state_30m/program_state_30m_0_GXSBTC.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# pprint(data_points)
# f.close()


#ut.append_or_create_data('./binance_' + length + '_trades/'+ length + '_trade_data', [.5,'YOMAMA',ut.get_time()])


# file_path = './binance_30m_trades/30m_trade_data'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# pprint(data_points)
# f.close()






# from binance.client import Client

# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)

# depth = client.get_order_book(symbol='BNBBTC')
# pprint(depth)
# print(depth['bids'][0][0])
