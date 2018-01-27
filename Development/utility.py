import requests
import time
from pprint import pprint
import numpy
import sys
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
import socket
import random
from six.moves import urllib
global number_of_api_requests
from binance.websockets import BinanceSocketManager



# part_of_bitcoin_to_use

def get_readable_time(time_to_get):
    return datetime.datetime.fromtimestamp(int(time_to_get)-7*60*60).strftime('%Y-%m-%d %H:%M:%S')

def get_time():
    return datetime.datetime.fromtimestamp(int(time.time())-7*60*60).strftime('%Y-%m-%d %H:%M:%S')


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def pickle_read(file_path):
    try:
        f = gzip.open(file_path,'rb')
        data = pickle.load(f)
        f.close()
        return data
    except Exception as e:
        #print(e)
        return False

def pickle_write(file_path, data, error_message='pickle could not write'):
    try:
        f = gzip.open(file_path,'wb')
        pickle.dump(data,f)
        f.close()
    except Exception as e:
        return
        #print(e)
        #print(error_message)



def get_min_decimals(min_qty):
    min_price_for_decimal = str(min_qty)
    if '1.' in min_price_for_decimal:
        price_decimals = 0
    else:
        parts = min_price_for_decimal.split('.')
        parts2 = parts[1].split('1')
        price_decimals = len(parts2[0]) + 1
    return price_decimals

def get_min_decimals_new(min_notional):
    min_price_for_decimal = str(min_notional)
    if '1.' in min_price_for_decimal:
        price_decimals = 0
    else:
        parts = min_price_for_decimal.split('.')
        ints = re.findall(r"[1-9]", parts[1])
        parts2 = parts[1].split(ints[0])
        price_decimals = len(parts2[0]) + 1
    return price_decimals

def float_to_str(f):
    import decimal
    ctx = decimal.Context()
    ctx.prec = 20
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

def candle_to_dict(candle):
    return {
        'time': int(candle[0]),
        'open': float(candle[1]),
        'high': float(candle[2]),
        'low': float(candle[3]),
        'close': float(candle[4]),
        'volume': float(candle[5])
    }


def sleep_but_check_order(current_state, time_to_sleep):

    if time_to_sleep <= 0:
        return

    for i in range(0, time_to_sleep):
        time.sleep(60)
        try:
            sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
            if sale_order_info['status'] == 'FILLED':
                return
        except Exception as e:
            print('sleep_but_check_order() could not get sale_order_info, retrying in 60s... error:')
            print(e)
            time.sleep(60)
            sleep_but_check_order(current_state, time_to_sleep - i)
            return

def cancel_buy_order(current_state):

    try:
        buy_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print('could not cancel buy order')

    buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
    current_state['state'] = 'buying'
    current_state['orderId'] = False
    current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
    if float(buy_order_info['price']) != 0:
        current_state['original_price'] = float(buy_order_info['price'])
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')

    return current_state

def cancel_sale_order(current_state):

    order_id_of_current_state = current_state['orderId']

    try:
        sale_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print('could not cancel sale order')


    current_state['state'] = 'selling'
    current_state['orderId'] = False
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')

    sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=order_id_of_current_state)

    current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
    current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')

    return current_state

def create_buy_order(current_state, price_to_buy):

    maximum_order_to_buy = float_to_str(round(current_state['largest_buy_segment'],current_state['quantity_decimals']))
    maximum_possible_buy = float_to_str(round(current_state['original_amount_to_buy'] - current_state['executedQty'], current_state['quantity_decimals']))
    quantity_to_buy = min(float(maximum_order_to_buy), float(maximum_possible_buy))

    buy_order = current_state['client'].order_limit_buy(symbol=current_state['symbol'],quantity=quantity_to_buy,price=price_to_buy)

    current_state['state'] = 'buying'
    current_state['orderId'] = buy_order['orderId']
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state 2nd sell******')

    return current_state

