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

def load_current_state(current_state_info):
    return pickle_read('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + current_state_info['length'] + '_' + current_state_info['file_number'] + '_' + current_state_info['symbol'] + '.pklz')
    

def get_readable_time(time_to_get):
    stamp = int(time_to_get)-6*60*60
    # handle millisecond time stamps (as well as seconds)
    if len(str(time_to_get)) > 10:
        stamp = int(int(time_to_get)/1000.0-6*60*60)
    return datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M:%S')

def get_time():
    return datetime.datetime.fromtimestamp(int(time.time())-6*60*60).strftime('%Y-%m-%d %H:%M:%S')


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

def round_down(num,digits):
    if float(digits) == 0:
        #print('here..', num, math.floor(num))
        return math.floor(num)
    factor = 10.0 ** digits
    return math.floor(num * factor) / factor
    
def convert_date_to_epoch(date_time):
    #print(date_time)
    pattern = '%Y-%m-%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(date_time, pattern)))
    #print(epoch)
    return epoch
    
def get_length_of_float(f):
    string_of_float = str(f)
    if string_of_float.find('e') > -1:
        return len(string_of_float)-5
    else:
        return len(string_of_float)

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

    try:
        maximum_order_to_buy = float_to_str(round_down(current_state['largest_buy_segment'], current_state['quantity_decimals']))
        maximum_possible_buy = float_to_str(round_down(current_state['original_amount_to_buy'] - current_state['executedQty'], current_state['quantity_decimals']))
        
        quantity_to_buy = min(float(maximum_order_to_buy), float(maximum_possible_buy))
        
        # DEBUGGER
        # print('qty', quantity_to_buy, 'price', price_to_buy)
    
        buy_order = current_state['client'].order_limit_buy(symbol=current_state['symbol'], quantity=quantity_to_buy, price=price_to_buy)
    
        current_state['state'] = 'buying'
        current_state['orderId'] = buy_order['orderId']
        write_current_state(current_state, current_state)
    
        return current_state
    except Exception as e:
        return current_state
    

def create_sale_order(current_state, price_to_sell, market=False):
    #print('in create sale order', price_to_sell)

    if not 'largest_bitcoin_order' in current_state:
        print(current_state['symbol'], 'largest_bitcoin_order NOT defined', get_time())
        # EXCEPTION IN (/home/nelsonriley/Development/utility.py, LINE 294 "sold_coin, current_state = sell_with_order_book(current_state, current_state['price_to_sell_3'], current_state['minutes_until_sale_3'])"): 'largest_bitcoin_order'
        current_state['largest_bitcoin_order'] = .1

    max_quantity = float_to_str(round_down(current_state['largest_bitcoin_order']/float(price_to_sell),current_state['quantity_decimals']))
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

   
    if 'sell_now' in current_state:
        recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['look_back'], current_state['a_b'], current_state['price_to_buy_factor'], current_state['price_to_sell_factor'], current_state['original_buy_time'], get_time(), current_state['std_dev_increase_factor'], current_state['length_indicator_trades'], 1]
    else:
        recorded_trade = [current_state['original_buy_time_readable'], current_state['symbol'], profit_from_trade, percent_profit_from_trade, invested_btc, current_state['look_back'], current_state['a_b'], current_state['price_to_buy_factor'], current_state['price_to_sell_factor'], current_state['original_buy_time'], get_time(), current_state['std_dev_increase_factor'], current_state['length_indicator_trades'], 0]
    
        
    pickle_write('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/'+ current_state['length'] + '_' + current_state['file_number'] + '_' + str(current_state['original_buy_time']) + '_binance_all_trades_history.pklz', recorded_trade)

    # update program state
    write_current_state(current_state, False)
    
    if percent_profit_from_trade < -.01 and percent_profit_from_trade != -1.0:
        print('**** more than 1% drop, blocking coin for 24 hrs', current_state['symbol'],get_time())
        stop_trading_until = int(time.time()) + 60*60*24
        pickle_write('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_2_' + current_state['symbol'], stop_trading_until)
    
    print('################## wrote profit and freed coin....', current_state['symbol'])

    # ignore trades we have big losses on for 12 hours
    # if profit_from_trade < -.01:
    #     current_state['state'] = 'sleeping'
    #     write_current_state(current_state, current_state)
    #     time.sleep(60*60*1)

