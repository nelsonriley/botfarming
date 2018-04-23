#!/usr/bin/python2.7
import sys
import pickle
import gzip
import time
import os
import datetime
from pprint import pprint
import utility as ut
import utility_2 as ut2
import numpy
from binance.client import Client
from binance.websockets import BinanceSocketManager

from urlparse import urlparse
from threading import Thread
import threading
import httplib
from Queue import Queue
import requests
import math
import binance_optimization_utility as bou
import functions_financial as fn

# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())

################################################################################ PLAY WITH CODE

api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)

acct_info = client.get_account()
prices = client.get_all_tickers()
# pprint(acct_info)
# pprint(prices)

## earlier in time
# ryan_btc_before_bots = 6.21201378 + 3.18120133 + 0.13423430603 + 0.20798 - 0.61213 + 2.38472954 + 2.21955718 + 2.11721460 # 9.23021912
# ryans_symbols = { 'BNB': 494.00943559 }
## 20180422
ryan_btc_before_bots = 6.21201378 + 3.18120133 + 0.13423430603 + 0.20798 - 0.61213 + 2.38472954 + 2.21955718 + 2.11721460 - 4.07636575
ryans_symbols = { 'BNB': 210.21609545, 'XVG': 409685 }

coins_held = 0
bot_value = 0
for balance in acct_info['balances']:
    if balance['asset'] == 'BTC':
        bot_value += float(balance['free'])
        print('BTC holding', float(balance['free']))
        coins_held += 1
    elif float(balance['free']) > 0 or float(balance['locked']) > 0:
        for price in prices:
            if price['symbol'] == balance['asset'] + 'BTC':
                qty = float(balance['free']) + float(balance['locked'])
                if balance['asset'] in ryans_symbols:
                    qty = qty - ryans_symbols[balance['asset']]
                coin_value = float(price['price']) * qty
                if coin_value > 0.05:
                    print float(balance['locked']), float(balance['free']), balance['asset'], coin_value
                bot_value += coin_value
                coins_held += 1
                break
        pass

profit = bot_value - ryan_btc_before_bots
print('coins_held', coins_held)
print('bot_value', bot_value)
print('ryan_btc_before_bots', ryan_btc_before_bots)
print('profit', profit, profit * 7000)




# file_path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop_ENHANCED.pklz'
# trades = ut.pickle_read(file_path)


################################################################################ GET RESULTS for 24hr_1min_drop
# file_path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop_ENHANCED.pklz'
# trades = ut.pickle_read(file_path)
# print('trades', len(trades))
# profit_usd = 0
# trades_positive = 0
# trades_positive_sum = 0
# trades_negative = 0
# trades_negative_sum = 0
# trades_passing_all_tests = 0
# trades_reporting = 0
# for i, t in enumerate(trades):
#     # 20180220 = 62, 275
#     # 20180221 = 310 to 361 morning session ($54 profit, $70 in account, 30% volume)
#         # 361 to 393, 0.4 session, made $13 negative $19 & positive $35
#     # 20180222 393 to 781 = 388
#     if i >= 781:
#         # if 'symbol' in t:
#         #     print('s', t['symbol'])
#         trades_reporting += 1
#         profit_usd += t['live']['profit_usd']
#         if t['live']['profit_usd'] >= 0:
#             trades_positive += 1
#             trades_positive_sum += t['live']['profit_usd']
#         else:
#             trades_negative += 1
#             trades_negative_sum += t['live']['profit_usd']
#         if t['tests']['all_tests_pass'] == True:
#             trades_passing_all_tests += 1

# print('trades_reporting', trades_reporting)
# print('profit_usd', profit_usd)
# # periods_in_24 = (24/8)
# # print('profit_usd_24', profit_usd * periods_in_24 )
# # print('profit_usd_365', profit_usd * periods_in_24 * 365 )

# # print('profit_usd_full_24', profit_usd * 10 * periods_in_24)
# # print('profit_usd_full_365', profit_usd * 10 * periods_in_24 * 365)