def create_sale_order(current_state, price_to_sell):
    #print('in create sale order', price_to_sell)

    if not 'largest_bitcoin_order' in current_state:
        print(current_state['symbol'], 'largest_bitcoin_order NOT defined', get_time())
        # EXCEPTION IN (/home/nelsonriley/Development/utility.py, LINE 294 "sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_3'], current_state['minutes_until_sale_3'])"): 'largest_bitcoin_order'
        current_state['largest_bitcoin_order'] = .1

    max_quantity = float_to_str(round(current_state['largest_bitcoin_order']/float(price_to_sell),current_state['quantity_decimals']))
    order_size = min(float(max_quantity), float(current_state['executedQty']))
    sale_order = current_state['client'].order_limit_sell(symbol=current_state['symbol'],quantity=order_size,price=price_to_sell)

    current_state['state'] = 'selling'
    current_state['orderId'] = sale_order['orderId']
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state 2nd sell******')

    return current_state

def calculate_profit_and_free_coin(current_state):
    # also save trade to trade history

    print('coin sold, calculating profit and freeing coin', current_state['symbol'],get_time())
    percent_profit_from_trade = (current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price'])/(current_state['original_quantity']*current_state['original_price'])
    profit_from_trade = current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price']
    invested_btc = current_state['original_quantity']*current_state['original_price']
    print('profit was, absoulte profit, percent', profit_from_trade, percent_profit_from_trade, get_time())

    # save trade stats
    # OLD WAY: writing each file path unique to look back
    data_to_save = [profit_from_trade, percent_profit_from_trade, current_state['original_quantity']*current_state['original_price'], current_state['symbol'],current_state['original_buy_time_readable'], get_time()]
    append_or_create_data('./binance_' + str(current_state['look_back']) + '_trades/'+ str(current_state['look_back']) + '_trade_data', data_to_save)
    # NEW WAY: keep one array, use dict not array, record volume data (24hr + past 10 trades)
    volume_ten_candles_btc = .01
    if 'trailing_volumes' in current_state and len(current_state['trailing_volumes']) > 10:
        trailing_volumes = current_state['trailing_volumes']
        volume_ten_candles_btc = float(numpy.sum(trailing_volumes[-10:]))
        # print('-------Debug')
        # print('trailing_volumes', len(current_state['trailing_volumes']), current_state['trailing_volumes'])
        # print('sum', float(numpy.sum(trailing_volumes[-10:])))
    volume_twentyfour_hr_btc = .01
    try:
        # ie: https://www.binance.com/api/v1/ticker/24hr?symbol=ETHBTC
        url = "https://api.binance.com/api/v1/ticker/24hr?symbol=" + current_state['symbol']
        data = requests.get(url).json()
        volume_twentyfour_hr_btc = float(data['quoteVolume'])
    except Exception as e:
        print('could not get volume_twentyfour_hr_btc for', current_state['symbol'])
        print(e)
        sys.exit()
    volume_twentyfour_hr_ratio = invested_btc / volume_twentyfour_hr_btc
    volume_ten_candles_ratio = invested_btc / volume_ten_candles_btc
    recorded_trade = {
        'symbol': current_state['symbol'],
        'invested_btc': invested_btc,
        'profit_btc': profit_from_trade,
        'profit_percent': percent_profit_from_trade,
        'time_buy_human': current_state['original_buy_time_readable'],
        'time_buy_epoch': current_state['original_buy_time'],
        'time_end_human': get_time(),
        'time_end_epoch': int(time.time()),
        'look_back': current_state['look_back'],
        'largest_bitcoin_order': current_state['largest_bitcoin_order'],
        'part_of_bitcoin_to_use': current_state['part_of_bitcoin_to_use'],
        'volume_ten_candles_btc': volume_ten_candles_btc,
        'volume_ten_candles_ratio': volume_ten_candles_ratio,
        'volume_twentyfour_hr_btc': volume_twentyfour_hr_btc,
        'volume_twentyfour_hr_ratio': volume_twentyfour_hr_ratio,
        'current_state': current_state
    }
    file_path_all_trades = './binance_all_trades_history/binance_all_trades_history.pklz'
    append_or_create_data(file_path_all_trades, recorded_trade)

    # update program state
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False)
    pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + current_state['symbol'] + '.pklz', False)


