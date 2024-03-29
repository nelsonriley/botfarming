#!/usr/bin/python2.7
import sys
print('python', sys.version)
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

from urlparse import urlparse
from threading import Thread
import threading
import httplib
from Queue import Queue
import requests
import functions_financial as fn
import math
import sqlite3

# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())

################################################# PLAY WITH EXECUTABLE CODE HERE


################################################# STUFF / INIT EMPTY ARRAY @ FILE PATH
# DONE
# buy_triggered_live_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/buys_triggered_live.pklz'
# ut.pickle_write(buy_triggered_live_path, [])
# buy_triggered_sim_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/buys_triggered_sim.pklz'
# ut.pickle_write(buy_triggered_sim_path, [])
# NEW




# min_volume_btc = 0
# symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
# symbols_filtered, symbol_list = ut2.get_trimmed_symbols(symbols, min_volume_btc)
# day_1 = '20180222_24'
# for s in symbol_list:
#     data_1 = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ day_1 + '/'+ s +'_data_1m.pklz')
#     data_count = 0
#     for d in data_1:
#         c = ut2.get_candle_as_dict(d)
#         data_count += 1
#     print(s, data_count)



################################################# SET CURRENT STATE TO FALSE FOR ALL
# current_state = {}
# current_state['symbol'] = 'OAXBTC' # 'HSRBTC'
# current_state['version'] = '24hr_1min_drop_v0'
# current_state['file_number'] = '2000'
# current_state['length'] = '1m'
# current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
# ut.pickle_write(current_state_path, False)


################################################# USE SQL-LITE TO SAVE CANDLES
# db_path = '/home/ec2-user/environment/botfarming/Development/binance_training_data_db/candle_db'
# db = sqlite3.connect(db_path)

# cursor = db.cursor()
# cursor.execute('''
#     CREATE TABLE users(id INTEGER PRIMARY KEY,
#                       name TEXT,
#                       phone TEXT,
#                       email TEXT unique,
#                       password TEXT)
# ''')
# db.commit()

# db.close()




################################################# REPORT ON TRADES (pre ENHANCED)
# file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop.pklz'
# trades = ut.pickle_read(file_path_all_trades)
# pprint(trades)
# btc_usd_price = 6200
# print('---------------------------- TRADE STATS 24hr 1min drop')
# trades = trades[10:] # 20:50 reset
# stats = {
#     'gain_percent': ut.float_to_str(sum(trade[3] for trade in trades), 6),
#     'gain_btc': ut.float_to_str(sum(trade[2] for trade in trades), 8),
#     'real_gain_btc': round(sum(trade[2] for trade in trades), 8) * 10,
#     'real_gain_usd': round(sum(trade[2] for trade in trades), 8) * 10 * btc_usd_price,
#     'total_trades': len(trades)
# }
# pprint(stats)


################################################# CONFIRM MAX DROPS SAVED for 24 HOURS
# symbol_24hr_drop_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/24hr_1min_drops_by_symbol/YOYOBTC.pklz'
# data = ut.pickle_read(symbol_24hr_drop_path)
# pprint(data)

################################################# TUNE DATES FOR SAVING MAX DROPS over 24 HOURS
# epoch_now = int(time.time())
# readable_date_folder = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y%m%d')
# readable_date_start = datetime.datetime.fromtimestamp(epoch_now-7*60*60-24*60*60).strftime('%Y-%m-%d')
# readable_date_end = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y-%m-%d')
# folder_name = readable_date_folder+'_24'
# start = readable_date_start+' 12:00'
# end = readable_date_end+' 12:00'
# print(folder_name)
# print(start)
# print(end)
# save_params = [
#     [ folder_name, start, end ]
# ]
# pprint(save_params)





################################################# GET CANDLES FOR SYMBOL
# end_time = int(time.time())*1000
# start_time = (end_time-60*1000*2)
# s = 'ETHBTC'
# interval = '1m'
# url = 'https://api.binance.com/api/v1/klines?symbol='+ s +'&interval='+interval+'&startTime='+str(start_time)+'&endTime='+str(end_time)
# print(url)
# # data = requests.get(url).json()




################################################# INITIALIZE AN EMPTY ARRAY PICKLE FILE
# file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop.pklz'
# ut.pickle_write(file_path_all_trades, [])



################################################# save 24hr data & make folder
# epoch_now = int(time.time())
# epoch_24hrs_ago = epoch_now - 24*60*60
# end = epoch_now
# start = epoch_24hrs_ago - datapoints_trailing*60
# readable_time_now = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y-%m-%d_%H:%M')
# readable_time_24hrs_ago = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y-%m-%d_%H:%M')
# folder = readable_time_24hrs_ago + '_to_' + readable_time_now
# print(folder)





################################################# STUFF
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



















# A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark
# from binance.client import Client
# from binance.websockets import BinanceSocketManager
# api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
# api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
# client = Client(api_key, api_secret)
# bm = BinanceSocketManager(client)

# socket_list = ['neobtc@kline_1m', 'neobtc@depth20', 'wingsbtc@kline_1m', 'wingsbtc@depth20']
# def process_socket_pushes(msg):
#     if 'e' in msg and msg['e'] == 'error':
#         # close and restart the socket, if socket can't reconnect itself
#         print('restarting process_socket_pushes(msg)')
#         bm.close()
#         conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes)
#         bm.start()
#     else:
#         # if 'kline_1m' in msg['stream']:
#         #     print('--------------------------------------', msg['stream'], ut.get_time())
#         #     pprint(msg['data'])
#         #     print('--------------------------------------')
#         if 'depth' in msg['stream']:
#             # print('--------------------------------------', msg['stream'], ut.get_time())
#             # # pprint(msg['data'])
#             # # available: asks + bids
#             # # 'asks': [[u'0.01264000', u'18.92000000', []],
#             # #          [u'0.01265300', u'0.20000000', []],
#             # print('--------------------------------------')
#             symbol = msg['stream'].split('@')[0].upper()
#             ut.pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_book/'+symbol+'.pklz', msg['data'])

# conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes)
# bm.start()
# time.sleep(15)
# bm.close()














































#########################check if symbols are in our list
# symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
# symbol_list = []
# for s in symbols:
#     symbol = symbols[s]
#     symbol_list.append(s)
#     if float(symbol['24hourVolume']) > 450:
#         if s == 'ASTBTC':
#             print('----', s)
# print('symbol_count', len(symbol_list))
# i = 0
# symbols2 = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
# for s in symbols2:
#     if symbol_list[i] != s:
#         print('wtf!', s)
#     i += 1
#
# sys.exit()
# ####################################################

# end
print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print('elapsed:', int(time.time()) - start_time, 'seconds')