# print('trades_positive', trades_positive)
# print('trades_negative', trades_negative)
# print('trades_positive_sum', trades_positive_sum)
# print('trades_negative_sum', trades_negative_sum)
# print('trades_passing_all_tests', trades_passing_all_tests)




################################################################################ SET CURRENT STATE to FALSE for ALL
# symbol_data = requests.get("https://api.binance.com/api/v1/exchangeInfo").json()
# for symbol in symbol_data['symbols']:
#     if symbol['quoteAsset'] == 'BTC':
#         s = symbol['symbol']
#         print(s)
#         file_number = 2000
#         interval = '1m'
#         version = '24hr_1min_drop_v0'
#         current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + interval + '/program_state_' + interval + '_' + str(file_number) + '_' + s + '_V' + version + '.pklz'
#         ut.pickle_write(current_state_path, False)


################################################################################ TEST PASSING PROFIT % VALUES
# tests = {}
# sim = {}
# live = {}
# sim['profit_percent'] = -0.0021416847936521896
# live['profit_percent'] = -0.002253098009763497
# sim['profit_percent'] =  -0.001370699821262526
# live['profit_percent'] = -0.00028752156411747165
# passing_profit_percent_range = abs(0.2 * sim['profit_percent']) # based on profit percent
# passing_profit_percent_range = abs(0.002 * 0.2) # 0.0004 based on absolute value, 20% of 0.2% (the avg gain)
# passing_profit_percent_range = abs(0.0011) # 0.0004 based on absolute value, 20% of 0.2% (the avg gain)
# top_bound = abs(sim['profit_percent']) + passing_profit_percent_range
# bottom_bound = abs(sim['profit_percent']) - passing_profit_percent_range
# live_sim_same_side_of_zero = sim['profit_percent'] <= 0 and live['profit_percent'] <= 0 or sim['profit_percent'] > 0 and live['profit_percent'] > 0
# tests['profit_in_range'] = live_sim_same_side_of_zero and abs(live['profit_percent']) >= bottom_bound and abs(live['profit_percent']) <= top_bound

# print(tests['profit_in_range'])





################################################################################ ACCURATE ROUNDING
# base_qty_for_order = ut.float_to_str(round(18.345, 0))
# print('base_qty_for_order', base_qty_for_order)
# base_qty_for_order = ut.float_to_str(0.00945, 2)
# print('base_qty_for_order', base_qty_for_order)
# base_qty_for_order = ut.float_to_str(0.00945, 3)
# print('base_qty_for_order', base_qty_for_order)



################################################################################ MAKE A LIMIT ORDER
# WTF is min_notional etc?
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#filters
# s = 'TRXBTC'
# quantity_to_buy = 1000
# price_to_buy = 0.00000174
# notional = quantity_to_buy * price_to_buy
# min_notional = 0.001
# print('will pass MIN_NOTIONAL filter:', notional > min_notional)

# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)

# price_to_buy = ut.float_to_str(price_to_buy)
# buy_order = client.order_limit_buy(symbol=s, quantity=quantity_to_buy, price=price_to_buy)
# print('buy_order')
# pprint(buy_order)
# time.sleep(5)
# cancelled_order = client.cancel_order(symbol=s, orderId=buy_order['orderId'])
# print('cancelled_order')
# pprint(cancelled_order)





################################################################################ DEFINE A READABLE STOP TIME in EPOCH
# t = datetime.datetime(2018, 2, 14, 18, 15)
# s = int((t - datetime.datetime(1970, 1, 1)).total_seconds()) + 7 * 60 * 60
# epoch_now = int(time.time())
# diff = epoch_now - s
# print('diff', diff)
# print(ut.get_readable_time(int(time.time()+15*60)))



################################################################################ ALWAYS USE FLOATS WHEN DIVIDING
# print(1.0/(1/3.0), 'ok')
# print(1.0/(1/3.0), 'ok')
# print('1.0/(1/3)', 'will ERROR: float division by zero')




################################################################################ TEST FILE PATH WRITES ON AWS
# path = '/home/ec2-user/environment/botfarming/Development/botfarming/Development/__test_pickle'
# ut.pickle_write(path, 'it works!!!')
# saved = ut.pickle_read(path)
# print(saved)


