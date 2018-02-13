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
from binance.client import Client


######
symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
    
total_btc_coins = 0
symbols_trimmed = {}

for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol
        

total_gain = 0
total_symbols = 0
look_back_array = [1,2,4]
for s in symbols_trimmed:
    symbol = symbols_trimmed[s]
    print(symbol['symbol'])
    total_symbols += 1
    
    for look_back in look_back_array:
        look_back_optimized = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '_V12.pklz')
        if look_back_optimized != False:
            print(symbol['symbol'], look_back_optimized['look_back'], look_back_optimized['gain'], look_back_optimized['wins'], look_back_optimized['losses'])
            print(symbol['symbol'], look_back_optimized['optimal_buy_factor'], look_back_optimized['optimal_sell_factor'], look_back_optimized['optimal_band_factor'], look_back_optimized['optimal_increase_factor'], look_back_optimized['optimal_minutes_until_sale'])
            if look_back_optimized['gain'] > 0:
                total_gain += look_back_optimized['gain']
            
    
print('total_gain', total_gain)
print('total_symbols', total_symbols)






# length = '1m'

# result = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/optimal_for_2.pklz')

# pprint(result)


# file_path = '/home/ec2-user/environment/botfarming/Development/program_state_30m/program_state_30m_0_GXSBTC.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# pprint(data_points)
# f.close()


#ut.append_or_create_data('/home/ec2-user/environment/botfarming/Development/binance_' + length + '_trades/'+ length + '_trade_data', [.5,'YOMAMA',ut.get_time()])


# file_path = '/home/ec2-user/environment/botfarming/Development/binance_30m_trades/30m_trade_data'
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
