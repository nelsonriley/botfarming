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
import arrow
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

def write_current_state(current_state_info, current_state):
    pickle_write('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + current_state_info['length'] + '_' + current_state_info['file_number'] + '_' + current_state_info['symbol'] + '.pklz', current_state, '******could not write state******')

    

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


###########################################################################################


def cancel_buy_order(current_state):
    
    order_id_of_current_state = current_state['orderId']

    try:
        buy_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print('could not cancel buy order (no order id exists any longer)')

    current_state['state'] = 'buying'
    current_state['orderId'] = False
    write_current_state(current_state, current_state)
    
    buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=order_id_of_current_state)
    current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
    if float(buy_order_info['price']) != 0:
        current_state['original_price'] = float(buy_order_info['price'])
    write_current_state(current_state, current_state)
    

    return current_state

def cancel_sale_order(current_state):

    order_id_of_current_state = current_state['orderId']

    try:
        sale_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
    except Exception as e:
        print('could not cancel sale order')

    current_state['state'] = 'selling'
    current_state['orderId'] = False
    write_current_state(current_state, current_state)

    sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=order_id_of_current_state)

    current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
    current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
    write_current_state(current_state, current_state)

    return current_state

def create_buy_order(current_state, price_to_buy):

    maximum_order_to_buy = float_to_str(round(current_state['largest_buy_segment'], current_state['quantity_decimals']))
    maximum_possible_buy = float_to_str(round(current_state['original_amount_to_buy'] - current_state['executedQty'], current_state['quantity_decimals']))
    
    
    
    if current_state['length'] == '1m':
        quantity_to_buy = min(float(maximum_order_to_buy), float(maximum_possible_buy))
    else:
        quantity_to_buy = maximum_possible_buy

    # DEBUGGER
    # print('qty', quantity_to_buy, 'price', price_to_buy)

    buy_order = current_state['client'].order_limit_buy(symbol=current_state['symbol'], quantity=quantity_to_buy, price=price_to_buy)

    current_state['state'] = 'buying'
    current_state['orderId'] = buy_order['orderId']
    write_current_state(current_state, current_state)

    return current_state

def create_sale_order(current_state, price_to_sell, market=False):
    #print('in create sale order', price_to_sell)

    if not 'largest_bitcoin_order' in current_state:
        print(current_state['symbol'], 'largest_bitcoin_order NOT defined', get_time())
        # EXCEPTION IN (/home/nelsonriley/Development/utility.py, LINE 294 "sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_3'], current_state['minutes_until_sale_3'])"): 'largest_bitcoin_order'
        current_state['largest_bitcoin_order'] = .1

    max_quantity = float_to_str(round(current_state['largest_bitcoin_order']/float(price_to_sell),current_state['quantity_decimals']))
    order_size = min(float(max_quantity), float(current_state['executedQty']))

    if market:
        sale_order = current_state['client'].order_market_sell(symbol=current_state['symbol'], quantity=order_size)
    else:
        sale_order = current_state['client'].order_limit_sell(symbol=current_state['symbol'], quantity=order_size, price=price_to_sell)

    current_state['state'] = 'selling'
    current_state['orderId'] = sale_order['orderId']
    write_current_state(current_state, current_state)

    return current_state

def calculate_profit_and_free_coin(current_state):
    # also save trade to trade history

    print('coin sold, calculating profit and freeing coin', current_state['symbol'],get_time())
    percent_profit_from_trade = (current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price'])/(current_state['original_quantity']*current_state['original_price'])
    profit_from_trade = current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price']
    invested_btc = current_state['original_quantity']*current_state['original_price']
    print('PROFIT', current_state['symbol'] ,'profit was, absoulte profit, percent profit, amount invested', float_to_str(profit_from_trade, 8), float_to_str(percent_profit_from_trade, 5), float_to_str(invested_btc,8), get_time())

    recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['look_back'], current_state['a_b'], current_state['look_back_gains'], current_state['look_back_wins'], current_state['look_back_losses'], current_state['price_to_buy_factor'], current_state['price_to_sell_factor'], current_state['original_buy_time'], get_time()]
    
    append_data('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/'+ current_state['length'] + '_' + current_state['file_number'] + '_binance_all_trades_history.pklz', recorded_trade)

    # update program state
    write_current_state(current_state, False)
    print('################## wrote profit and freed coin....', current_state['symbol'])

    # ignore trades we have big losses on for 12 hours
    # if profit_from_trade < -.01:
    #     current_state['state'] = 'sleeping'
    #     write_current_state(current_state, current_state)
    #     time.sleep(60*60*1)