def get_first_in_line_price_buying(current_state):
    order_book = current_state['client'].get_order_book(symbol=current_state['symbol'], limit=10)
    # pprint(order_book)
    # bids & asks.... 0=price, 1=qty
    first_bid = float(order_book['bids'][0][0])
    second_bid = float(order_book['bids'][1][0])
    second_price_to_check = first_bid - 3*current_state['min_price']
    second_price_to_buy = float_to_str(round(second_bid + current_state['min_price'], current_state['price_decimals']))
    price_to_buy = float_to_str(round(first_bid + current_state['min_price'], current_state['price_decimals']))

    return price_to_buy,first_bid, second_price_to_buy, second_bid, second_price_to_check


def get_first_in_line_price(current_state):
    order_book = current_state['client'].get_order_book(symbol=current_state['symbol'], limit=10)
    # pprint(order_book)
    # bids & asks.... 0=price, 1=qty
    first_ask = float(order_book['asks'][0][0])
    second_ask = float(order_book['asks'][1][0])
    second_price_to_check = first_ask + 3*current_state['min_price']
    second_price_to_buy = float_to_str(round(second_ask - current_state['min_price'], current_state['price_decimals']))
    price_to_buy = float_to_str(round(first_ask - current_state['min_price'], current_state['price_decimals']))
    # print(first_ask)
    # print(price_to_buy)
    return price_to_buy,first_ask, second_price_to_buy, second_ask, second_price_to_check


def sell_with_order_book(current_state, price_to_sell, minutes_until_sale):

    started_selling = False
    minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
    minutes_to_run = minutes_until_sale - minutes_since_start

    time_to_give_up = int(time.time()) + minutes_to_run * 60
    price_to_sell_min = current_state['sell_price_drop_factor'] * price_to_sell
    print('price_to_sell_min', price_to_sell_min)
    while True:
        if current_state['orderId'] != False:
            sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
            if sale_order_info['status'] == 'FILLED':
                current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
                current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
                current_state['state'] = 'selling'
                current_state['orderId'] = False
                pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state 2nd sell******')
                if current_state['executedQty'] < current_state['min_quantity']:
                    return True, current_state

        if int(time.time()) >= time_to_give_up:
            if current_state['orderId'] != False:
                current_state = cancel_sale_order(current_state)
                if current_state['executedQty'] < current_state['min_quantity']:
                    return True, current_state
                else:
                    return False, current_state
            return False, current_state

        first_in_line_price, first_ask, second_in_line_price, second_ask, second_price_to_check = get_first_in_line_price(current_state)

        if float(first_in_line_price) >= price_to_sell_min or started_selling == True:
            started_selling = True
            if current_state['orderId'] != False:
                sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                if first_ask != float(sale_order_info['price']):
                    current_state = cancel_sale_order(current_state)
                    if current_state['executedQty'] < current_state['min_quantity']:
                        return True, current_state
                    current_state = create_sale_order(current_state, first_in_line_price)
                else:
                    if second_price_to_check < second_ask:
                        current_state = cancel_sale_order(current_state)
                        if current_state['executedQty'] < current_state['min_quantity']:
                            return True, current_state
                        current_state = create_sale_order(current_state, second_in_line_price)

            else:
                current_state = create_sale_order(current_state, first_in_line_price)

        time.sleep(.1)



def sell_coin_with_order_book(current_state):

    try:

        if current_state['executedQty'] >= current_state['min_quantity']:

            print('selling..', current_state['symbol'], get_time())

            print('selling at price level 1', current_state['symbol'])
            sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell'], current_state['minutes_until_sale'])

            if not sold_coin:
                print('selling at price level 2', current_state['symbol'])
                sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_2'], current_state['minutes_until_sale_2'])

            if not sold_coin:
                print('selling at price level 3', current_state['symbol'])
                sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_3'], current_state['minutes_until_sale_3'])

            if not sold_coin:
                print('selling at level 4', current_state['symbol'])
                sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_3']/2, 9999)

        calculate_profit_and_free_coin(current_state)
        return True
    except Exception as e:
        print(e)
        print_exception()
        error_as_string = str(e)
        if error_as_string.find('Account has insufficient balance for requested action.') >= 0:
            print('error selling, but account has insufficient balance, so calculating profit and freeing coin')
            calculate_profit_and_free_coin(current_state)
            return True
        if error_as_string.find('Filter failure: MIN_NOTIONAL') >= 0:
            print('error selling, MIN_NOTIONAL error, so probably coin has sold mostly, so calculating profit and freeing coin')
            calculate_profit_and_free_coin(current_state)
            return True
        print('error selling')
        return False