def get_order_book_local(symbol, length):
    while True:
        order_book = pickle_read('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+ symbol +'.pklz')
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

def sell_off_and_block_coin(symbol, client):
    print('selling off and blocking coin for 24 hrs..', symbol['symbol'], get_time())
    time_to_start_trading_2 = int(time.time()) + 24*60*60
    pickle_write('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_2_' + symbol['symbol'], time_to_start_trading_2)
    
    if symbol['symbol'] != 'BNBBTC':
        
        all_lengths = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']
        for each_length in all_lengths:
            pickle_write('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + each_length + '_0_' + symbol['symbol'] + '.pklz', False)
        
        acct_info = client.get_account()

        for balance in acct_info['balances']:
            
            if balance['asset']+'BTC' == symbol['symbol']:
                try:
                    if float(balance['free']) > 0:
                        print('sell', balance['asset'])
                        min_quantity = max(float(symbol['filters'][1]['minQty']), float(symbol['filters'][2]['minNotional']))
                        if float(balance['free']) > float(min_quantity):
                            quantity_decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                            if float(quantity_decimals) == 0:
                                quantity_for_sale = str(math.floor(float(balance['free'])))
                            else:
                                rounded_down_quantity = round_down(float(balance['free']),quantity_decimals)
                                print('rounded_down_quantity', rounded_down_quantity)
                                quantity_for_sale = float_to_str(rounded_down_quantity,get_length_of_float(rounded_down_quantity))
                            print('quantity_for_sale', quantity_for_sale)
                            sale_order = client.order_market_sell(symbol=symbol['symbol'], quantity=quantity_for_sale)
                            pprint(sale_order)
                except Exception as e:
                    print('selling off all of this coin failed, error below', symbol['symbol'])
                    print(e)
    

def sell_coin_with_order_book_use_min(current_state):
    print('########### - Selling...', current_state['symbol'], 'at minimum price',  current_state['price_to_sell'], 'original_buy_time_readable', current_state['original_buy_time_readable'], 'original investment', current_state['original_quantity']*current_state['original_price'], 'original price', current_state['original_price'], 'exectuedQty', current_state['executedQty'], 'look_back', current_state['look_back'], 'price to buy factor', current_state['price_to_buy_factor'], 'price_to_sell_factor', current_state['price_to_sell_factor'])
    
    try:

        if current_state['executedQty'] >= current_state['min_quantity']:
    
            keep_price = False
            started_second_round = False
            started_give_up = False
            started_give_up_2 = False
            sell_now = False
            try:
                minutes_since_start = int(round((int(time.time()) - current_state['finish_buy_time'])/60))
            except Exception as e:
                minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))-2
                
            minutes_until_change = current_state['minutes_until_sale'] - minutes_since_start
            minutes_to_run = current_state['minutes_until_sale_final'] - minutes_since_start
        
            time_to_change = int(time.time()) + minutes_until_change * 60
            time_to_give_up = int(time.time()) + minutes_to_run * 60
            time_to_give_up_2 = int(time.time()) + minutes_to_run * 60 + minutes_to_run * 60
            
            if int(time.time()) >= time_to_give_up:
                started_give_up = True
                print('Started give up 1, reduced price increase factor by half', current_state['symbol'], 'price_increase_factor', current_state['price_increase_factor'])
                    
            if int(time.time()) >= time_to_give_up_2:
                started_give_up_2 = True
                print('Started give up 2, reduced price increase factor by half again', current_state['symbol'], 'price_increase_factor', current_state['price_increase_factor'])
            
            while True:
                
                for times_to_try_to_load in range(0, 60):
                    new_current_state = load_current_state(current_state)
                    if new_current_state != False:
                        current_state = new_current_state
                        break
                
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
                        
                if int(time.time()) >= time_to_give_up_2:
                    if started_give_up_2 == False:
                        started_give_up_2 = True
                        current_state['price_increase_factor'] = (float(current_state['price_increase_factor'])-1)/2+1
                        print('Started give up 2, reduced price increase factor by half again', current_state['symbol'], 'price_increase_factor', current_state['price_increase_factor'])
                        write_current_state(current_state, current_state)
                        
                first_in_line_price, first_ask, second_in_line_price, second_ask, second_price_to_check, first_bid = get_first_in_line_price(current_state)
                
                # if float(first_in_line_price) < .985*float(current_state['original_price']):
                #     if sell_now == False:
                #         sell_now = True
                #         print('******* price dropped 1% selling now..', current_state['symbol'], get_time())
                #         current_state['sell_now'] = 1
                #         write_current_state(current_state, current_state)
                
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
        
                if float(first_in_line_price) >= price_to_sell_min or ('sell_now' in current_state and current_state['sell_now'] == 1):
                    if started_second_round == True:
                        keep_price = True
                    if current_state['orderId'] != False:
                        sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                        if first_ask != float(sale_order_info['price']):
                            #print(current_state['symbol'], 'cancel sale order, price is in range, but we are not the first bid, so cancel and make us first bid. first_in_line_price', first_in_line_price, 'price_to_sell_min', price_to_sell_min, 'first_ask', first_ask, 'sale_order_info[price]', sale_order_info['price'])
                            current_state = cancel_sale_order(current_state)
                            if current_state['executedQty'] < current_state['min_quantity']:
                                break
                            current_state = create_sale_order(current_state, first_in_line_price)
                        else:
                            if second_price_to_check < second_ask:
                                #print(current_state['symbol'], 'cancel sale order, price is in range, we are first bid, but the next price is far back, so cancel and move us back. first_in_line_price', first_in_line_price, 'price_to_sell_min', price_to_sell_min, 'first_ask', first_ask, 'second_ask', second_ask, 'second_price_to_check', second_price_to_check, 'sale_order_info[price]', sale_order_info['price'])
                                current_state = cancel_sale_order(current_state)
                                if current_state['executedQty'] < current_state['min_quantity']:
                                    break
                                current_state = create_sale_order(current_state, second_in_line_price)
        
                    else:
                        #print(current_state['symbol'], 'price that would make us first is in range, but no sale order so create one', 'first_in_line_price', first_in_line_price, 'price_to_sell_min', price_to_sell_min)
                        current_state = create_sale_order(current_state, first_in_line_price)
                else:
                    if current_state['orderId'] != False:
                        #print(current_state['symbol'], 'cancel sale order, price that would make us first is out of range', 'first_in_line_price', first_in_line_price, 'price_to_sell_min', price_to_sell_min)
                        current_state = cancel_sale_order(current_state)
                        if current_state['executedQty'] < current_state['min_quantity']:
                                break
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
        if error_as_string.find('Filter failure: LOT_SIZE') >= 0:
            print('error selling, LOT_SIZE error, so probably coin has sold mostly, so calculating profit and freeing coin')
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