def get_order_book_local(symbol, length):
    while True:
        order_book = pickle_read('/home/ec2-user/environment/botfarming/Development/recent_order_books/' + length + '_'+symbol +'.pklz')
        if order_book == False:
            #print('could not get orderbook for ', symbol)
            time.sleep(.1)
            continue
        return order_book

def get_first_in_line_price_buying(current_state):

    order_book = get_order_book_local(current_state['symbol'], current_state['length'])
    # pprint(order_book)
    # bids & asks.... 0=price, 1=qty
    first_bid = float(order_book['bids'][0][0])
    second_bid = float(order_book['bids'][1][0])
    second_price_to_check = first_bid - 3*current_state['min_price']
    second_price_to_buy = float_to_str(round(second_bid + current_state['min_price'], current_state['price_decimals']))
    price_to_buy = float_to_str(round(first_bid + current_state['min_price'], current_state['price_decimals']))

    return price_to_buy,first_bid, second_price_to_buy, second_bid, second_price_to_check


def get_first_in_line_price(current_state):
    order_book = get_order_book_local(current_state['symbol'], current_state['length'])
    # pprint(order_book)
    # bids & asks.... 0=price, 1=qty
    first_ask = float(order_book['asks'][0][0])
    second_ask = float(order_book['asks'][1][0])
    first_bid = float(order_book['bids'][0][0])
    second_price_to_check = first_ask + 3*current_state['min_price']
    second_price_to_buy = float_to_str(round(second_ask - current_state['min_price'], current_state['price_decimals']))
    price_to_buy = float_to_str(round(first_ask - current_state['min_price'], current_state['price_decimals']))
    # print(first_ask)
    # print(price_to_buy)
    return price_to_buy,first_ask, second_price_to_buy, second_ask, second_price_to_check, first_bid

