import requests
import time
from pprint import pprint
import numpy
import sys
import os
import pickle
import gzip
import datetime
import json
import math
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
from binance.client import Client
from binance.websockets import BinanceSocketManager



# part_of_bitcoin_to_use

def get_readable_time(time_to_get):
    stamp = int(time_to_get)-7*60*60
    # handle millisecond time stamps (as well as seconds)
    if len(str(time_to_get)) > 10:
        stamp = int(int(time_to_get)/1000.0-7*60*60)
    return datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M:%S')

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
        print(e)
        print(error_message)
        return

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

###########################################################################################


def new_buy_and_sell_thread(buy_params):
    # TODO !!!
    return False


def buy_coin_socket(msg):
    if 'e' in msg and msg['e'] == 'error':
        # close and restart the socket, if socket can't reconnect itself
        print('restarting process_socket_pushes(msg)')
        global socket_list
        global bm
        bm.close()
        conn_key = bm.start_multiplex_socket(socket_list, buy_coin_socket)
        bm.start()
    else:
        if 'depth' in msg['stream']:
            symbol = msg['stream'].split('@')[0].upper()
            print(symbol,  msg['data']['bids'][0][0], get_time())
            time.sleep(5)


def process_socket_pushes_order_book(msg):
    if 'e' in msg and msg['e'] == 'error':
        # close and restart the socket, if socket can't reconnect itself
        print('restarting process_socket_pushes(msg)')
        global socket_list
        global bm
        bm.close()
        conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes_order_book)
        bm.start()
    else:
        # if 'kline_1m' in msg['stream']:
        #     print('--------------------------------------', msg['stream'], get_time())
        #     pprint(msg['data'])
        #     print('--------------------------------------')
        if 'depth' in msg['stream']:
            # print('--------------------------------------', msg['stream'], get_time())
            # # pprint(msg['data'])
            # # available: asks + bids
            # # 'asks': [[u'0.01264000', u'18.92000000', []],
            # #          [u'0.01265300', u'0.20000000', []],
            # print('--------------------------------------', process_socket_pushes_order_book(msg))
            symbol = msg['stream'].split('@')[0].upper()
            pickle_write('./recent_order_books/'+symbol+'.pklz', msg['data'])

            if symbol == 'ETHBTC' and (time.localtime().tm_sec == 1 or time.localtime().tm_sec == 2):
                print('process_socket_pushes_order_book() ETHBTC', msg['data']['bids'][0][0], get_time())

            # globals()[symbol + '_order_book'] = msg['data']



def update_symbol_list():
    # save symbol list daily since API sometimes fail when getting live
    symbol_data = requests.get("https://api.binance.com/api/v1/exchangeInfo").json()
    ticker_data = requests.get("https://api.binance.com/api/v1/ticker/24hr").json()

    symbols_for_save = {}
    for symbol in symbol_data['symbols']:
        if symbol['quoteAsset'] == 'BTC':
            symbols_for_save[symbol['symbol']] = symbol
    for symbol in ticker_data:
        if 'BTC' in symbol['symbol'] and not 'BTC' in symbol['symbol'][:3]:
            symbols_for_save[symbol['symbol']]['24hourVolume'] = symbol['quoteVolume']
            symbols_for_save[symbol['symbol']]['24priceChangePercent'] = symbol['priceChangePercent']

    # print('---------------ETHBTC')
    # pprint(symbols_for_save['ETHBTC'])
    # print('---------------ETHBTC')

    print('btc symbols found:', len(symbols_for_save))
    pickle_write('./binance_btc_symbols.pklz', symbols_for_save)

    symbols_saved = pickle_read('./binance_btc_symbols.pklz')
    print('btc symbols saved:', len(symbols_saved))