def buy_coin_from_state(current_state):

    print('buy coin from state', current_state['symbol'])

    if (current_state['state'] == 'buying'):

        if current_state['orderId'] != False:
            current_state = cancel_buy_order(current_state)


        if float(current_state['executedQty']) < current_state['min_quantity']:
            print('buy order canceled, was never filled, exiting')
            pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False, '******could not write state buy from stae******')
            pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + current_state['symbol'] + '.pklz', False)
            return
        else:
            current_state['state'] = 'selling'
            current_state['original_quantity'] = current_state['executedQty']
            pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')


    ##are selling...
    print('buy_coin_from_state() selling..', current_state['symbol'])

    if current_state['orderId'] > 0:

        print('sale order exisits canceling it..')
        current_state = cancel_sale_order(current_state)
        if current_state['executedQty'] < current_state['min_quantity']:
            calculate_profit_and_free_coin(current_state)
            return

    print('buy_coin_from_state() no open orders, selling coin..', current_state['symbol'])
    sell_coin_with_order_book(current_state)


def buy_coin(symbol, length, file_number):

    data = []

    current_state = load_current_state(symbol['symbol'], file_number, length)

    if isinstance(current_state,dict):
        print('loading state to sell coin..', current_state['symbol'])
        buy_coin_from_state(current_state)
        return

    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    bm = BinanceSocketManager(client)
    conn_key = bm.start_depth_socket(symbol['symbol'], check_coin_price)
    bm.start()

    global candle_data
    while True:
        time.localtime().tm_sec < 4:
            end_time = int(time.time())*1000
            start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
            data = opener.open(url).read()
            data = json.loads(data)
            time.sleep(4)