def get_indicator_trade_lengths(indicator_trades, overall_keep_length, minutes):
    
    indicator_trades_lengths = [0] * (overall_keep_length+1)
    for keep_length in range(1, overall_keep_length+1):
        for indicator_trade in indicator_trades:
            if int(time.time()) - indicator_trade[1] < keep_length*minutes*60:
                 indicator_trades_lengths[keep_length] += 1
                 
    return indicator_trades_lengths
    
    

def buy_coin(symbol, length, file_number, client, indicator_bot):
    
    # if symbol['symbol'] == 'KNCBTC':
    #     print('here')

    try:
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz','rb')
        current_state = pickle.load(f)
        f.close()
    except Exception as e:
        current_state = False

    if isinstance(current_state,dict) and indicator_bot == 0:
        print('loading state to sell coin..', current_state['symbol'])
        buy_coin_from_state(current_state)
        return

    try:
        
        if indicator_bot == 0:
            
            stop_trading_until_length = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_until_'+length)
            
            if stop_trading_until_length != False and int(time.time()) < stop_trading_until_length:
                if symbol['symbol'] == 'ETHBTC' and length == '1d':
                    print('not trading anything...')
                    time.sleep(20*60)
                time.sleep(10*60)
                return
            
            
            
            stop_trading_until = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_until')
            
            if stop_trading_until != False and int(time.time()) < stop_trading_until:
                #pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor', 0)
                if symbol['symbol'] == 'ETHBTC' and length == '1d':
                    print('not trading anything...')
                time.sleep(10*60)
                return
            
            time_to_start_trading = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_' + symbol['symbol'])
            
            if time_to_start_trading != False and int(time.time()) < time_to_start_trading:
                if symbol['symbol'] == 'ETHBTC':
                     print('not trading coin...')
                time.sleep(60)
                return
    
            time_to_start_trading_2 = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_2_' + symbol['symbol'])
            
            if time_to_start_trading_2 != False and int(time.time()) < time_to_start_trading_2:
                time.sleep(60)
                return
        ##
        
        if symbol['symbol'] == 'CTRBTC':
            time.sleep(6000000)
            return
        
        a_b = random.randint(0,1)


        largest_bitcoin_order = .1
        look_back_schedule = [1,5,9,15]
        max_std_increase = 1
        overall_keep_length = 2
        indicator_trade_check_length = 1
        if length == '1m':
            minutes = 1
            overall_keep_length = 15
            max_price_to_buy_factor = .98
            largest_bitcoin_order = .1
            max_trades_allowed = 30
            max_std_increase = 1
            indicator_trade_check_length = 4
            part_of_bitcoin_to_use = .4*2
            gain_min = .001
            buy_price_increase_factor = 1.001
            minutes_until_sale = 10
            minutes_until_sale_final = 12
        elif length == '5m':
            minutes = 5
            overall_keep_length = 6
            max_price_to_buy_factor = .965
            largest_bitcoin_order = .2
            max_trades_allowed = 7
            max_std_increase = 1
            indicator_trade_check_length = 2
            part_of_bitcoin_to_use = .45*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 12*minutes
            minutes_until_sale_final = 14*minutes
        elif length == '15m':
            minutes = 15
            max_trades_allowed = 10
            max_std_increase = 1
            indicator_trade_check_length = 2
            max_price_to_buy_factor = .965
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .5*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 12*minutes
            minutes_until_sale_final = 14*minutes
        elif length == '30m':
            minutes = 30
            max_trades_allowed = 9
            max_std_increase = 1
            indicator_trade_check_length = 2
            max_price_to_buy_factor = .955
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .55*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 12*minutes
            minutes_until_sale_final = 14*minutes
        elif length == '1h':
            minutes = 60
            max_trades_allowed = 8
            max_std_increase = 1
            indicator_trade_check_length = 2
            max_price_to_buy_factor = .95
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .6*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 12*minutes
            minutes_until_sale_final = 14*minutes
        elif length == '2h':
            minutes = 2*60
            max_trades_allowed = 5
            max_std_increase = 1
            indicator_trade_check_length = 2
            max_price_to_buy_factor = .94
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .65*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 8*minutes
            minutes_until_sale_final = 10*minutes
        elif length == '6h':
            minutes = 6*60
            max_trades_allowed = 1
            max_price_to_buy_factor = .92
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .7*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 4*minutes
            minutes_until_sale_final = 6*minutes
        elif length == '12h':
            minutes = 12*60
            max_trades_allowed = 1
            max_price_to_buy_factor = .91
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .75*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 3*minutes
            minutes_until_sale_final = 5*minutes
        elif length == '1d':
            minutes = 24*60
            max_trades_allowed = 1
            max_price_to_buy_factor = .9
            largest_bitcoin_order = .2
            part_of_bitcoin_to_use = .8*2
            gain_min = .001
            buy_price_increase_factor = 1.002
            minutes_until_sale = 2*minutes
            minutes_until_sale_final = 4*minutes
           
        stop_trading_value = -.023
        stop_trading_time = 6 # hrs 
        price_to_start_buy_factor = 1.003
        sell_price_drop_factor = .997
        

        price_to_buy_factor_array = {}
        price_to_sell_factor_array = {}
        lower_band_buy_factor_array = {}
        price_increase_factor_array = {}
        
        
        datapoints_trailing = look_back_schedule[-1] + 20
        
        std_dev_increase_factor = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor_' + length)
        
        if indicator_bot == 1:
            std_dev_increase_factor = 1

        for look_back in look_back_schedule:
            
            # NOTE, don't A/B test indicator_bot
            look_back_optimized = pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/1_' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '.pklz')
            
            if look_back_optimized != False:
                
                price_to_buy_factor = look_back_optimized['lowest_buy_factor'] + std_dev_increase_factor * look_back_optimized['lowest_buy_factor_std_dev']
                price_to_sell_factor = min(look_back_optimized['highest_sale_factor'], .99)
                
                if indicator_bot != 1: 
                    if price_to_sell_factor - price_to_buy_factor < .007:
                        price_to_buy_factor = price_to_sell_factor - .007
                        
                    if price_to_buy_factor > max_price_to_buy_factor:
                        price_to_buy_factor = max_price_to_buy_factor
                    
            
                price_to_buy_factor_array[look_back] = price_to_buy_factor
                price_to_sell_factor_array[look_back] = price_to_sell_factor
                lower_band_buy_factor_array[look_back] = 100
                price_increase_factor_array[look_back] = 1.01
                
            else:
                #print('No trading parameters for', symbol['symbol'], 'look_back', look_back)
                time.sleep(60*1)
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

            if length == '1m':
                time.sleep(2)
            elif length == '5m':
                time.sleep(6)
            elif length == '15m':
                time.sleep(12)
            elif length == '30m':
                time.sleep(18)
            elif length == '1h':
                time.sleep(26)
            elif length == '2h':
                time.sleep(36)
            elif length == '6h':
                time.sleep(56)
            elif length == '12h':
                time.sleep(76)
            elif length == '1d':
                time.sleep(96)
            
                
            current_price = float(order_book['bids'][0][0])
            

            for look_back in look_back_schedule:
                
                if indicator_bot == 0 and price_to_buy_factor_array[look_back] > max_price_to_buy_factor:
                    continue
            
                price_to_start_buy = float(data[index-look_back][4])*price_to_buy_factor_array[look_back]*price_to_start_buy_factor


                if current_price <= price_to_start_buy:
                    
                    # reset std_dev_increase_factor based on number of recent trades by "indicator bot"
                    # instead of resetting std_dev_increase_factor with every new trade
                    if indicator_bot == 1:
                        indicator_trades_path = '/home/ec2-user/environment/botfarming/Development/variables/indicator_trades_' + length
                        indicator_trades_old = pickle_read(indicator_trades_path)
                        indicator_trades_new = []
                        
                        trade_keep_length = minutes*overall_keep_length*60
                    
                        for old_trade in indicator_trades_old:
                            if int(time.time()) - old_trade[1] < trade_keep_length and old_trade[0] != symbol['symbol']:
                                indicator_trades_new.append(old_trade)
                              
                          
                        indicator_trades_new.append([symbol['symbol'],int(time.time())])
                        # if len(indicator_trades_new) > 6:
                        #     pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor', 0)
                        pickle_write(indicator_trades_path, indicator_trades_new)
                        
                        indicator_trades_lengths = get_indicator_trade_lengths(indicator_trades_new, overall_keep_length, minutes)
                        
                        new_std_dev_increase_factor = max(0,round((float(max_trades_allowed)-float(indicator_trades_lengths[indicator_trade_check_length]))*max_std_increase/float(max_trades_allowed),2))
                        new_std_dev_increase_factor = new_std_dev_increase_factor -.5
        
                        pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor_'+length, new_std_dev_increase_factor)
                        
                        print('new trade', symbol['symbol'], 'length indicator', indicator_trades_lengths[indicator_trade_check_length], 'std_increase_factor',new_std_dev_increase_factor,  get_time())
                        
                        time.sleep(minutes*60)
                        return
                    
                    
                    indicator_trades = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/indicator_trades_'+length)
                    
                    
                    
                    indicator_trades_lengths = get_indicator_trade_lengths(indicator_trades, overall_keep_length, minutes)
                    
                    
                    print('----start buy', symbol['symbol'], 'std_dev_increase_factor', std_dev_increase_factor, 'len(indicator_trades)', indicator_trades_lengths[indicator_trade_check_length], get_time())
                    
                    
                    ## block symbols for 24 hrs if 2 trades trigger within 4 minutes (only 1st trade executes)
                    last_trade_start = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/last_trade_start_' + symbol['symbol'])
                    if last_trade_start != False and int(time.time()) - last_trade_start < 190:
                        print('too many trades on ', symbol['symbol'], 'selling all coins blocking for 24 hr', get_time())
                        time_to_start_trading_2 = int(time.time()) + 24*60*60
                        pickle_write('/home/ec2-user/environment/botfarming/Development/variables/stop_trading_2_' + symbol['symbol'], time_to_start_trading_2)
                        # all_lengths = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']
                        # for each_length in all_lengths:
                            
                        #     others_current_state = pickle_read('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + each_length + '_0_' + symbol['symbol'] + '.pklz')
                        #     if others_current_state != False:
                        #         others_current_state['sell_now'] = 1
                        #         pickle_write('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + each_length + '_0_' + symbol['symbol'] + '.pklz', others_current_state)
        
                        return
                    
                    
                    if indicator_trades_lengths[indicator_trade_check_length] > max_trades_allowed:
                        time.sleep(120)
                        return
                    

                    lower_band_buy_factor = lower_band_buy_factor_array[look_back]
                    price_to_buy_factor = price_to_buy_factor_array[look_back]
                    price_to_sell_factor = price_to_sell_factor_array[look_back]
                    price_increase_factor = price_increase_factor_array[look_back]


                    price_to_buy = float(data[index-look_back][4])*price_to_buy_factor
                        
                    price_to_sell = float(data[index-look_back][4])*(price_to_sell_factor - (price_to_sell_factor - price_to_buy_factor)*.15)
                    

                    print('-------------------buy!', symbol['symbol'], 'current price', current_price, 'current price time', get_readable_time(order_book['time']), 'look_back', look_back, 'look back original price', data[index-look_back][4], 'look back original time', get_readable_time(data[index-look_back][0]),   'price_to_buy', price_to_buy , 'price_to_buy_factor', price_to_buy_factor_array[look_back], 'price_to_sell', price_to_sell,  'price_to_sell_factor',price_to_sell_factor_array[look_back] , 'price_increase_factor',price_increase_factor_array[look_back] , minutes_until_sale, get_time())
                    
                    
                    amount_to_buy = part_of_bitcoin_to_use/price_to_buy
                    largest_buy_segment = largest_bitcoin_order/price_to_buy

                    price_decimals = get_min_decimals(symbol['filters'][0]['minPrice'])

                    quantity_decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                    # quantity_decimals = get_min_decimals_new(symbol['filters'][2]['minNotional'])

                    current_state = {}
                    current_state['state'] = 'buying'
                    current_state['look_back'] = look_back
                    current_state['a_b'] = a_b
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
                    current_state['min_quantity'] = max(float(symbol['filters'][1]['minQty']), float(symbol['filters'][2]['minNotional']))
                    current_state['stop_trading_value'] = stop_trading_value
                    current_state['stop_trading_time'] = stop_trading_time
                    current_state['std_dev_increase_factor'] = std_dev_increase_factor
                    current_state['length_indicator_trades'] = indicator_trades_lengths
                    current_state['symbol_info'] = symbol

                    write_current_state(current_state, current_state)

                    if length == '1m':
                        time_to_give_up = int(time.time()) + 120
                    elif length == '5m':
                        time_to_give_up = int(time.time()) + 240
                    elif length == '15m':
                        time_to_give_up = int(time.time()) + 360
                    elif length == '30m':
                        time_to_give_up = int(time.time()) + 480
                    elif length == '1h':
                        time_to_give_up = int(time.time()) + 720
                    elif length == '2h':
                        time_to_give_up = int(time.time()) + 1080
                    elif length == '6h':
                        time_to_give_up = int(time.time()) + 30*60
                    elif length == '12h':
                        time_to_give_up = int(time.time()) + 45*60
                    elif length == '1d':
                        time_to_give_up = int(time.time()) + 60*60
                    
                    
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
                        if float(first_in_line_price) <= price_to_buy_max:
                            if current_state['orderId'] != False:
                                buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                                if first_bid != float(buy_order_info['price']):
                                    #print(current_state['symbol'], 'cancel buy order, price is in range, but we are not the first bid, so cancel and make us first bid. first_in_line_price', first_in_line_price, 'price_to_buy_max', price_to_buy_max, 'first_bid', first_bid)
                                    current_state = cancel_buy_order(current_state)
                                    if current_state['executedQty'] >= amount_to_stop_buying:
                                        break
                                    current_state = create_buy_order(current_state, first_in_line_price)
                                    if current_state['orderId'] == False:
                                        break
                                else:
                                    if second_price_to_check > second_bid:
                                        #print(current_state['symbol'], 'cancel buy order, price is in range, we are the first but, but the second bid is pretty far back, so cancel and move our bid back. first_in_line_price', first_in_line_price, 'price_to_buy_max', price_to_buy_max, 'first_bid', first_bid, 'second_bid', second_bid, 'second_price_to_check', second_price_to_check)
                                        current_state = cancel_buy_order(current_state)
                                        if current_state['executedQty'] >= amount_to_stop_buying:
                                            break
                                        current_state = create_buy_order(current_state, second_in_line_price)
                                        if current_state['orderId'] == False:
                                            break

                            else:
                                #print(current_state['symbol'], 'price is in range and no order, so creating one.. first_in_line_price ',  first_in_line_price, 'price_to_buy_max', price_to_buy_max)
                                current_state = create_buy_order(current_state, first_in_line_price)
                                if current_state['orderId'] == False:
                                        break
                        else:
                            if current_state['orderId'] != False:
                                #print(current_state['symbol'], 'cancel buy order because price that would make us first is greater than the max price we would pay, first_in_line_price', first_in_line_price, 'price_to_buy_max', price_to_buy_max)
                                current_state = cancel_buy_order(current_state)
                                if current_state['executedQty'] >= amount_to_stop_buying:
                                    break

                        if current_state['orderId'] != False:
                            time.sleep(5)
                        else:
                            time.sleep(.03)


                    if current_state['executedQty'] < current_state['min_quantity']:
                        while int(time.time()) <= time_to_give_up:
                            time.sleep(5)
                        print('[last line reached] no one bought cancel order - freeing coin', current_state['symbol'], get_time())
                        write_current_state(current_state, False)
                        return True
                        
                    
                    # std_dev_increase_factor
                    pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor', 0)
                    
                    # last_trade_start
                    pickle_write('/home/ec2-user/environment/botfarming/Development/variables/last_trade_start_' + symbol['symbol'], int(time.time()))

                    current_state['finish_buy_time'] = int(time.time())
                    current_state['finish_buy_time_readable'] = get_time()
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