def cancel_buy_order(current_state):

    try:
        buy_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print('could not cancel buy order')

    try:
        buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
        current_state['state'] = 'buying'
        current_state['orderId'] = False
        current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
        if float(buy_order_info['price']) != 0:
            current_state['original_price'] = float(buy_order_info['price'])
        pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')
    except Exception as e:
        print('could not get buy_order_info')
        current_state['state'] = 'buying'
        current_state['orderId'] = False
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
    print('for ', current_state['symbol'] ,'profit was, absoulte profit, percent profit, amount invested', profit_from_trade, percent_profit_from_trade,invested_btc, get_time())

    # # save trade stats
    # # OLD WAY: writing each file path unique to look back
    #     # data_to_save = [profit_from_trade, percent_profit_from_trade, current_state['original_quantity']*current_state['original_price'], current_state['symbol'],current_state['original_buy_time_readable'], get_time()]
    #     # append_or_create_data('./binance_' + str(current_state['look_back']) + '_trades/'+ str(current_state['look_back']) + '_trade_data', data_to_save)
    # # NEW WAY: keep one array, use dict not array, record volume data (24hr + past 10 trades)
    # volume_ten_candles_btc = .01
    # if 'trailing_volumes' in current_state and len(current_state['trailing_volumes']) > 10:
    #     trailing_volumes = current_state['trailing_volumes']
    #     volume_ten_candles_btc = float(numpy.sum(trailing_volumes[-10:]))
    #     # print('-------Debug')
    #     # print('trailing_volumes', len(current_state['trailing_volumes']), current_state['trailing_volumes'])
    #     # print('sum', float(numpy.sum(trailing_volumes[-10:])))
    # volume_twentyfour_hr_btc = .01
    # try:
    #     # ie: https://www.binance.com/api/v1/ticker/24hr?symbol=ETHBTC
    #     url = "https://api.binance.com/api/v1/ticker/24hr?symbol=" + current_state['symbol']
    #     data = requests.get(url).json()
    #     volume_twentyfour_hr_btc = float(data['quoteVolume'])
    # except Exception as e:
    #     print('could not get volume_twentyfour_hr_btc for', current_state['symbol'])
    #     print(e)
    #     sys.exit()
    # volume_twentyfour_hr_ratio = invested_btc / volume_twentyfour_hr_btc
    # volume_ten_candles_ratio = invested_btc / volume_ten_candles_btc
    # recorded_trade = {
    #     'symbol': current_state['symbol'],
    #     'invested_btc': invested_btc,
    #     'profit_btc': profit_from_trade,
    #     'profit_percent': percent_profit_from_trade,
    #     'time_buy_human': current_state['original_buy_time_readable'],
    #     'time_buy_epoch': current_state['original_buy_time'],
    #     'time_end_human': get_time(),
    #     'time_end_epoch': int(time.time()),
    #     'look_back': current_state['look_back'],
    #     'largest_bitcoin_order': current_state['largest_bitcoin_order'],
    #     'part_of_bitcoin_to_use': current_state['part_of_bitcoin_to_use'],
    #     'volume_ten_candles_btc': volume_ten_candles_btc,
    #     'volume_ten_candles_ratio': volume_ten_candles_ratio,
    #     'volume_twentyfour_hr_btc': volume_twentyfour_hr_btc,
    #     'volume_twentyfour_hr_ratio': volume_twentyfour_hr_ratio,
    #     'current_state': current_state
    # }
    recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['look_back'], current_state['original_buy_time']]
    file_path_all_trades = './binance_all_trades_history/binance_all_trades_history.pklz'
    append_data(file_path_all_trades, recorded_trade)

    # update program state
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False)
    pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + current_state['symbol'] + '.pklz', False)
    print('################## wrote profit and freed coin....', current_state['symbol'])

    if profit_from_trade < -.01:
        current_state['state'] = 'sleeping'
        pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')
        time.sleep(60*60*12)

def get_order_book_local(symbol):
    while True:
        order_book = pickle_read('./recent_order_books/'+symbol +'.pklz')
        if order_book == False:
            time.sleep(.1)
            continue
        return order_book