def check_coin_price(msg):



    try:

        minutes = 1

        largest_bitcoin_order = .1
        part_of_bitcoin_to_use = 1.0
        price_to_start_buy = 1.003

        sell_price_drop_factor = .997
        buy_price_increase_factor = 1.002

        price_to_buy_factor_array = [0,.978, .973, .97, .971, .966, .96, .955, .95, .956, .95]
        price_to_sell_factor_array = [0,.994, .993, .996, .991, .989, .989, .983, .986, .986, .986]
        price_to_sell_factor_2_array = [0,.984, .984, .984, .983, .984, .983, .982, .982, .982, .981]
        price_to_sell_factor_3_array = [0,.965, .965, .965, .965, .965, .964, .964, .963, .963, .963]
        lower_band_buy_factor_array = [0,1.04, 1.12, 1.09, 1.07, 1.09, 1.12, 1.15, 1.16, 1.19, 1.19]

        datapoints_trailing = 230

        minutes_until_sale = 4
        minutes_until_sale_2 = 12
        minutes_until_sale_3 = 45



        if len(data) == 0:
            end_time = int(time.time())*1000
            start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
            data = opener.open(url).read()
            data = json.loads(data)
            #pprint(data)
            # TODO data = get_smart_candles(data)
        if isinstance(data, basestring):
            print('API request failed, exiting', symbol['symbol'])
            return


        trailing_volumes = []
        trailing_movement = []
        trailing_lows = []
        trailing_highs = []
        trailing_candles = []

        if first_bid > float(data[index-look_back][4])*price_to_buy_factor_array[look_back]*price_to_start_buy:
            return

        for index, candle in enumerate(data):

            # compare (only last candle)
            if len(trailing_movement) >= datapoints_trailing:

                # init binance client


                should_buy = False

                while True:


                    time.sleep(.5)
                    if (symbol['symbol'] == 'APPCBTC'):
                        print("start api call ", symbol['symbol'], get_time())
                    order_book = client.get_order_book(symbol=symbol['symbol'], limit=10)
                    first_bid = float(order_book['bids'][0][0])

                    look_back_schedule = [6,1,8,10,9,4,5,2,7,3]
                    # look_back_schedule = [1,2,3,4,5,6]
                    for look_back in look_back_schedule:

                        if first_bid < float(data[index-look_back][4])*price_to_buy_factor_array[look_back]*price_to_start_buy:

                            if lower_band_buy_factor_array[look_back] < 100:
                                candles_for_look_back = fn.get_n_minute_candles(look_back, data[index-22*look_back-1:index])
                                candles_for_look_back, smart_trailing_candles = fn.add_bollinger_bands_to_candles(candles_for_look_back)
                                lower_band_for_index = candles_for_look_back[-1][14]
                                #print('lower_band_for_index', lower_band_for_index)
                                band_ok_value = lower_band_for_index*lower_band_buy_factor_array[look_back]
                                band_ok = float(candle[4]) < band_ok_value
                            else:
                                band_ok = True

                            if band_ok:
                                should_buy = True
                                break

                    if should_buy == True or time.localtime().tm_sec < 4:
                        break


                if should_buy:
                    lower_band_buy_factor = lower_band_buy_factor_array[look_back]
                    price_to_buy_factor = price_to_buy_factor_array[look_back]
                    price_to_sell_factor = price_to_sell_factor_array[look_back]
                    price_to_sell_factor_2 = price_to_sell_factor_2_array[look_back]
                    price_to_sell_factor_3 = price_to_sell_factor_3_array[look_back]

                    try:
                        is_invested = pickle_read('./binance_is_invested_' + length +'/is_invested_' + length + '_' + symbol['symbol'] + '.pklz')
                    except Exception as e:
                        is_invested = False

                    # record attempts to buy, not just complete trades
                    if lower_band_buy_factor < 100:
                        price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(data[index-look_back][4])*price_to_buy_factor)
                    else:
                        price_to_buy = float(data[index-look_back][4])*price_to_buy_factor
                    recorded_trade_attempt = {
                        'symbol': symbol['symbol'],
                        'price_to_buy': price_to_buy,
                        'time_human': get_time(),
                        'time_epoch': int(time.time()),
                        'look_back': look_back
                    }
                    file_path_all_trades_attempts = './binance_all_trades_history/binance_all_trades_history_attempts.pklz'
                    append_or_create_data(file_path_all_trades_attempts, recorded_trade_attempt)

                    if is_invested == False:

                        print('buy', symbol['symbol'], 'look back', look_back)

                        pickle_write('./binance_is_invested_' + length +'/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', True)

                        if lower_band_buy_factor < 100:
                            price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(data[index-look_back][4])*price_to_buy_factor)
                        else:
                            price_to_buy = float(data[index-look_back][4])*price_to_buy_factor
                        price_to_sell = float(data[index-look_back][4])*price_to_sell_factor
                        price_to_sell_2 = float(data[index-look_back][4])*price_to_sell_factor_2
                        price_to_sell_3 = float(data[index-look_back][4])*price_to_sell_factor_3

                        amount_to_buy = part_of_bitcoin_to_use/price_to_buy
                        largest_buy_segment = largest_bitcoin_order/price_to_buy

                        price_decimals = get_min_decimals(symbol['filters'][0]['minPrice'])

                        quantity_decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                        # quantity_decimals = get_min_decimals_new(symbol['filters'][2]['minNotional'])

                        current_state = {}
                        current_state['state'] = 'buying'
                        current_state['look_back'] = look_back
                        current_state['sell_price_drop_factor'] = sell_price_drop_factor
                        current_state['original_amount_to_buy'] = amount_to_buy
                        current_state['largest_bitcoin_order'] = largest_bitcoin_order
                        current_state['part_of_bitcoin_to_use'] = part_of_bitcoin_to_use
                        current_state['largest_buy_segment'] = largest_buy_segment
                        current_state['original_buy_time'] = int(time.time())
                        current_state['symbol'] = symbol['symbol']
                        current_state['orderId'] = False
                        current_state['original_buy_time_readable'] = get_time()
                        current_state['executedQty'] = 0
                        current_state['total_revenue'] = 0
                        current_state['minutes_until_sale'] = minutes_until_sale
                        current_state['minutes_until_sale_2'] = minutes_until_sale_2
                        current_state['minutes_until_sale_3'] = minutes_until_sale_3
                        current_state['price_to_buy'] = price_to_buy
                        current_state['price_to_sell'] = price_to_sell
                        current_state['price_to_sell_2'] = price_to_sell_2
                        current_state['price_to_sell_3'] = price_to_sell_3
                        current_state['length'] = length
                        current_state['file_number'] = str(file_number)
                        current_state['client'] = client
                        current_state['error_cancel_order'] = False
                        current_state['price_decimals'] = price_decimals
                        current_state['quantity_decimals'] = quantity_decimals
                        current_state['min_price'] = float(symbol['filters'][0]['minPrice'])
                        current_state['min_quantity'] = min(float(symbol['filters'][1]['minQty']), float(symbol['filters'][2]['minNotional']))
                        current_state['trailing_candles'] = trailing_candles
                        current_state['trailing_volumes'] = trailing_volumes

                        pickle_write('./program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz', current_state, '******could not write state******')



                        time_to_give_up = int(time.time()) + 60
                        price_to_buy_max = price_to_buy*buy_price_increase_factor
                        amount_to_stop_buying = part_of_bitcoin_to_use/price_to_buy_max
                        print('max price', price_to_buy_max)
                        while True:
                            if current_state['orderId'] != False:
                                buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                                if buy_order_info['status'] == 'FILLED':
                                    current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
                                    current_state['original_price'] = float(buy_order_info['price'])
                                    current_state['state'] = 'buying'
                                    current_state['orderId'] = False
                                    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state 2nd sell******')
                                    if current_state['executedQty'] >= amount_to_stop_buying:
                                        break

                            if int(time.time()) >= time_to_give_up:
                                if current_state['orderId'] != False:
                                    current_state = cancel_buy_order(current_state)
                                break

                            first_in_line_price, first_bid, second_in_line_price, second_bid, second_price_to_check = get_first_in_line_price_buying(current_state)
                            if float(first_in_line_price) > price_to_buy_max:
                                if current_state['orderId'] != False:
                                    current_state = cancel_buy_order(current_state)
                                    if current_state['executedQty'] >= amount_to_stop_buying:
                                        break
                            else:
                                if current_state['orderId'] != False:
                                    buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                                    if first_bid != float(buy_order_info['price']):
                                        current_state = cancel_buy_order(current_state)
                                        if current_state['executedQty'] >= amount_to_stop_buying:
                                            break
                                        current_state = create_buy_order(current_state, first_in_line_price)
                                    else:
                                        if second_price_to_check > second_bid:
                                            current_state = cancel_buy_order(current_state)
                                            if current_state['executedQty'] >= amount_to_stop_buying:
                                                break
                                            current_state = create_buy_order(current_state, second_in_line_price)

                                else:
                                    current_state = create_buy_order(current_state, first_in_line_price)

                            time.sleep(.1)

                        # call_back_args = [symbol['symbol'],look_back]
                        # t = Thread(target=free_coin_after_candle, args=call_back_args)
                        # t.start()


                        if current_state['executedQty'] < current_state['min_quantity']:
                            print('no one bought cancel order - freeing coin', current_state['symbol'])
                            pickle_write('./program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz', False, '******could not write state inside buy coin - no one bought coin******')
                            pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + symbol['symbol'] + '.pklz', False)
                            return True


                        current_state['original_quantity'] = current_state['executedQty']
                        current_state['state'] = 'selling'
                        pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not update state to selling******')

                        coin_sold = sell_coin_with_order_book(current_state)

                        if coin_sold:
                            print('finished order - freeing coin', current_state['symbol'])

                            pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + symbol['symbol'] + '.pklz', False)

                            print('#########################')

                        return True

                    else:
                        print('coin invested skipping..', symbol['symbol'])


            # update
            if len(trailing_movement) <= datapoints_trailing:
                trailing_volumes.append(float(candle[7])) # 5 is symbol volume, 7 is quote asset volume (BTC)
                trailing_movement.append(abs(float(candle[4])-float(candle[1])))
                trailing_highs.append(float(candle[2]))
                trailing_lows.append(float(candle[3]))
                trailing_candles.append(candle)
            if len(trailing_movement) > datapoints_trailing:
                break

        return True

    except Exception as e:
        print('some error - freeing coin:', symbol['symbol'])
        print('number_of_api_requests', number_of_api_requests)
        print(e)
        print_exception()
        pickle_write('./binance_is_invested_' + length + '/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', False)
        time.sleep(60*4)
        return False


