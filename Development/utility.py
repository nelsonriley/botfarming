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
import utility_2 as ut2



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
        #print('ERROR in pickle_read()')
        #print(e)
        return False
        
def pickle_read_test(file_path, file_was_in_use=False):
    try:
        # file_exists = os.path.isfile(file_path)
        # if not file_exists:
        #     print('sleeping in pickle_read_test')
        #     time.sleep(0.1)
        f = gzip.open(file_path,'rb')
        data = pickle.load(f)
        f.close()
        return data
    except Exception as e:
        if not file_was_in_use:
            time.sleep(1.5)
            pickle_read_test(file_path, file_was_in_use=True)
        # print('ERROR in pickle_read_test() after retrying read', file_path, e)
        # print(e)
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

def float_to_str(f, precision=20):
    import decimal
    ctx = decimal.Context()
    ctx.prec = precision
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
        if 'stream' in msg:
            if 'depth' in msg['stream']:
                symbol = msg['stream'].split('@')[0].upper()
                print(symbol,  msg['data']['bids'][0][0], get_time())
                time.sleep(5)
        else:
            print('socket msg has no stream key, printing whole msg so we can figure out what the response is')
            pprint(msg)


def process_socket_pushes_order_book(msg):
    if not 'stream' in msg:
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
            msg['data']['time'] = int(time.time())
            pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+symbol+'.pklz', msg['data'])

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
    pickle_write('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz', symbols_for_save)

    symbols_saved = pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
    print('btc symbols saved:', len(symbols_saved))


def cancel_buy_order(current_state):
    
    order_id_of_current_state = current_state['orderId']

    try:
        buy_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print(current_state['symbol'], current_state['version'], 'could not cancel buy order (no order id exists any longer)')

    current_state['state'] = 'buying'
    current_state['orderId'] = False
    current_state['last_update_time'] = int(time.time())
    pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state******')
    
    buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=order_id_of_current_state)
    current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
    if float(buy_order_info['price']) != 0:
        current_state['original_price'] = float(buy_order_info['price'])
    current_state['last_update_time'] = int(time.time())
    pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state******')
    

    return current_state

def cancel_sale_order(current_state):

    order_id_of_current_state = current_state['orderId']

    try:
        sale_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print(current_state['symbol'], current_state['version'], 'could not cancel sale order')

    current_state['state'] = 'selling'
    current_state['orderId'] = False
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    current_state['last_update_time'] = int(time.time())
    pickle_write(current_state_path, current_state, '******could not write state******')

    sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=order_id_of_current_state)

    current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
    current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
    current_state['last_update_time'] = int(time.time())
    pickle_write(current_state_path, current_state, '******could not write state******')

    return current_state

def create_buy_order(current_state, price_to_buy):

    maximum_order_to_buy = float_to_str(round(current_state['largest_buy_segment'], current_state['quantity_decimals']))
    maximum_possible_buy = float_to_str(round(current_state['original_amount_to_buy'] - current_state['executedQty'], current_state['quantity_decimals']))
    #quantity_to_buy = min(float(maximum_order_to_buy), float(maximum_possible_buy))
    #quantity_to_buy = maximum_possible_buy
    quantity_to_buy = min(float(maximum_possible_buy),float(maximum_order_to_buy))

    # DEBUGGER
    # print('qty', quantity_to_buy, 'price', price_to_buy)

    buy_order = current_state['client'].order_limit_buy(symbol=current_state['symbol'], quantity=quantity_to_buy, price=price_to_buy)

    current_state['state'] = 'buying'
    current_state['orderId'] = buy_order['orderId']
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    current_state['last_update_time'] = int(time.time())
    pickle_write(current_state_path, current_state, '******could not write state 2nd sell******')

    return current_state