################################################################################ TEST TICKER WEB SOCKET (is it current price?)
# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)
# bm = BinanceSocketManager(client)

# def process_ticker_socket(msg):
#     print('-----------------------------------')
#     print(msg['stream'], msg['data']['c'])

# conn_key = bm.start_multiplex_socket(['neobtc@ticker'], process_ticker_socket)
# bm.start()




################################################################################ INVESTIGATE RELATIVE / ABSOLUTE PATHS ON AWS
# print(os.curdir)
# print(os.getcwd())
# print(os.path.isdir('/home/ec2-user/environment/botfarming/Development/recent_tickers/'))

# def get_current_price_from_ticker(s):
#     ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
#     ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
#     ticker = ut.pickle_read(ticker_path)
#     current_price = float(ticker['c'])
#     return current_price
    
# s = 'ENJBTC'
# price = ut2.get_current_price_from_ticker(s)
# print(price)

# ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
# ticker = ut.pickle_read(ticker_path)
# pprint(ticker)

# while True:
#     price = ut2.get_current_price_from_ticker(s)
#     print(s, price)
#     time.sleep(0.3)



################################################################################ GET KLINES FROM BINANCE API
# end_time = int(time.time())*1000
# start_time = (end_time-60*1000*2)
# s = 'ETHBTC'
# interval = '1m'
# url = 'https://api.binance.com/api/v1/klines?symbol='+ s +'&interval='+interval+'&startTime='+str(start_time)+'&endTime='+str(end_time)
# print(url)
# # data = requests.get(url).json()




################################################# save 24hr data & make folder
# epoch_now = int(time.time())
# epoch_24hrs_ago = epoch_now - 24*60*60
# end = epoch_now
# start = epoch_24hrs_ago - datapoints_trailing*60
# readable_time_now = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y-%m-%d_%H:%M')
# readable_time_24hrs_ago = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y-%m-%d_%H:%M')
# folder = readable_time_24hrs_ago + '_to_' + readable_time_now
# print(folder)





################################################# STUFF / INIT EMPTY ARRAY @ FILE PATH
# file_path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop_ENHANCED.pklz'
# ut.pickle_write(file_path, [])
# file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop.pklz'
# ut.pickle_write(file_path_all_trades, [])
# file_path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_attempts.pklz'
# ut.pickle_write(file_path, [])
# file_path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history.pklz'
# ut.pickle_write(file_path, [])
# print(ut.pickle_read(file_path))


# print(datetime.datetime.fromtimestamp(int(time.time())-7*60*60).strftime('%Y-%m-%d %H:%M:%S'), int(time.time()))
# print(datetime.datetime.fromtimestamp(math.floor(time.time())-7*60*60).strftime('%Y-%m-%d %H:%M:%S'), int(time.time()))

# while True:
#     datapoints_trailing = 230
#     minutes = 1
#     end_time = int(time.time())*1000
#     start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
#     url = 'https://api.binance.com/api/v1/klines?symbol=NEOBTC&interval=1m&startTime='+str(start_time)+'&endTime='+str(end_time)
#     data = requests.get(url).json()
#     print(ut.get_time(), ut.get_readable_time(data[-1][0]), ut.get_readable_time(data[-1][6]))
#     time.sleep(0.2)



# while True:
#     order_book = globals()['ETHBTC_order_book']
#     print('order_book', order_book)
#     current_price = float(order_book['bids'][0][0])
#     print('current_price', current_price)
#     time.sleep(2)






############################################ How to Exit Threads

# def testexit_b():
#     while True:
#         print('---B')
#         sys.exit()

# def testexit():
#     while True:
#         print('---1')
#         time.sleep(2)
#         print('---2')
#         testexit_b()
#         time.sleep(2)
#         # sys.exit()

# t = Thread(target=testexit)
# t.start()
# # tt = Thread(target=testexit)
# # tt.start()
# # t.join() # join is bad, makes it run as if it was synchronous not asynchronous
# # tt.join()
# print '-------------Sub thread started'
# time.sleep(7)
# print '-------------Exiting main thread'
# sys.exit()