def run_bot_parallel(file_number, length, total_files, client, indicator_bot=0):

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
                if indicator_bot == 0:
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
            t = Thread(target=buy_coin_thread, args=[symbol, length, file_number, client, indicator_bot])
            t.start()

        loops += 1


# "worker"
def buy_coin_thread(symbol, length, file_number, client, indicator_bot):

    while True:

        buy_coin(symbol, length, file_number, client, indicator_bot)


def append_data(file_path, data):
    data_points = pickle_read(file_path)
    data_points.append(data)
    pickle_write(file_path, data_points)

def save_data(save_params, datapoints_trailing, min_volume, minutes, symbols_to_download = False):
    
    for settings in save_params:

        day_folder = settings[0]
        start_time = arrow.get(settings[1]).replace(tzinfo='America/Denver')
        end_time = arrow.get(settings[2]).replace(tzinfo='America/Denver')

        path = '/home/ec2-user/environment/botfarming/Development/binance_training_data/'
        if not os.path.exists(path):
            os.makedirs(path)

        start_end_style = True
        if start_end_style:
            
            # print('STARTING CANDLES DOWNLOAD', settings, get_time())

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
            if symbols_to_download == False:
                symbols = pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
            else:
                symbols = symbols_to_download
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
            # print('SAVING CANDLE DATA', settings, 'for', len(coins), 'symbols', get_time())
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
                candle_path = '/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ symbol +'_data_'+str(minutes)+'m.pklz'
                pickle_write(candle_path, data)

    return True