def create_sale_order(current_state, price_to_sell, market=False):

    max_quantity = float_to_str(round(current_state['largest_bitcoin_order']/float(price_to_sell),current_state['quantity_decimals']))
    order_size = min(float(max_quantity), float(current_state['executedQty']))

    if market:
        sale_order = current_state['client'].order_market_sell(symbol=current_state['symbol'], quantity=order_size)
    else:
        sale_order = current_state['client'].order_limit_sell(symbol=current_state['symbol'], quantity=order_size, price=price_to_sell)

    current_state['state'] = 'selling'
    current_state['orderId'] = sale_order['orderId']
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    current_state['last_update_time'] = int(time.time())
    pickle_write(current_state_path, current_state, '******could not write state 2nd sell******')

    return current_state

def calculate_profit_and_free_coin(current_state, strategy='ryan'):
    # also save trade to trade history

    print(current_state['symbol'], current_state['version'], 'coin sold, calculating profit and freeing coin', get_time())
    percent_profit_from_trade = (current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price'])/(current_state['original_quantity']*current_state['original_price'])
    profit_from_trade = current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price']
    invested_btc = current_state['original_quantity']*current_state['original_price']
    print(current_state['symbol'], current_state['version'], '######PROFIT profit was, absoulte profit, percent profit, amount invested', float_to_str(profit_from_trade, 8), float_to_str(percent_profit_from_trade, 5), float_to_str(invested_btc,8), get_time())

    if strategy == 'ryan':
        recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['look_back'], current_state['original_buy_time'], get_time()]
    if strategy == '24hr_1min_drop':
        recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['original_buy_time']]

    file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history.pklz'
    if strategy == '24hr_1min_drop':
        file_path_all_trades = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/binance_all_trades_history_24hr_1min_drop.pklz'
    append_data(file_path_all_trades, recorded_trade)

    # update program state
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    pickle_write(current_state_path, False)
    print(current_state['symbol'], current_state['version'], '################## wrote profit and freed coin....')

    # ignore trades we have big losses on for 1 hour
    if profit_from_trade < -.01:
        current_state['state'] = 'sleeping'
        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state******')
        time.sleep(60*60*1)