############################################ Detect Milliseconds vs Seconds for Time Stamp
# stamp = 1517159488
# stamp2 = 1517159488 * 1000
# if len(str(stamp2)) > 10:
#     print 'stamp2 is milliseconds'
# if len(str(stamp)) > 10:
#     print 'stamp is milliseconds'
# sys.exit()







############################################ Get/Save Candles for Muliple Symbols every minute on the minute

# def worker_get_klines_on_the_minute(interval, symbol_list, datapoints_trailing):
#     while True:
#         minutes = 1
#         secs = time.localtime().tm_sec
#         delay = 60 - secs
#         print 'start threads to fetch klines in', delay, 'seconds'
#         time.sleep(delay)
#         end_time = int(time.time())*1000
#         start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
#         print 'start threads to fetch klines now', ut.get_time()
#         for s in symbol_list:
#             t = Thread(target=worker_get_and_save_klines, args=[interval, s, start_time, end_time])
#             t.start()
#         time.sleep(5)

# def worker_get_and_save_klines(interval, symbol, start_time, end_time):
#     url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol +'&interval='+interval+'&startTime='+str(start_time)+'&endTime='+str(end_time)
#     data = requests.get(url).json()
#     ut.pickle_write('/home/ec2-user/environment/botfarming/Development/recent_klines/'+symbol+'_'+interval+'.pklz', data)
#     # print first candle open & last candle open as readable
#         # print('-------------candle 0')
#         # print symbol, ut.get_readable_time(data[0][0])
#         # print('-------------candle -1')
#         # print symbol, ut.get_readable_time(data[-1][0])
#     sys.exit() # exit the thread

# t = Thread(target=worker_get_klines_on_the_minute, args=['1m', ['NEOBTC', 'WINGSBTC'], 230])
# t.start()








############################################ Get/View Trade History Array
# file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history.pklz'
# # empty our trades array
#     # ut.pickle_write(file_path_all_trades, [])
#     # sys.exit()

# data = ut.pickle_read(file_path_all_trades)
# print('trade count', len(data))
# profit_btc_total = 0
# trade_count = 0
# trades_negative = 0
# trades_positive = 0
# last_trade = {}
# start_time_epoch = 1516918780
# end_time_epoch = None
# end_time_epoch_is_last_trade = True
# for d in data:
#     start_good = d['time_buy_epoch'] >= start_time_epoch
#     end_good = d['time_end_epoch'] <= end_time_epoch
#     if start_good:
#         profit_btc_total += d['profit_btc']
#         if d['profit_btc'] > 0:
#             trades_positive += 1
#         else:
#             trades_negative += 1
#         trade_count += 1
#         print('---------------------------------------------- TRADE', trade_count)
#         print('symbol', d['symbol'])
#         print('invested_btc', d['invested_btc'])
#         print('profit_btc', d['profit_btc'])
#         print('profit_percent', d['profit_percent'])
#         print('time_buy_human', d['time_buy_human'])
#         print('time_buy_epoch', d['time_buy_epoch'])
#         print('time_end_human', d['time_end_human'])
#         print('time_end_epoch', d['time_end_epoch'])
#         print('look_back', d['look_back'])
#         print('largest_bitcoin_order', d['largest_bitcoin_order'])
#         print('part_of_bitcoin_to_use', d['part_of_bitcoin_to_use'])
#         print('volume_ten_candles_btc', d['volume_ten_candles_btc'])
#         print('volume_ten_candles_ratio', d['volume_ten_candles_ratio'])
#         print('volume_twentyfour_hr_btc', d['volume_twentyfour_hr_btc'])
#         print('volume_twentyfour_hr_ratio', d['volume_twentyfour_hr_ratio'])
#         if 'price_to_buy' in d['current_state']:
#             print('price_to_buy', ut.float_to_str(d['current_state']['price_to_buy']))
#         print('price_to_sell', ut.float_to_str(d['current_state']['price_to_sell']))
#         print('price_to_sell_2', ut.float_to_str(d['current_state']['price_to_sell_2']))
#         print('price_to_sell_3', ut.float_to_str(d['current_state']['price_to_sell_3']))
#         if end_time_epoch_is_last_trade:
#             end_time_epoch = d['time_end_epoch']

