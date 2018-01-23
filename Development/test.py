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
import numpy
from binance.client import Client

from urlparse import urlparse
from threading import Thread
import threading
import httplib
from Queue import Queue
import requests
import functions_financial as fn

# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())

fn.print_ascii()
















# print(int(12/10))
# print(int(10/10))
# print(12%10)
# print(0%10)
# pprint(range(5, 0, -1))

############################################ N-minute Candles from 1-minute Data
# one_min_data = ut.pickle_read('./binance_training_data/20180117/BATBTC_data_1m_p0.pklz')
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
# data = ut.pickle_read('./binance_training_data/20180118/ETHBTC_data_30m_p7.pklz')
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






# file_path = './binance_1m_trades/1m_trades.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# print(numpy.sum(data_points))
# pprint(data_points)
# f.close()


# file_path = './binance_30m_trades/30m_trades.pklz'
# f = gzip.open(file_path,'rb')
# data_points = pickle.load(f)
# print(numpy.sum(data_points))
# pprint(data_points)
# f.close()



# ut.append_or_create_data('./binance_30m_trades/test.pklz', 99)
# time.sleep(1)
# ut.append_or_create_data('./binance_30m_trades/test.pklz', 99)

# is_file = os.path.isfile('./binance_profit_graph/profit_graphNOT.pklz')
# print(is_file)
# is_file = os.path.isfile('./binance_profit_graph/profit_graph.pklz')
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
# f = gzip.open('../Data/testPickleFile.pklz','wb')
# pickle.dump(myObject,f)
# f.close()

# #restore the object
# f = gzip.open('../Data/testPickleFile.pklz','rb')
# myNewObject = pickle.load(f)
# f.close()

# print myObject
# print myNewObject

# end
print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print('elapsed:', int(time.time()) - start_time, 'seconds')