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
import utility_3 as ut
import json
import math
from binance.client import Client


small_float = 35.1234/100000000
print(small_float)
print(ut.round_down(small_float,8))

print(ut.float_to_str(ut.round_down(small_float,8)))

print(ut.float_to_str(small_float,ut.get_length_of_float(small_float)))

small_float_2 = 14.2

print(ut.get_length_of_float(small_float_2))

print(ut.float_to_str(small_float_2,ut.get_length_of_float(small_float_2)))

# order_book_history = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/1m_0_1521906576_binance_all_trades_history.pklz')

# pprint(order_book_history)

# save_data_until = int(time.time()) + 30*60
# print ut.get_readable_time(save_data_until)

# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/ETHBTC_should_save', save_data_until)

# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/ETHBTC_already_saved', False)

# should_save = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/ETHBTC_should_save')

# print('should_save', should_save, ut.get_readable_time(should_save))

# if should_save != False and should_save > int(time.time()):
#     print('hi')
# stop_trading_time = int(time.time()) + 60*60*12

# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_ETHBTC', stop_trading_time)
    


# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/1m_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/5m_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/15m_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/30m_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/1h_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/2h_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/6h_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/12h_stop_trading', True)
# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/1d_stop_trading', True)

# stop_trading = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/1m_stop_trading')

# if stop_trading == True:
#     print('should stop trading')

# look_back_gains = {}
# look_back_gains[1] = .2
# look_back_gains[2] = .1
# look_back_gains[4] = .4
# look_back_gains[5] = .15
# look_back_gains[7] = .3
# look_back_gains[9] = .12

# look_back_gains_sorted = sorted(look_back_gains, key=look_back_gains.get, reverse=True)

# pprint(look_back_gains_sorted)



# length = '4h'

# minutes = int(length[:1])*60

# print(minutes)



# order_book = ut.get_order_book_local('FUELBTC')

# pprint(order_book)

# result = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/program_state_1m/program_state_1m_0_DLTBTC_V0.pklz')

# pprint(result)
# result['executedQty'] = 55963.0

# ut.pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_1m/program_state_1m_0_RPXBTC.pklz', result)

# result = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/program_state_1m/program_state_1m_0_RPXBTC.pklz')

# pprint(result)

# order_book = ut.get_order_book_local('GTOBTC')
# pprint(order_book)
# total_bitcoin_of_bids = 0
# max_bitcoin_in_front = .02
# for asks in order_book['asks']:
#     total_bitcoin_of_bids += float(asks[0])*float(asks[1])
#     if total_bitcoin_of_bids > max_bitcoin_in_front:
#         price_to_buy = ut.float_to_str(round(float(asks[0]) - .00000001, 8))
#         break
# print('price_to_buy', price_to_buy)

# time.sleep(1)
# order_book = ut.get_order_book_local('GTOBTC')
# pprint(order_book)
# total_bitcoin_of_bids = 0
# max_bitcoin_in_front = .2
# for asks in order_book['asks']:
#     total_bitcoin_of_bids += float(asks[0])*float(asks[1])
#     if total_bitcoin_of_bids > max_bitcoin_in_front:
#         price_to_buy = ut.float_to_str(round(float(asks[0]) - .00000001, 8))
#         break
# print('price_to_buy', price_to_buy)


    # # pprint(order_book)
    # # bids & asks.... 0=price, 1=qty
    # first_ask = float(order_book['asks'][0][0])
    # second_ask = float(order_book['asks'][1][0])
    # first_bid = float(order_book['bids'][0][0])
    # second_price_to_check = first_ask + 3*current_state['min_price']
    # second_price_to_buy = float_to_str(round(second_ask - current_state['min_price'], current_state['price_decimals']))
    # price_to_buy = float_to_str(round(first_ask - current_state['min_price'], current_state['price_decimals']))
    # # print(first_ask)
    # # print(price_to_buy)
    # return price_to_buy,first_ask, second_price_to_buy, second_ask, second_price_to_check, first_bid



# length = '1m'




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