def get_order_book_local(symbol):
    while True:
        order_book = pickle_read('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+symbol +'.pklz')
        if order_book == False:
            #print('could not get orderbook for ', symbol)
            time.sleep(.1)
            continue
        return order_book

def get_first_in_line_price_buying(current_state, buy_order_info):

    order_book = get_order_book_local(current_state['symbol'])
    total_bitcoin_of_bids = 0
    max_bitcoin_in_front = .02
    for bids in order_book['bids']:
        if buy_order_info != False and (float(buy_order_info['price']) == float(float(bids[0]))):
            amount_of_others_bitcoin = float(bids[0])*float(bids[1]) - float(buy_order_info['origQty']) + float(buy_order_info['executedQty'])
            amount_of_others_bitcoin = max(0, amount_of_others_bitcoin)
            total_bitcoin_of_bids += amount_of_others_bitcoin
        else:
            total_bitcoin_of_bids += float(bids[0])*float(bids[1])
        if total_bitcoin_of_bids > max_bitcoin_in_front:
            price_to_buy = float_to_str(round(float(bids[0]) + current_state['min_price'], current_state['price_decimals']))
            break
   
    return price_to_buy


def get_first_in_line_price(current_state, sale_order_info):
    
    order_book = get_order_book_local(current_state['symbol'])
    total_bitcoin_of_asks = 0
    max_bitcoin_in_front = .02
    for asks in order_book['asks']:
        if sale_order_info != False and (float(sale_order_info['price']) == float(float(asks[0]))):
            amount_of_others_bitcoin = float(asks[0])*float(asks[1]) - float(sale_order_info['origQty']) + float(sale_order_info['executedQty'])
            amount_of_others_bitcoin = max(0, amount_of_others_bitcoin)
            total_bitcoin_of_asks += amount_of_others_bitcoin
        else:
            total_bitcoin_of_asks += float(asks[0])*float(asks[1])
        if total_bitcoin_of_asks > max_bitcoin_in_front:
            price_to_sell = float_to_str(round(float(asks[0]) - current_state['min_price'], current_state['price_decimals']))
            break
    first_bid = float(order_book['bids'][0][0])
    
    return price_to_sell, first_bid


def sell_coin_with_order_book_use_min(current_state):
    
    print(current_state['symbol'], current_state['version'],'########### - Selling... at minimum price',  current_state['price_to_sell'], get_time())
    
    try:

        if current_state['executedQty'] >= current_state['min_quantity']:
    
            keep_price = False
            started_second_round = False
            started_give_up = False
            started_give_up_2 = False
            minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
            minutes_until_change = current_state['minutes_until_sale'] - minutes_since_start
            minutes_to_run = current_state['minutes_until_sale_final'] - minutes_since_start
        
            time_to_change = int(time.time()) + minutes_until_change * 60
            time_to_give_up = int(time.time()) + minutes_to_run * 60
            while True:
                sale_order_info = False
                if current_state['orderId'] != False:
                    sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                    if sale_order_info['status'] == 'FILLED':
                        current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
                        current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
                        current_state['state'] = 'selling'
                        current_state['orderId'] = False
                        current_state['last_update_time'] = int(time.time())
                        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
                        if current_state['executedQty'] < current_state['min_quantity']:
                            break
                    
                if int(time.time()) >= time_to_give_up:
                    if started_give_up == False:
                        started_give_up = True
                        print(current_state['symbol'], current_state['version'], 'Started give up 1, reduced price increase factor by half')
                        current_state['price_increase_factor'] = current_state['price_increase_factor']*.995
                        current_state['last_update_time'] = int(time.time())
                        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
                
                if int(time.time()) >= 1.5*time_to_give_up:
                    if started_give_up_2 == False:
                        started_give_up_2 = True
                        print(current_state['symbol'], current_state['version'],'Started give up 2, reduced price increase factor by half again')
                        current_state['price_increase_factor'] = current_state['price_increase_factor']*.9975
                        current_state['last_update_time'] = int(time.time())
                        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
        
                first_in_line_price, first_bid = get_first_in_line_price(current_state, sale_order_info)
                if time.localtime().tm_sec < 1:
                    if keep_price == True:
                        if first_bid < current_state['compare_price']:
                            current_state['compare_price'] = first_bid
                    else:
                        current_state['compare_price'] = first_bid
                    current_state['last_update_time'] = int(time.time())
                    pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
                
                if int(time.time()) < time_to_change:
                    price_to_sell_min = current_state['price_to_sell']
                else:
                    if started_second_round == False:
                        started_second_round = True
                        print(current_state['symbol'], current_state['version'],'######## starting second round of selling... sell at price', current_state['compare_price']*current_state['price_increase_factor'], get_time())
                    price_to_sell_min_1 = current_state['compare_price']*current_state['price_increase_factor']
                    price_to_sell_min_2 = current_state['price_to_sell']
                    price_to_sell_min = min(price_to_sell_min_1, price_to_sell_min_2)
        
                if float(first_in_line_price) >= price_to_sell_min:
                    if started_second_round == True:
                        keep_price = True
                    if current_state['orderId'] != False:
                        sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                        
                        #print('prices for selling, first_in_line_price, sale_order_info_price, first_in_line_price+min_price', first_in_line_price, sale_order_info['price'], float(first_in_line_price) + current_state['min_price'], current_state['symbol'])
                        if float(first_in_line_price) + current_state['min_price'] < float(sale_order_info['price']) or float(first_in_line_price) >  float(sale_order_info['price']) +  3*current_state['min_price']:
                            #print('price not close canceling sale order...', current_state['symbol'])
                            current_state = cancel_sale_order(current_state)
                            if current_state['executedQty'] < current_state['min_quantity']:
                                break
                            current_state = create_sale_order(current_state, first_in_line_price)
                    else:
                        current_state = create_sale_order(current_state, first_in_line_price)
                else:
                    if current_state['orderId'] != False:
                        current_state = cancel_sale_order(current_state)
                time.sleep(.03)
        
        calculate_profit_and_free_coin(current_state)
        return True
    
    except Exception as e:
        print(e)
        print_exception()
        error_as_string = str(e)
        if error_as_string.find('Account has insufficient balance for requested action.') >= 0:
            print(current_state['symbol'], current_state['version'], 'error selling, but account has insufficient balance, so calculating profit and freeing coin')
            calculate_profit_and_free_coin(current_state)
            return True
        if error_as_string.find('Filter failure: MIN_NOTIONAL') >= 0:
            print(current_state['symbol'], current_state['version'], 'error selling, MIN_NOTIONAL error, so probably coin has sold mostly, so calculating profit and freeing coin')
            calculate_profit_and_free_coin(current_state)
            return True
        print(current_state['symbol'], current_state['version'], 'error selling')
        return False
    

def sell_with_order_book(current_state, price_to_sell, minutes_until_sale):

    started_selling = False
    minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
    minutes_to_run = minutes_until_sale - minutes_since_start

    time_to_give_up = int(time.time()) + minutes_to_run * 60
    price_to_sell_min = current_state['sell_price_drop_factor'] * price_to_sell
    print(current_state['symbol'], current_state['version'], '########price_to_sell_min', price_to_sell_min)
    while True:
        if current_state['orderId'] != False:
            sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
            if sale_order_info['status'] == 'FILLED':
                current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
                current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
                current_state['state'] = 'selling'
                current_state['orderId'] = False
                pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
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

def buy_coin_from_state(current_state, strategy='ryan'):


    try:
        print(current_state['symbol'], current_state['version'],'buy coin from state', 'strategy', strategy)
        current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    
        if (current_state['state'] == 'sleeping'):
            print(current_state['symbol'], current_state['version'], 'sleeping...')
            sleep_minutes = 30
            while True:
                current_state['last_update_time'] = int(time.time())
                pickle_write(current_state_path, current_state, '******could not write state buy from stae******')
                time.sleep(60)

            pickle_write(current_state_path, False, '******could not write state buy from stae******')
            return
    
        if (current_state['state'] == 'buying'):
    
            if current_state['orderId'] != False:
                current_state = cancel_buy_order(current_state)
    
            if float(current_state['executedQty']) < current_state['min_quantity']:
                print(current_state['symbol'], current_state['version'], '######buy order canceled, was never filled, exiting')
                pickle_write(current_state_path, False, '******could not write state buy from stae******')
                if strategy == 'ryan':
                    pickle_write(current_state_path, False)
                return
            else:
                current_state['state'] = 'selling'
                current_state['original_quantity'] = current_state['executedQty']
                pickle_write(current_state_path, current_state, '******could not write state******')
    
    
        ##are selling...
        print(current_state['symbol'], current_state['version'],'######buy_coin_from_state() selling..')
    
        if current_state['orderId'] > 0:
    
            print(current_state['symbol'], current_state['version'], '######sale order exisits canceling it..')
            current_state = cancel_sale_order(current_state)
            if current_state['executedQty'] < current_state['min_quantity']:
                calculate_profit_and_free_coin(current_state)
                return
    
        print(current_state['symbol'], current_state['version'],'buy_coin_from_state() no open orders, selling coin..', 'strategy', strategy)
        if strategy == 'ryan':
            coin_sold = sell_coin_with_order_book_use_min(current_state)
        if strategy == '24hr_1min_drop':
            ut2.sell_for_24hr_1min_drop(current_state)
        
        if coin_sold:
            print(current_state['symbol'], current_state['version'],'finished order - freeing coin')
            print('#########################')
            return True
    
    except Exception as e:
        print(current_state['symbol'], current_state['version'], 'some error - freeing coin: in buy_coin_from_state')
        print(e)
        print_exception()
        time.sleep(60*4)
        return False


def buy_coin(symbol, length, file_number):

    # if (symbol['symbol'] == 'ETHBTC') and (time.localtime().tm_min%2 == 0 and time.localtime().tm_sec == 1 or time.localtime().tm_sec == 2):
    #     print('buy_coin() still alive', symbol['symbol'], get_time())

    # if time.localtime().tm_min == 2:
    #     print("started buy coin ", symbol['symbol'], get_time())
    #     order_book = pickle_read('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+symbol['symbol'] +'.pklz')
    #     try:
    #         print("current price:", order_book['bids'][0][0], symbol['symbol'], get_time())
    #     except Exception as e:
    #         print('symbol does not have a price:', symbol['symbol'])
    #         print(e)

    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    for version in range(0,10):
        current_state = False
        try:
            f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '_V' + str(version) +  '.pklz','rb')
            current_state = pickle.load(f)
            f.close()
        except Exception as e:
            current_state = False
        
        if isinstance(current_state,dict) and int(time.time()) - current_state['last_update_time'] > 65:
            print(current_state['symbol'], version ,'********#######****** starting thread to run buy_coin_from_state..')
            t = Thread(target=buy_coin_from_state, args=[current_state])
            t.start()
        
    current_state = False        

    try:

        minutes = 1

        largest_bitcoin_order = min(float(symbol['24hourVolume'])/450*.075, .15)
        largest_bitcoin_order_buying = min(float(symbol['24hourVolume'])/450*.15, .35)
        part_of_bitcoin_to_use = min(float(symbol['24hourVolume'])/450*.25, .45)
        price_to_start_buy_factor = 1.003

        sell_price_drop_factor = .997
        buy_price_increase_factor = 1.002

        price_to_buy_factor_array = [0,.977, .969, .973, .965, .962, .96, .958, .95, .956, .95]
        price_to_sell_factor_array = [0,.977, .969, .973, .965, .962, .96, .958, .95, .956, .95]
        lower_band_buy_factor_array = [0,1.01, 1.15, 1.09, 1.055, 1.09, 1.12, 1.15, 1.16, 1.19, 1.19]
        price_increase_factor_array = [0,1.021,1.021,1.021,1.021,1.021,1.021,1.021,1.021,1.021,1.021]
        
        minutes_until_sale = 6
        
        minutes_until_sale_final = 45

        datapoints_trailing = 230

        look_back_schedule = [1,2,4,5,7]
        look_back_gains = [0,0,0,0,0,0,0,0,0,0]
        look_back_wins = [0,0,0,0,0,0,0,0,0,0]
        look_back_losses = [0,0,0,0,0,0,0,0,0,0]
        max_look_back_gain = 0
        
        should_trade = False

        for look_back in look_back_schedule:
            
            look_back_optimized = pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '_V12.pklz')
            if look_back_optimized != False:
                price_to_buy_factor_array[look_back] = look_back_optimized['optimal_buy_factor']
                price_to_sell_factor_array[look_back] = look_back_optimized['optimal_sell_factor']
                lower_band_buy_factor_array[look_back] = look_back_optimized['optimal_band_factor']
                price_increase_factor_array[look_back] = look_back_optimized['optimal_increase_factor']
                look_back_gains[look_back] = look_back_optimized['gain']
                look_back_wins[look_back] = look_back_optimized['wins']
                look_back_losses[look_back] = look_back_optimized['losses']
                if look_back_gains[look_back] > max_look_back_gain:
                    max_look_back_gain = look_back_gains[look_back]
            else:
                #print('No trading parameters for', symbol['symbol'], 'look_back', look_back)
                look_back_gains[look_back] = 0
                
            
        if max_look_back_gain <= 0:
            print(symbol['symbol'], 'This symbol has bad or no results and we should not trade on it. max_look_back_gain', max_look_back_gain)
            time.sleep(30*30)
            return

        while time.localtime().tm_sec < 3:
            time.sleep(.1)

        data = []

        end_time = int(time.time())*1000
        start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
        url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
        data = requests.get(url).json()

        if isinstance(data, basestring):
            print(symbol['symbol'], 'API request failed, exiting', symbol['symbol'])
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
            
            # if (symbol['symbol'] == 'ETHBTC'):
            #     print(symbol['symbol'],'time since orderbook update', int(time.time()) - order_book['time'])
            
            
            if int(time.time()) - order_book['time'] > 30:
                time.sleep(1)
                continue

            time.sleep(.3)
            current_price = float(order_book['bids'][0][0])

            # if (symbol['symbol'] == 'ETHBTC'):
            #     print('about to check lookback', symbol['symbol'], 'current_price',  current_price, get_time())

            for look_back in look_back_schedule:
                
                if look_back_gains[look_back] <= 0:
                    continue

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
                        price_increase_factor = price_increase_factor_array[look_back]


                        if lower_band_buy_factor < 100:
                            price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(data[index-look_back][4])*price_to_buy_factor)
                        else:
                            price_to_buy = float(data[index-look_back][4])*price_to_buy_factor


                        print(symbol['symbol'], '-------------------buy!', 'look_back', look_back, 'price', price_to_buy , 'price_to_buy_factor', price_to_buy_factor_array[look_back], 'price_to_sell_factor',price_to_sell_factor_array[look_back] , 'price_increase_factor',price_increase_factor_array[look_back] , minutes_until_sale, 'look_back_gain', look_back_gains[look_back], 'look_back_wins', look_back_wins[look_back], 'look_back_losses', look_back_losses[look_back], 'part_of_bitcoin_to_use', part_of_bitcoin_to_use, get_time())

                        if lower_band_buy_factor < 100:
                            price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(data[index-look_back][4])*price_to_buy_factor)
                        else:
                            price_to_buy = float(data[index-look_back][4])*price_to_buy_factor
                        
                        price_to_sell = float(data[index-look_back][4])*price_to_sell_factor

                        amount_to_buy = part_of_bitcoin_to_use/price_to_buy
                        largest_buy_segment = largest_bitcoin_order_buying/price_to_buy

                        price_decimals = get_min_decimals(symbol['filters'][0]['minPrice'])

                        quantity_decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                        # quantity_decimals = get_min_decimals_new(symbol['filters'][2]['minNotional'])
                        
                        for version in range(0,10):
                            state_of_version = pickle_read('/home/ec2-user/environment/botfarming/Development/program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '_V'+ str(version) + '.pklz')
                            if state_of_version == False:
                                break
                        if version == 9:
                            print(symbol['symbol'], 'too many versions of this coin are trading, exiting..')
                            return True
                            
                            

                        current_state = {}
                        current_state['state'] = 'buying'
                        current_state['look_back'] = look_back
                        current_state['version'] = str(version)
                        current_state['sell_price_drop_factor'] = sell_price_drop_factor
                        current_state['original_amount_to_buy'] = amount_to_buy
                        current_state['largest_bitcoin_order'] = largest_bitcoin_order
                        current_state['part_of_bitcoin_to_use'] = part_of_bitcoin_to_use
                        current_state['largest_buy_segment'] = largest_buy_segment
                        current_state['last_update_time'] = int(time.time())
                        current_state['original_buy_time'] = int(time.time())
                        current_state['original_buy_time_readable'] = get_time()
                        current_state['symbol'] = symbol['symbol']
                        current_state['orderId'] = False
                        current_state['executedQty'] = 0
                        current_state['total_revenue'] = 0
                        current_state['minutes_until_sale'] = minutes_until_sale
                        current_state['minutes_until_sale_final'] = minutes_until_sale_final
                        current_state['price_to_buy'] = price_to_buy
                        current_state['price_to_sell'] = price_to_sell
                        current_state['compare_price'] = price_to_buy
                        current_state['price_increase_factor'] = price_increase_factor
                        current_state['minimum_price_seen'] = price_to_buy
                        current_state['length'] = length
                        current_state['file_number'] = str(file_number)
                        current_state['client'] = client
                        current_state['error_cancel_order'] = False
                        current_state['price_decimals'] = price_decimals
                        current_state['quantity_decimals'] = quantity_decimals
                        current_state['min_price'] = float(symbol['filters'][0]['minPrice'])
                        current_state['min_quantity'] = min(float(symbol['filters'][1]['minQty']), float(symbol['filters'][2]['minNotional']))

                        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol']  + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state******')


                        time_to_give_up = int(time.time()) + 60
                        price_to_buy_max = price_to_buy*buy_price_increase_factor
                        amount_to_stop_buying = part_of_bitcoin_to_use/price_to_buy_max - current_state['min_quantity']
                        print(current_state['symbol'], current_state['version'],'################max price for', price_to_buy_max)
                        while True:
                            buy_order_info = False
                            if current_state['orderId'] != False:
                                buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                                if buy_order_info['status'] == 'FILLED':
                                    current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
                                    current_state['original_price'] = float(buy_order_info['price'])
                                    current_state['state'] = 'buying'
                                    current_state['orderId'] = False
                                    pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not write state 2nd sell******')
                                    if current_state['executedQty'] >= amount_to_stop_buying:
                                        break

                            if int(time.time()) >= time_to_give_up:
                                if current_state['orderId'] != False:
                                    current_state = cancel_buy_order(current_state)
                                break

                            first_in_line_price = get_first_in_line_price_buying(current_state, buy_order_info)
                            if float(first_in_line_price) > price_to_buy_max:
                                if current_state['orderId'] != False:
                                    current_state = cancel_buy_order(current_state)
                                    if current_state['executedQty'] >= amount_to_stop_buying:
                                        break
                            else:
                                if current_state['orderId'] != False:
                                    buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                                    if float(first_in_line_price) - current_state['min_price'] > float(buy_order_info['price']) or float(first_in_line_price) <  float(buy_order_info['price']) -  3*current_state['min_price']:
                                        current_state = cancel_buy_order(current_state)
                                        if current_state['executedQty'] >= amount_to_stop_buying:
                                            break
                                        current_state = create_buy_order(current_state, first_in_line_price)
                                else:
                                    current_state = create_buy_order(current_state, first_in_line_price)

                            time.sleep(.03)


                        if current_state['executedQty'] < current_state['min_quantity']:
                            print(current_state['symbol'], current_state['version'], '##############no one bought cancel order - freeing coin', get_time())
                            pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '_V' + current_state['version'] + '.pklz', False, '******could not write state inside buy coin - no one bought coin******')
                            return True


                        current_state['original_quantity'] = current_state['executedQty']
                        current_state['state'] = 'selling'
                        current_state['last_update_time'] = int(time.time())
                        pickle_write('/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz', current_state, '******could not update state to selling******')

                        print(current_state['symbol'], current_state['version'], '#########Starting a thread to sell coin')
                        t = Thread(target=sell_coin_with_order_book_use_min, args=[current_state])
                        t.start()
                        
                        time.sleep(60000)
                
                        return True


    except Exception as e:
        print(symbol['symbol'], '######some error - freeing coin:')
        print(e)
        print_exception()
        time.sleep(60*4)
        return False

def free_coin_after_candle(symbol, look_back):

    while True:
        if time.localtime().tm_sec < 2:
            print('onto next candle freeing coin with look_back...', symbol, look_back)
            pickle_write('/home/ec2-user/environment/botfarming/Development/binance_is_invested_' + str(look_back) +'m/is_invested_' + str(look_back) + 'm_' + symbol + '.pklz', False)
            return


def load_current_state(symbol, file_number, length):

    try:
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol + '_V' + current_state['version'] + '.pklz','rb')
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

        symbols = pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')

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


# file_path = '/home/ec2-user/environment/botfarming/Development/binance_30m_trades/30m_trades.pklz'
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

def get_current_price_from_ticker(s):
    ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
    ticker = ut.pickle_read(ticker_path)
    if ticker == False:
        print('IN get_current_price_from_ticker(s) FALSE')
        return False
    current_price = float(ticker['c'])
    return current_price