# print('---------------------------------------------- STATS')
# profit_btc_total += 0.1 # adjust for whack trade1 14 'INSBTC'
# bitcoin_value_usd = 11000

# print('profit_btc_total', profit_btc_total)
# print('trade_count', trade_count)
# print('trades_positive', trades_positive)
# print('trades_negative', trades_negative)
# print('profit_dollars', profit_btc_total * bitcoin_value_usd)
# elapsed_seconds = float(end_time_epoch - start_time_epoch)
# elapsed_minutes = float(elapsed_seconds / 60.0)
# elapsed_hours = float(elapsed_seconds / 60.0 / 60.0)
# elapsed_days = float(elapsed_seconds / 60.0 / 60.0 / 24.0)
# print('elapsed_hours', elapsed_hours)
# print('elapsed_days', elapsed_days)
# profit_per_day_btc = 1 / elapsed_days * profit_btc_total
# profit_per_hour_btc = 1 / elapsed_hours * profit_btc_total
# profit_per_year_btc = profit_per_day_btc * 365
# profit_per_day_usd = profit_per_day_btc * bitcoin_value_usd
# profit_per_hour_usd = profit_per_hour_btc * bitcoin_value_usd
# profit_per_year_usd = profit_per_year_btc * bitcoin_value_usd
# print('profit_per_day_usd', profit_per_day_usd)
# print('profit_per_year_usd', profit_per_year_usd)

####NEED TO FIX
    # python 2.7.6 (default, Oct 26 2016, 20:30:19)
    # [GCC 4.8.4]
    # ('running bot', 0, 'of', 12, '1m')
    # ('buy', u'INSBTC', 'look back', 4)
    # ('max price', 0.00044920732139999995)
    # could not cancel buy order
    # could not cancel buy order
    # could not cancel buy order
    # ('selling..', u'INSBTC', '2018-01-25 19:20:56')
    # ('selling at price level 1', u'INSBTC')
    # ('price_to_sell_min', 0.0004561720659)
    # ('selling at price level 2', u'INSBTC')
    # ('price_to_sell_min', 0.0004524895467)
    # APIError(code=-2010): Account has insufficient balance for requested action. **********************
    # EXCEPTION IN (/home/nelsonriley/Development/utility.py, LINE 345 "sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_2'], current_sta
    # te['minutes_until_sale_2'])"): APIError(code=-2010): Account has insufficient balance for requested action.**************
    # error selling, but account has insufficient balance, so calculating profit and freeing coin
    # ('coin sold, calculating profit and freeing coin', u'INSBTC', '2018-01-25 19:26:57')
    # ('profit was, absoulte profit, percent', -0.10772103699999996, -0.2303164364285631, '2018-01-25 19:26:57')
    # file updated
    # file updated
    # ('finished order - freeing coin', u'INSBTC')
    # #########################












# print(int(12/10))
# print(int(10/10))
# print(12%10)
# print(0%10)
# pprint(range(5, 0, -1))

############################################ N-minute Candles from 1-minute Data
# one_min_data = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_training_data/20180117/BATBTC_data_1m_p0.pklz')
# pprint(data)
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data
    # 1499040000000,      0 // Open time
    # "0.01634790",       1 // Open
    # "0.80000000",       2 // High
    # "0.01575800",       3 // Low
    # "0.01577100",       4 // Close
    # "148976.11427815",  5 // Volume
    # 1499644799999,      6 // Close time

# def get_n_minute_candles(n_minutes, one_min_data):

#     candles_to_return = int(len(one_min_data) / n_minutes)
#     offset = len(one_min_data) % n_minutes

#     candles = []
#     start_of_n_min_candle = True
#     open_time = 0
#     open_price = 0
#     high = 0
#     low = 9999999
#     close = 0
#     volume = 0.0
#     close_time = 0
#     for i in range(0 + offset, candles_to_return * n_minutes):
#         c = one_min_data[i]
#         if start_of_n_min_candle:
#             open_time = int(c[0])
#             open_price = float(c[1])
#             start_of_n_min_candle = False
#         if float(c[2]) > high:
#             high = float(c[2])
#         if float(c[3]) < low:
#             low = float(c[3])
#         volume += float(c[5])