def sell_coin_with_order_book_use_min(current_state):
    print('########### - Selling...', current_state['symbol'], 'at minimum price',  current_state['price_to_sell'], 'original_buy_time_readable', current_state['original_buy_time_readable'], 'original investment', current_state['original_quantity']*current_state['original_price'], 'original price', current_state['original_price'], 'exectuedQty', current_state['executedQty'], 'look_back', current_state['look_back'], 'price to buy factor', current_state['price_to_buy_factor'], 'price_to_sell_factor', current_state['price_to_sell_factor'])
    
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
                if current_state['orderId'] != False:
                    sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                    if sale_order_info['status'] == 'FILLED':
                        current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
                        current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
                        current_state['state'] = 'selling'
                        current_state['orderId'] = False
                        write_current_state(current_state, current_state)
                        if current_state['executedQty'] < current_state['min_quantity']:
                            break
                    
                if int(time.time()) >= time_to_give_up:
                    if started_give_up == False:
                        started_give_up = True
                        current_state['price_increase_factor'] = (float(current_state['price_increase_factor'])-1)/2+1
                        print('Started give up 1, reduced price increase factor by half', current_state['symbol'], 'price_increase_factor', current_state['price_increase_factor'])
                        write_current_state(current_state, current_state)
                        
                if int(time.time()) >= 2*time_to_give_up:
                    if started_give_up_2 == False:
                        started_give_up_2 = True
                        current_state['price_increase_factor'] = (float(current_state['price_increase_factor'])-1)/2+1
                        print('Started give up 2, reduced price increase factor by half again', current_state['symbol'], 'price_increase_factor', current_state['price_increase_factor'])
                        write_current_state(current_state, current_state)
                        
                first_in_line_price, first_ask, second_in_line_price, second_ask, second_price_to_check, first_bid = get_first_in_line_price(current_state)
                if time.localtime().tm_sec < 1:
                    if keep_price == True:
                        if first_bid < current_state['compare_price']:
                            current_state['compare_price'] = first_bid
                    else:
                        current_state['compare_price'] = first_bid
                    write_current_state(current_state, current_state)
                    
                if int(time.time()) < time_to_change:
                    price_to_sell_min = current_state['price_to_sell']
                else:
                    if started_second_round == False:
                        started_second_round = True
                        print('######## starting second round of selling', current_state['symbol'], 'sell at price', current_state['compare_price']*current_state['price_increase_factor'], get_time())
                    price_to_sell_min_1 = current_state['compare_price']*current_state['price_increase_factor']
                    price_to_sell_min_2 = current_state['price_to_sell']
                    price_to_sell_min = min(price_to_sell_min_1, price_to_sell_min_2)
        
                if float(first_in_line_price) >= price_to_sell_min:
                    if started_second_round == True:
                        keep_price = True
                    if current_state['orderId'] != False:
                        sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                        if first_ask != float(sale_order_info['price']):
                            current_state = cancel_sale_order(current_state)
                            if current_state['executedQty'] < current_state['min_quantity']:
                                break
                            current_state = create_sale_order(current_state, first_in_line_price)
                        else:
                            if second_price_to_check < second_ask:
                                current_state = cancel_sale_order(current_state)
                                if current_state['executedQty'] < current_state['min_quantity']:
                                    break
                                current_state = create_sale_order(current_state, second_in_line_price)
        
                    else:
                        current_state = create_sale_order(current_state, first_in_line_price)
                else:
                    if current_state['orderId'] != False:
                        current_state = cancel_sale_order(current_state)
                
                if current_state['orderId'] != False:
                    time.sleep(5)
                else:
                    time.sleep(.1)
        
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


    try:
        print('buy coin from state', current_state['symbol'])
        
        if (current_state['state'] == 'sleeping'):
            print('sleeping...', current_state['symbol'])
            time.sleep(60*60)
            write_current_state(current_state, False)
            return
    
        if (current_state['state'] == 'buying'):
    
            if current_state['orderId'] != False:
                current_state = cancel_buy_order(current_state)
    
            if float(current_state['executedQty']) < current_state['min_quantity']:
                print('buy order canceled, was never filled, exiting')
                write_current_state(current_state, False)
                return
            else:
                current_state['state'] = 'selling'
                current_state['original_quantity'] = current_state['executedQty']
                write_current_state(current_state, current_state)
    
    
        ##are selling...
        print('buy_coin_from_state() selling..', current_state['symbol'])
    
        if current_state['orderId'] > 0:
    
            print('sale order exisits canceling it..')
            current_state = cancel_sale_order(current_state)
            if current_state['executedQty'] < current_state['min_quantity']:
                calculate_profit_and_free_coin(current_state)
                return
    
        print('buy_coin_from_state() no open orders, selling coin..', current_state['symbol'])
        
        coin_sold = sell_coin_with_order_book_use_min(current_state)
        
        
        if coin_sold:
            print('finished order - freeing coin', current_state['symbol'])
            print('#########################')
            return True
    
    except Exception as e:
        print('some error - freeing coin:', current_state['symbol'])
        print(e)
        print_exception()
        time.sleep(60*4)
        return False