def get_first_in_line_price_buying(current_state):

    order_book = get_order_book_local(current_state['symbol'])
    # pprint(order_book)
    # bids & asks.... 0=price, 1=qty
    first_bid = float(order_book['bids'][0][0])
    second_bid = float(order_book['bids'][1][0])
    second_price_to_check = first_bid - 3*current_state['min_price']
    second_price_to_buy = float_to_str(round(second_bid + current_state['min_price'], current_state['price_decimals']))
    price_to_buy = float_to_str(round(first_bid + current_state['min_price'], current_state['price_decimals']))

    return price_to_buy,first_bid, second_price_to_buy, second_bid, second_price_to_check


def get_first_in_line_price(current_state):
    order_book = get_order_book_local(current_state['symbol'])
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

        time.sleep(.03)



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

    if (current_state['state'] == 'sleeping'):
        print('sleeping...', current_state['symbol'])
        time.sleep(60*60*10)
        pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False, '******could not write state buy from stae******')
        return

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

    # if (symbol['symbol'] == 'ETHBTC') and (time.localtime().tm_min%2 == 0 and time.localtime().tm_sec == 1 or time.localtime().tm_sec == 2):
    #     print('buy_coin() still alive', symbol['symbol'], get_time())

    if time.localtime().tm_min == 2:
        print("started buy coin ", symbol['symbol'], get_time())
        order_book = pickle_read('./recent_order_books/'+symbol['symbol'] +'.pklz')
        try:
            print("current price:", order_book['bids'][0][0], symbol['symbol'], get_time())
        except Exception as e:
            print('symbol does not have a price:', symbol['symbol'])
            print(e)

    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    current_state = load_current_state(symbol['symbol'], file_number, length)

    if isinstance(current_state,dict):
        print('loading state to sell coin..', current_state['symbol'])
        buy_coin_from_state(current_state)
        return

    try:

        minutes = 1

        largest_bitcoin_order = .1
        part_of_bitcoin_to_use = .35
        price_to_start_buy_factor = 1.003

        sell_price_drop_factor = .996
        buy_price_increase_factor = 1.002

        price_to_buy_factor_array = [0,.977, .969, .973, .965, .962, .96, .958, .95, .956, .95]
        price_to_sell_factor_array = [0,.995, .993, .987, .995, .992, .989, .991, .986, .986, .986]
        price_to_sell_factor_2_array = [0,.982, .98, .984, .985, .984, .983, .982, .982, .982, .981]
        price_to_sell_factor_3_array = [0,.96, .969, .965, .966, .965, .964, .964, .963, .963, .963]
        lower_band_buy_factor_array = [0,1.01, 1.15, 1.09, 1.055, 1.09, 1.12, 1.15, 1.16, 1.19, 1.19]
        minutes_until_sale_array = [0,6,6,4,6,4,4,4,4,4]
        minutes_until_sale_2_array = [0,20,24,12,22,12,12,12,12,12]
        minutes_until_sale_3 = 45

        datapoints_trailing = 230


        while time.localtime().tm_sec < 3:
            time.sleep(.1)

        data = []

        end_time = int(time.time())*1000
        start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
        url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
        data = requests.get(url).json()

        if isinstance(data, basestring):
            print('API request failed, exiting', symbol['symbol'])
            return

        trailing_volumes = []
        trailing_movement = []
        trailing_lows = []
        trailing_highs = []
        trailing_candles = []
        for index, candle in enumerate(data):
            if len(trailing_movement) >= datapoints_trailing:
                break
            trailing_volumes.append(float(candle[7])) # 5 is symbol volume, 7 is quote asset volume (BTC)
            trailing_movement.append(abs(float(candle[4])-float(candle[1])))
            trailing_highs.append(float(candle[2]))
            trailing_lows.append(float(candle[3]))
            trailing_candles.append(candle)


        while time.localtime().tm_sec < 1 or time.localtime().tm_sec > 2:

            order_book = get_order_book_local(symbol['symbol'])

            time.sleep(.3)
            current_price = float(order_book['bids'][0][0])

            # if (symbol['symbol'] == 'ETHBTC'):
            #     print('about to check lookback', symbol['symbol'], 'current_price',  current_price, get_time())

            look_back_schedule = [4,1,2]

            for look_back in look_back_schedule:

                price_to_start_buy = float(data[index-look_back][4])*price_to_buy_factor_array[look_back]*price_to_start_buy_factor

                if current_price <= price_to_start_buy:

                    should_buy = False

                    if lower_band_buy_factor_array[look_back] < 100:
                        candles_for_look_back = fn.get_n_minute_candles(look_back, data[index-22*look_back-1:index])
                        candles_for_look_back, smart_trailing_candles = fn.add_bollinger_bands_to_candles(candles_for_look_back)
                        lower_band_for_index = candles_for_look_back[-1][14]
                        band_ok_value = lower_band_for_index*lower_band_buy_factor_array[look_back]
                        band_ok = current_price < band_ok_value

                    else:
                        band_ok = True

                    if band_ok:
                        should_buy = True

                    if should_buy:

                        lower_band_buy_factor = lower_band_buy_factor_array[look_back]
                        price_to_buy_factor = price_to_buy_factor_array[look_back]
                        price_to_sell_factor = price_to_sell_factor_array[look_back]
                        price_to_sell_factor_2 = price_to_sell_factor_2_array[look_back]
                        price_to_sell_factor_3 = price_to_sell_factor_3_array[look_back]
                        minutes_until_sale = minutes_until_sale_array[look_back]
                        minutes_until_sale_2 = minutes_until_sale_2_array[look_back]


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
                        append_data(file_path_all_trades_attempts, recorded_trade_attempt)

                        print('-------------------buy!', symbol['symbol'], 'look_back', look_back, price_to_buy, get_time())

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
                        current_state['original_buy_time_readable'] = get_time()
                        current_state['symbol'] = symbol['symbol']
                        current_state['orderId'] = False
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
                        print('max price for', symbol['symbol'], price_to_buy_max)
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

                            time.sleep(.03)


                        if current_state['executedQty'] < current_state['min_quantity']:
                            print('[last line reached] no one bought cancel order - freeing coin', current_state['symbol'], get_time())
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

                        return False


    except Exception as e:
        print('some error - freeing coin:', symbol['symbol'])
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
        min_symbol_volume = 450
        global socket_list
        socket_list = []
        for s in symbols:
            symbol = symbols[s]
            if float(symbol['24hourVolume']) > min_symbol_volume:
                socket_list.append(symbol['symbol'].lower() + '@depth20')
                total_btc_coins += 1
                symbols_trimmed[s] = symbol

        print('total_btc_coins with volume >', min_symbol_volume, '---', total_btc_coins)

    except Exception as e:
            print(e)
            sys.exit()

    file_start = file_number*total_btc_coins/total_files
    file_end = (file_number+1)*total_btc_coins/total_files

    loops = 0
    for s in symbols_trimmed:
        symbol = symbols_trimmed[s]

        if loops >= file_start and loops < file_end:
            t = Thread(target=buy_coin_thread, args=[symbol, file_number])
            t.start()

        loops += 1


# "worker"
def buy_coin_thread(symbol, file_number):

    # api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    # api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    # client = Client(api_key, api_secret)
    # bm = BinanceSocketManager(client)
    # conn_key = bm.start_depth_socket(symbol['symbol'], process_depth_socket, depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)
    # #socket_list = [symbol['symbol'].lower() + '@depth20']
    # #conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes_order_book_single)
    # bm.start()

    while True:

        buy_coin(symbol, '1m', file_number)


# file_path = './binance_30m_trades/30m_trades.pklz'
def append_data(file_path, data):
    data_points = pickle_read(file_path)
    data_points.append(data)
    pickle_write(file_path, data_points)

def append_or_create_data(file_path, data):
    is_file = os.path.isfile(file_path)
    if is_file:
        data_points = pickle_read(file_path)
        data_points.append(data)
        pickle_write(file_path, data_points)
        #print('file updated')
    else:
        #save the file first time
        pickle_write(file_path, [data])
        #print('file created')

def buy_coin_test(symbol):
    print('hi')