#         if (i + 1) % n_minutes == 0:
#             close_time = int(c[6])
#             close = float(c[4])

#             candle = [open_time, ut.float_to_str(open_price), ut.float_to_str(high), ut.float_to_str(low), ut.float_to_str(close), ut.float_to_str(volume), close_time]
#             candles.append(candle)

#             start_of_n_min_candle = True
#             open_time = 0
#             open_price = 0
#             high = 0
#             low = 9999999
#             close = 0
#             volume = 0.0
#             close_time = 0
#     return candles

# two_min_data = get_n_minute_candles(2, one_min_data)
# print('len 2m', len(two_min_data))
# pprint(one_min_data[-2])
# pprint(one_min_data[-1])
# pprint(two_min_data[-1])




############################################ Test Data Quality
# data = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_training_data/20180118/ETHBTC_data_30m_p7.pklz')
# pprint(data)





############################################ Get Order Book Data + first in line price
# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)
# current_state = {
#     'symbol': 'ETHBTC',
#     'client': client,
#     'min_price': 0.00000100
# }
# # get min_price @ https://www.binance.com/api/v1/exchangeInfo  minPrice
# ut.get_first_in_line_price(current_state)





############################################ Develop Technical Indicators (MACD)
# symbol = 'BCCBTC'
# minutes = 1
# periods = 120
# end_time_period = int(time.time()) * 1000
# start_time_period = end_time_period - 60 * 1000 * minutes * periods
# start_readable = datetime.datetime.fromtimestamp(start_time_period/1000).strftime('%Y-%m-%d %H:%M:%S')
# end_readable = datetime.datetime.fromtimestamp(end_time_period/1000).strftime('%Y-%m-%d %H:%M:%S')
# print('symbol', symbol, 'minutes', minutes, 'periods', periods)
# print('start_readable', start_readable)
# print('end_readable', end_readable)
# url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol +'&interval='+str(minutes)+'m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period)
# print(url)
# r = requests.get(url)
# data = r.json()

# # candles, smart_candles = fn.add_bollinger_bands_to_candles(data)
# candles2, smart_candles2 = fn.make_smart_candles(data)

# for i in range(27,120):
#     # readable = datetime.datetime.fromtimestamp(float(candles[i][0])/1000).strftime('%Y-%m-%d %H:%M:%S')
#     # print(readable, candles2[i][14])
#     # pprint(candles2)
#     readable2 = datetime.datetime.fromtimestamp(float(candles2[i][0])/1000-7*60*60).strftime('%Y-%m-%d %H:%M:%S')
#     # print('macd_line, macd_signal_line, macd_histogram, macd_histogram_positive')
#     # print('11:37')
#     # print('-0.000016 (12), -0.000139 (26), -0.000154 (9)')
#     print(readable2, candles2[i][30])
#     print(readable2, candles2[i][31])
#     print(readable2, candles2[i][32])
#     print(readable2, candles2[i][33])
#     print(readable2, candles2[i][34])
#     print(readable2, candles2[i][35])
#     # print(readable2, candles2[i][24], candles2[i][25], candles2[i][26])
#     # print(readable2, candles2[i][27], candles2[i][28], candles2[i][29])
#     # print(readable2, candles2[i][16], candles2[i][17], candles2[i][18], candles2[i][19])
#     # print(readable2, candles2[i][20], candles2[i][21], candles2[i][22], candles2[i][23])
#     # print(readable2, candles2[i][14], candles2[i][16], candles2[i][17], candles2[i][18])
#     # print('-------')





################################################### parallel via functions

# urls = []
# minutes = 1
# end_time = int(time.time())*1000
# start_time = (end_time-60*1000*minutes*(10+1))
# length = '1m'
# for i in range(10):
#     url = 'https://api.binance.com/api/v1/klines?symbol='+ 'WINGSBTC' +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
#     urls.append(url)
# ##
# ut.start_url_threads(urls, ut.get_candles_then_buy_coin_test, call_back_args=['WINGSBTC', '1m', 4])