def buy_coin(symbol, length, file_number):

    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    try:
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz','rb')
        current_state = pickle.load(f)
        f.close()
    except Exception as e:
        current_state = False

    if isinstance(current_state,dict):
        print('loading state to sell coin..', current_state['symbol'])
        buy_coin_from_state(current_state)
        return

    try:
        
        if length == '1d':
            minutes = 24*60
        elif length == '12h':
            minutes = 12*60
        elif length == '6h':
            minutes = 6*60
        elif length == '1m':
            minutes = 1


        largest_bitcoin_order = .1
        if length == '1d':
            part_of_bitcoin_to_use = 2.4
            gain_min = .24
            buy_price_increase_factor = 1.002
            look_back_schedule = [1,2,3,4,5,7,9,11]
        if length == '12h':
            part_of_bitcoin_to_use = 2.2
            gain_min = .19
            buy_price_increase_factor = 1.002
            look_back_schedule = [1,2,3,4,5,7,9,11]
        elif length == '6h':
            part_of_bitcoin_to_use = 2
            gain_min = .15
            buy_price_increase_factor = 1.002
            look_back_schedule = [1,2,3,4,5,7,9,11]
        elif length == '1m':
            part_of_bitcoin_to_use = .6
            gain_min = .001
            buy_price_increase_factor = 1.001
            look_back_schedule = [1,3,5,7]
            
        price_to_start_buy_factor = 1.003
        sell_price_drop_factor = .997
        

        price_to_buy_factor_array = {}
        price_to_sell_factor_array = {}
        lower_band_buy_factor_array = {}
        price_increase_factor_array = {}
        
        minutes_until_sale = 3*minutes
        
        minutes_until_sale_final = 5*minutes

        datapoints_trailing = 11

        look_back_gains = {}
        look_back_gains_ave = {}
        look_back_wins = {}
        look_back_losses = {}
        max_look_back_gain = 0
        
        a_b = random.randint(0,1)
        
        should_trade = False

        for look_back in look_back_schedule:
            
            look_back_optimized = pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '.pklz')
            
                
            if look_back_optimized != False:
                price_to_buy_factor_array[look_back] = look_back_optimized['optimal_buy_factor']
                price_to_sell_factor_array[look_back] = look_back_optimized['optimal_sell_factor']
                lower_band_buy_factor_array[look_back] = look_back_optimized['optimal_band_factor']
                price_increase_factor_array[look_back] = look_back_optimized['optimal_increase_factor']
                price_increase_factor_array[look_back] = 1.01
                look_back_gains[look_back] = look_back_optimized['gain']
                look_back_wins[look_back] = look_back_optimized['wins']
                look_back_losses[look_back] = look_back_optimized['losses']
                if look_back_optimized['wins'] + look_back_optimized['losses'] > 0:
                    look_back_gains_ave[look_back] = look_back_optimized['gain']/(look_back_optimized['wins'] + look_back_optimized['losses'])
                if look_back_gains[look_back] > max_look_back_gain:
                    max_look_back_gain = look_back_gains[look_back]
            else:
                #print('No trading parameters for', symbol['symbol'], 'look_back', look_back)
                time.sleep(60*1)
                return
            
        if max_look_back_gain <= 0:
            #print('This symbol has bad or no results and we should not trade on it ', symbol['symbol'], 'max_look_back_gain', max_look_back_gain)
            time.sleep(1*60)
            return

        while time.localtime().tm_sec < 3:
            time.sleep(.1)

        data = []

        end_time = int(time.time())*1000 + 60000
        start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
        url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
        #print(url)
        data = requests.get(url).json()

        if isinstance(data, basestring):
            print('API request failed, exiting', symbol['symbol'])
            return
        
        # if length == '1m' and (symbol['symbol'] == 'XEMBTC' or symbol['symbol'] == 'SNTBTC' or symbol['symbol'] == 'ETHBTC'):
        #     print(symbol['symbol'],'price', data[-1][4], 'price two ago', data[-2][4], 'candle end time', data[-1][0], get_readable_time(data[-1][0]), 'candle end time 2 ago', data[-2][0],  get_readable_time(data[-2][0]), 'requested end time', end_time, get_readable_time(end_time), 'need time within', get_readable_time(end_time - 60000))
        #     time.sleep(5)
        #     return
        
        if length == '1m':
            for check_back in range(1, 7):
                if data[-1*check_back][0] < end_time-2*65000*check_back:
                    print('messed up candle end time', get_readable_time(data[-1*check_back][0]), 'need time within', get_readable_time(end_time - 2*60000*check_back), 'requested end time', get_readable_time(end_time), symbol['symbol'],'price', data[-1][4], 'price two ago', data[-2][4],'check_back', check_back, )
                    time.sleep(10)
                    return
                

        trailing_volumes = []
        trailing_movement = []
        trailing_lows = []
        trailing_highs = []
        trailing_candles = []
        for index, candle in enumerate(data):
            trailing_volumes.append(float(candle[7])) # 5 is symbol volume, 7 is quote asset volume (BTC)
            trailing_movement.append(abs(float(candle[4])-float(candle[1])))
            trailing_highs.append(float(candle[2]))
            trailing_lows.append(float(candle[3]))
            trailing_candles.append(candle)


        while time.localtime().tm_sec < 1 or time.localtime().tm_sec > 2:

            order_book = get_order_book_local(symbol['symbol'], length)
            
            # if (symbol['symbol'] == 'ETHBTC'):
            #     print(symbol['symbol'],'time since orderbook update', int(time.time()) - order_book['time'])
            
            
            if int(time.time()) - order_book['time'] > 30:
                time.sleep(1)
                continue

            time.sleep(2)
            current_price = float(order_book['bids'][0][0])

            # if (symbol['symbol'] == 'ETHBTC'):
            #     print('about to check lookback', symbol['symbol'], 'current_price',  current_price, get_time())
    
            look_back_gains_ave_sorted = sorted(look_back_gains_ave, key=look_back_gains_ave.get, reverse=True)

            for look_back in look_back_gains_ave_sorted:
                
                # if symbol['symbol'] == 'ICXBTC':
                #     print(get_readable_time(data[index-look_back][0]))
                    
                
                if look_back_wins[look_back] + look_back_losses[look_back] < 1 or look_back_gains[look_back]/(look_back_wins[look_back] + look_back_losses[look_back]) < gain_min:
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
                        
                        # print ('should buy', symbol['symbol'])
                        # sys.exit()

                        lower_band_buy_factor = lower_band_buy_factor_array[look_back]
                        price_to_buy_factor = price_to_buy_factor_array[look_back]
                        price_to_sell_factor = price_to_sell_factor_array[look_back]
                        price_increase_factor = price_increase_factor_array[look_back]


                        if lower_band_buy_factor < 100:
                            price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(data[index-look_back][4])*price_to_buy_factor)
                        else:
                            price_to_buy = float(data[index-look_back][4])*price_to_buy_factor
                            
                        price_to_sell = float(data[index-look_back][4])*price_to_sell_factor


                        print('-------------------buy!', symbol['symbol'], 'current price', current_price, 'current price time', get_readable_time(order_book['time']), 'look_back', look_back, 'look back original price', data[index-look_back][4], 'look back original time', get_readable_time(data[index-look_back][0]),   'price_to_buy', price_to_buy , 'price_to_buy_factor', price_to_buy_factor_array[look_back], 'price_to_sell', price_to_sell,  'price_to_sell_factor',price_to_sell_factor_array[look_back] , 'price_increase_factor',price_increase_factor_array[look_back] , minutes_until_sale, 'look_back_gain', look_back_gains[look_back], 'look_back_wins', look_back_wins[look_back], 'look_back_losses', look_back_losses[look_back], get_time())
                        
                        

                        amount_to_buy = part_of_bitcoin_to_use/price_to_buy
                        largest_buy_segment = largest_bitcoin_order/price_to_buy

                        price_decimals = get_min_decimals(symbol['filters'][0]['minPrice'])

                        quantity_decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                        # quantity_decimals = get_min_decimals_new(symbol['filters'][2]['minNotional'])

                        current_state = {}
                        current_state['state'] = 'buying'
                        current_state['look_back'] = look_back
                        current_state['a_b'] = a_b
                        current_state['look_back_gains'] = look_back_gains[look_back]
                        current_state['look_back_wins'] = look_back_wins[look_back]
                        current_state['look_back_losses'] = look_back_losses[look_back]
                        current_state['price_to_buy_factor'] = price_to_buy_factor
                        current_state['price_to_sell_factor'] = price_to_sell_factor
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

                        write_current_state(current_state, current_state)

                        if length == '1m':
                            time_to_give_up = int(time.time()) + 120
                        else:
                            time_to_give_up = int(time.time()) + 60*minutes/15
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
                                    write_current_state(current_state, current_state)
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

                            
                            if current_state['orderId'] != False:
                                time.sleep(5)
                            else:
                                time.sleep(.03)


                        if current_state['executedQty'] < current_state['min_quantity']:
                            print('[last line reached] no one bought cancel order - freeing coin', current_state['symbol'], get_time())
                            write_current_state(current_state, False)
                            return True


                        current_state['original_quantity'] = current_state['executedQty']
                        current_state['state'] = 'selling'
                        write_current_state(current_state, current_state)
                        
                        coin_sold = sell_coin_with_order_book_use_min(current_state)

                        if coin_sold:
                            print('finished order - freeing coin', current_state['symbol'])
                            print('#########################')

                            return True

                        return False


    except Exception as e:
        print('some error - freeing coin:', symbol['symbol'])
        print(e)
        print_exception()
        time.sleep(60*4)
        return False