def process_socket_pushes_order_book(msg):
    try:
        if not 'stream' in msg:
            return
        elif 'depth' in msg['stream']:
                
            symbol = msg['stream'].split('@')[0].upper()
            msg['data']['time'] = int(time.time())
            pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+symbol+'.pklz', msg['data'])
    
            if (symbol == 'ETHBTC' or symbol == 'ZECBTC') and (time.localtime().tm_sec == 1 or time.localtime().tm_sec == 2):
                print('process_socket_pushes_order_book()', symbol, msg['data']['bids'][0][0], 'time given', get_readable_time(msg['data']['time']), 'current time', get_time())
    
            # if time.localtime().tm_sec < 30:
            #     should_save = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/should_save_' + symbol)
            #     if should_save != False and should_save > int(time.time()):
            #         already_saved = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/already_saved_' + symbol)
            #         if already_saved == False:
            #             try:
            #                 order_book_history = pickle_read('/home/ec2-user/environment/botfarming/Development/order_book_history/' + symbol + '_' + str(should_save))
            #                 order_book_history.append(msg['data'])
            #                 pickle_write('/home/ec2-user/environment/botfarming/Development/order_book_history/' + symbol + '_' + str(should_save), order_book_history)
            #                 pickle_write('/home/ec2-user/environment/botfarming/Development/variables/already_saved_' + symbol, True)
            #             except Exception as e:
            #                 print(e)
            # elif time.localtime().tm_sec > 30:
            #     should_save = pickle_read('/home/ec2-user/environment/botfarming/Development/variables/should_save_' + symbol)
            #     if should_save != False and should_save > int(time.time()):
            #         pickle_write('/home/ec2-user/environment/botfarming/Development/variables/already_saved_' + symbol, False)
    except Exception as e:
        print(e)        

    
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
    
    extra_coins_to_add = {}
    if min_volume == 300:
        for s in symbols:
            symbol = symbols[s]
            lengths = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']
            for length in lengths:
                try:
                    f = gzip.open('/home/ec2-user/environment/botfarming/Development/program_state/program_state_' + length + '_0_' + symbol['symbol'] + '.pklz','rb')
                    current_state = pickle.load(f)
                    f.close()
                except Exception as e:
                    current_state = False
            
                if isinstance(current_state,dict):
                    extra_coins_to_add[current_state['symbol']] = 1
    
   
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
            pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+s+'.pklz', False)
        elif min_volume == 300 and symbol['symbol'] in extra_coins_to_add and float(symbol['24hourVolume']) < min_volume:
            print('adding extra coins', symbol['symbol'])
            total_btc_coins += 1
            symbols_trimmed[s] = symbol
            socket_list.append(s.lower()+'@depth20')
            pickle_write('/home/ec2-user/environment/botfarming/Development/recent_order_books/'+s+'.pklz', False)
        
    
    
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