#################################################### get candles in parallel
# print('threads running', threading.active_count())
# # maximum = 124
# concurrent = 10

# def run_get_url_as_json_threads():
#     while True:
#         url = q.get()
#         the_json = get_url_as_json(url)
#         process_get_url_as_json_result(the_json)
#         q.task_done()

# def get_url_as_json(url):
#     try:
#         r = requests.get(url)
#         data = r.json()
#         return data
#     except Exception as e:
#         print(e)
#         return "error with getStatus()", url

# def process_get_url_as_json_result(the_json):
#     pprint(the_json[0][0])

# q = Queue(concurrent * 2)
# for i in range(concurrent):
#     t = Thread(target=run_get_url_as_json_threads)
#     t.daemon = True
#     t.start()
# try:
#     urls = []
#     minutes = 1
#     end_time = int(time.time())*1000
#     start_time = (end_time-60*1000*minutes*(10+1))
#     length = '1m'
#     for i in range(concurrent):
#         url = 'https://api.binance.com/api/v1/klines?symbol='+ 'WINGSBTC' +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
#         urls.append(url)
#     for url in urls:
#         q.put(url.strip())
#     q.join()
# except KeyboardInterrupt:
#     sys.exit(1)

# print(urls[0])






################## concurrent HTTP requests example
# print('threads running', threading.active_count())
# # maximum = 124
# concurrent = 124

# def doWork():
#     while True:
#         url = q.get()
#         status, url = getStatus(url)
#         doSomethingWithResult(status, url)
#         q.task_done()

# def getStatus(ourl):
#     try:
#         url = urlparse(ourl)
#         conn = httplib.HTTPConnection(url.netloc)
#         conn.request("HEAD", url.path)
#         res = conn.getresponse()
#         return res.status, ourl
#     except:
#         return "error", ourl

# def doSomethingWithResult(status, url):
#     print(status, url)

# q = Queue(concurrent * 2)
# for i in range(concurrent):
#     t = Thread(target=doWork)
#     t.daemon = True
#     t.start()
# try:
#     urls = []
#     for i in range(concurrent):
#         urls.append('http://google.com')
#     for url in urls:
#         q.put(url.strip())
#     q.join()
# except KeyboardInterrupt:
#     sys.exit(1)






# file_path = '/home/ec2-user/environment/botfarming/Development/binance_1m_trades/1m_trades.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# print(numpy.sum(data_points))
# pprint(data_points)
# f.close()


# file_path = '/home/ec2-user/environment/botfarming/Development/binance_30m_trades/30m_trades.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# print(numpy.sum(data_points))
# pprint(data_points)
# f.close()



# ut.append_or_create_data('/home/ec2-user/environment/botfarming/Development/binance_30m_trades/test.pklz', 99)
# time.sleep(1)
# ut.append_or_create_data('/home/ec2-user/environment/botfarming/Development/binance_30m_trades/test.pklz', 99)

# is_file = os.path.isfile('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graphNOT.pklz')
# print(is_file)
# is_file = os.path.isfile('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graph.pklz')
# print(is_file)


# zero = "1.00000000"
# one = "0.10000000"
# three = "0.00100000"
# five = "0.00001000"

# def get_decimal_places(lot_size):
#     lot_size = str(lot_size)
#     if '1.' in lot_size:
#         return 0
#     parts = lot_size.split('.')
#     parts2 = parts[1].split('1')
#     return len(parts2[0]) + 1

# print(get_decimal_places(zero))
# print(get_decimal_places(one))
# print(get_decimal_places(three))
# print(get_decimal_places(five))
# print(round(1.1111, 3))


# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)

# order = client.order_limit_buy(
#     symbol='BNBBTC',
#     quantity=100,
#     price='0.0001')
# pprint.pprint(order)

# amount_to_buy = round(.01/float('0.00003631'), 4)
# print(amount_to_buy)
# order = client.order_market_buy(
#     symbol='VIBBTC',
#     quantity=str(amount_to_buy))
# pprint.pprint(order)