def free_coin_after_candle(symbol, look_back):

    while True:
        if time.localtime().tm_sec < 2:
            print('onto next candle freeing coin with look_back...', symbol, look_back)
            pickle_write('./binance_is_invested_' + str(look_back) +'m/is_invested_' + str(look_back) + 'm_' + symbol + '.pklz', False)
            return


def load_current_state(symbol, file_number, length):

    try:
        f = gzip.open('./program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol + '.pklz','rb')
        current_state = pickle.load(f)
        f.close()
    except Exception as e:
        current_state = False

    return current_state

def run_bot(file_number, total_files, overlap, length):
    print('running bot', file_number, 'of', total_files, length)
    try:
        symbols = pickle_read('./binance_btc_symbols.pklz')

        total_btc_coins = 0
        symbols_trimmed = {}

        for s in symbols:
            symbol = symbols[s]
            if float(symbol['24hourVolume']) > 450:
                total_btc_coins += 1
                symbols_trimmed[s] = symbol

    except Exception as e:
            print(e)
            sys.exit()

    symbol_back_up = symbols_trimmed
    current_state = []

    while True:

            symbols_trimmed = symbol_back_up
        #try:
            loops = 0

            file_start_index = file_number
            file_end_index = (file_number+overlap)%total_files
            if file_end_index == 0:
                file_end_index = total_files

            file_start_number = math.floor(total_btc_coins/total_files)*file_start_index
            file_end_number = file_end_index*math.floor(total_btc_coins/total_files)

            for s in symbols_trimmed:
                symbol = symbols_trimmed[s]
                if file_end_index < overlap:
                    if loops >= file_start_number or loops < file_end_number:
                        current_state = load_current_state(symbol['symbol'], file_number, length)
                else:
                    if loops >= file_start_number and loops < file_end_number:
                        current_state = load_current_state(symbol['symbol'], file_number, length)
                loops += 1

                if isinstance(current_state,dict):
                    print('loading state to sell coin..', current_state['symbol'])
                    buy_coin_from_state(current_state)

                current_state = False

            symbols_trimmed = symbol_back_up

            loops = 0

            for s in symbols_trimmed:
                symbol = symbols_trimmed[s]

                if file_end_index < overlap:
                    if loops >= file_start_number or loops < file_end_number:
                        buy_coin(symbol, length, file_number)
                else:
                    if loops >= file_start_number and loops < file_end_number:
                        buy_coin(symbol, length, file_number)

                loops += 1
                #time.sleep(.1)
                # if length == '1m':
                #     time.sleep(.25)
                # elif length == '5m':
                #     time.sleep(.5)
                # else:
                #     time.sleep(1)

        # except Exception as e:
        #     print('error in wrapper')
        #     print(e)
        #     print_exception()
        #     continue

def run_bot_parallel(file_number, total_files):

    print('running bot', file_number, 'of', total_files, 'ip address:')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
    s.close()
    try:
        symbols = pickle_read('./binance_btc_symbols.pklz')

        total_btc_coins = 0
        symbols_trimmed = {}

        for s in symbols:
            symbol = symbols[s]
            if float(symbol['24hourVolume']) > 450:
                #print(symbol['symbol'])
                total_btc_coins += 1
                symbols_trimmed[s] = symbol

        #print(total_btc_coins)
    except Exception as e:
            print(e)
            sys.exit()


    file_start = math.ceil(file_number*total_btc_coins/total_files)
    file_end = math.ceil((file_number+1)*total_btc_coins/total_files)

    loops = 0
    for s in symbols_trimmed:
        symbol = symbols_trimmed[s]

        if loops >= file_start and loops < file_end:
            t = Thread(target=buy_coin_thread, args=[symbol, file_number])
            t.start()

        loops += 1



# "worker"
def buy_coin_thread(symbol, file_number):

    global number_of_api_requests
    number_of_api_requests = 0

    times_called = 0
    while True:
        buy_coin(symbol, '1m', file_number)




# file_path = './binance_30m_trades/30m_trades.pklz'
def append_or_create_data(file_path, data):
    is_file = os.path.isfile(file_path)
    if is_file:
        data_points = pickle_read(file_path)
        data_points.append(data)
        pickle_write(file_path, data_points)
        print('file updated')
    else:
        #save the file first time
        pickle_write(file_path, [data])
        print('file created')

def buy_coin_test(symbol):
    print('hi')