def run_bot_parallel(file_number, length, total_files):

    print('running bot', file_number, 'of', total_files, 'ip address:')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
    s.close()


    try:

        symbols = pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')

        total_btc_coins = 0
        symbols_trimmed = {}
        min_symbol_volume = 300
        global socket_list
        socket_list = []
        for s in symbols:
            symbol = symbols[s]
            if float(symbol['24hourVolume']) > min_symbol_volume:
                socket_list.append(symbol['symbol'].lower() + '@depth20')
                total_btc_coins += 1
                symbols_trimmed[s] = symbol
            else:
                try:
                    f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz','rb')
                    current_state = pickle.load(f)
                    f.close()
                except Exception as e:
                    current_state = False
            
                if isinstance(current_state,dict):
                    print('loading state to sell coin..', current_state['symbol'])
                    t = Thread(target=buy_coin_from_state, args=[current_state])
                    t.start()

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
            t = Thread(target=buy_coin_thread, args=[symbol, length, file_number])
            t.start()

        loops += 1


# "worker"
def buy_coin_thread(symbol, length, file_number):

    while True:

        buy_coin(symbol, length, file_number)


def append_data(file_path, data):
    data_points = pickle_read(file_path)
    data_points.append(data)
    pickle_write(file_path, data_points)

def save_data(save_params, datapoints_trailing, min_volume, minutes):
    
    for settings in save_params:

        day_folder = settings[0]
        start_time = arrow.get(settings[1]).replace(tzinfo='America/Denver')
        end_time = arrow.get(settings[2]).replace(tzinfo='America/Denver')

        path = '/home/ec2-user/environment/botfarming/Development/binance_training_data/'+day_folder
        if not os.path.exists(path):
            os.makedirs(path)

        start_end_style = True
        if start_end_style:
            
            print('STARTING CANDLES DOWNLOAD', settings, get_time())

            start = start_time.timestamp * 1000
            # print('start', start, arrow.get(int(start/1000)).to('America/Denver'))
            start = start - datapoints_trailing * minutes * 60 * 1000
            # print('start with datapoints_trailing', start, arrow.get(int(start/1000)).to('America/Denver'))
            end = end_time.timestamp * 1000
            stop = start + 400 * minutes * 60 * 1000
            last_loop = False
            if stop > end:
                stop = end
                last_loop = True
            symbols = pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
            coins = {}
            loops = 1
            while True:
                # print('loop', loops)
                loops += 1
                for s in symbols:
                    symbol = symbols[s]
                    if float(symbol['24hourVolume']) > min_volume:
                        if not symbol['symbol'] in coins:
                            coins[symbol['symbol']] = []
                        # get data from binance
                        if minutes >= 24*60:
                            days = minutes/(24*60)
                            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval=' + str(days) + 'd&startTime='+str(start)+'&endTime='+str(stop)
                        elif minutes >= 60:
                            hours = minutes/60
                            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(hours)+'h&startTime='+str(start)+'&endTime='+str(stop)
                        else:
                            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minutes)+'m&startTime='+str(start)+'&endTime='+str(stop)
                        r = requests.get(url)
                        data = r.json()
                        # if symbol['symbol'] == 'ETHBTC':
                        #     print('--------------------ETHBTC')
                        #     print(url)
                        #     print(len(data))
                        #     print(start, arrow.get(int(start/1000)).to('America/Denver'))
                        #     print(stop, arrow.get(int(stop/1000)).to('America/Denver'))
                        #     duration_in_minutes = int(stop - start)/(1000*60)
                        #     print('duration_in_minutes', duration_in_minutes)
                        #     print('--------------------ETHBTC')
                        # watch for too many API requests
                        if isinstance(data, dict):
                            print('ERROR... API Failed')
                            print(url)
                            pprint(data)
                            break
                        # add to coins[symbol] array
                        for candle in data:
                            coins[symbol['symbol']].append(candle)
                if last_loop:
                    break
                # update times for next round of API requests
                start = stop
                stop = start + 400 * minutes * 60 * 1000
                if stop > end:
                    stop = end
                    last_loop = True

            # save continuous data for each coin to disk
            print('SAVING CANDLE DATA', settings, 'for', len(coins), 'symbols', get_time())
            for symbol in coins:
                data = coins[symbol]
                # if symbol == 'ETHBTC':
                #     print('--------------------ETHBTC')
                #     print('candles =', len(data), '...should be', 12 * 60 + 230)
                #     print('first candle')
                #     pprint(data[0])
                #     print('last candle')
                #     pprint(data[-1])
                #     print('--------------------ETHBTC')
                candle_path = '/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ day_folder + '/'+ symbol +'_data_'+str(minutes)+'m.pklz'
                pickle_write(candle_path, data)

    return True