# order = client.create_test_order(
#     symbol='BNBBTC',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_MARKET,
#     quantity=1)
# pprint.pprint(order)


# API-keys are passed into the Rest API via the X-MBX-APIKEY header
# Trade: Endpoint requires sending a valid API-Key and signature
# SIGNED endpoints require an additional parameter, signature, to be sent in the query string or request body
# HMAC SHA256 operation. Use your secretKey as the key and totalParams as the value for the HMAC operation
# SIGNED endpoint also requires a parameter, timestamp

# example signature
        # api_key = 'vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A'
        # api_secret = 'NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'
        # params = 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559'
        # signature = hmac.new(api_secret.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        # print(signature, 'should match:')
        # print('c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71')
        # request_url = 'https://api.binance.com/api/v1/order?'
        # url = request_url + params + '&signature=' + signature
        # symbol_buy = requests.post(url, headers={"X-MBX-APIKEY": api_key})
        # buy_data = symbol_buy.json()
        # print('buy_data')
        # pprint.pprint(buy_data)

# real signed request
# thanks: https://github.com/sammchardy/python-binance/issues/5
        # api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
        # api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
        # timestamp = int(time.time() * 1000)
        # request_url = 'https://api.binance.com/api/v1/order?'
        # params = 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.001&recvWindow=5000&timestamp='+str(timestamp)
        # signature = hmac.new(api_secret.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        # url = request_url + params + '&signature=' + signature
        # symbol_buy = requests.post(url, headers={"X-MBX-APIKEY": api_key})
        # buy_data = symbol_buy.json()
        # print('buy_data')
        # pprint.pprint(buy_data)


# http://www.irefone.com/no-text-sound-on-iphone-x-8-8-plus-7-7-plus.html
# epoch = int(time.time())
# readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%c')
# print readable_time
# fn.twilio_send_sms('UTC? '+readable_time)

# print 6755.65 >= 7000
# print int(round(time.time()) + 5)


# a = round(4.504783, 2)
# b = 4.5
# print a == b
# print a != b


# UTC time
# utc = datetime.utcnow()
# print utc
# print utc.hour, utc.minute, utc.second


# SCHEDULER
# def job():
#     print("I'm working...")
# def job_b():
#     print("...")

# schedule.every(10).seconds.do(job_b)
# schedule.every().day.at("20:46").do(job)

# while 1:
#     schedule.run_pending()
#     time.sleep(1)


# def doWork():
#     #do work here
#     epoch = int(time.time())
#     readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%c')
#     yyyymmddhhmmss = datetime.datetime.fromtimestamp(epoch).strftime('%Y%m%d%H%M%S')
#     do_save = epoch % 60 == 0
#     print epoch, readable_time, do_save, yyyymmddhhmmss

# # only start on even time segments
# save_every_n_seconds = 10
# while True:
#     epoch = int(time.time())
#     time.sleep(0.1)
#     if epoch % save_every_n_seconds == 0:
#         print 'start loop'
#         loop = task.LoopingCall(doWork)
#         loop.start(2.0)
#         reactor.run()
#         break
# # reactor.stop()


# epoch = int(time.time())
# readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%c')
# readable_time_2 = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
# yyyymmddhhmmss = datetime.datetime.fromtimestamp(epoch).strftime('%Y%m%d%H%M%S')
# print epoch
# print readable_time
# print readable_time_2
# print yyyymmddhhmmss

# print time.localtime()
# print time.localtime(1347517370)
# print time.strftime(, int(time.time()))
# print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))


# #store the object
# myObject = {'a':'blah','b':range(10)}
# f = gzip.open('./home/ec2-user/environment/botfarming/Development/Data/testPickleFile.pklz','wb')
# pickle.dump(myObject,f)
# f.close()

# #restore the object
# f = gzip.open('./home/ec2-user/environment/botfarming/Development/Data/testPickleFile.pklz','rb')
# myNewObject = pickle.load(f)
# f.close()

# print myObject
# print myNewObject

# end
print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print('elapsed:', int(time.time()) - start_time, 'seconds')