def process_socket_pushes_order_book(msg):
    if not 'stream' in msg:
        return
    elif 'depth' in msg['stream']:
            
        symbol = msg['stream'].split('@')[0].upper()
        msg['data']['time'] = int(time.time())
        pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/1m_'+symbol+'.pklz', msg['data'])
        pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/6h_'+symbol+'.pklz', msg['data'])
        pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/12h_'+symbol+'.pklz', msg['data'])
        pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/1d_'+symbol+'.pklz', msg['data'])

        if (symbol == 'ETHBTC'):  #and (time.localtime().tm_sec == 1 or time.localtime().tm_sec == 2):
            print('process_socket_pushes_order_book()', symbol, msg['data']['bids'][0][0], 'time given', get_readable_time(msg['data']['time']), 'current time', get_time())

        if (symbol == 'WAVESBTC'):
            print('process_socket_pushes_order_book()', symbol, msg['data']['bids'][0][0], 'time given', get_readable_time(msg['data']['time']), 'current time', get_time())



    
def update_order_book(min_volume, max_volume):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
    s.close()
    
    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)
    global bm
    bm = BinanceSocketManager(client)
    
    # limit symbols by 24hr volume
    
    symbol_path = '/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz'
    symbols = pickle_read(symbol_path)
    total_btc_coins = 0
    symbols_trimmed = {}
    global socket_list
    socket_list = []
    for s in symbols:
        symbol = symbols[s]
        if float(symbol['24hourVolume']) > min_volume and float(symbol['24hourVolume']) < max_volume:
            total_btc_coins += 1
            symbols_trimmed[s] = symbol
            socket_list.append(s.lower()+'@depth20')
            pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/3_'+s+'.pklz', False)
    
    print('symbols with volume > ', min_volume, 'and less than', max_volume, '=', len(socket_list))
    
    # start order_book web socket > call back saves most recent data to disk
    conn_key = bm.start_multiplex_socket(socket_list, process_socket_pushes_order_book)
    bm.start()
    

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
    pickle_write('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz', symbols_for_save)

    symbols_saved = pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
    print('btc symbols saved:', len(symbols_saved))