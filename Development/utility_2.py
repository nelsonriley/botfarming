#!/usr/bin/python2.7
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
import arrow
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
import utility as ut

################################################################################ 24hr 1min Drop Strategy

btc_usd_price = 10500

def get_current_price_from_ticker(s):
    ticker_path = '/home/ec2-user/environment/botfarming/Development/recent_tickers/'+s+'.pklz'
    ticker = ut.pickle_read_test(ticker_path)
    if ticker == False:
        return False
    # current_price = float(ticker['c'])
    current_price = float(ticker)
    return current_price

def run_24hr_1min_drop_strategy(bot_index=-1, total_bots=-1):
    min_volume_btc = 0
    symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
    symbols_filtered, symbol_list = get_trimmed_symbols(symbols, min_volume_btc)
    
    print('starting 24hr_1min_drop_strategy @', ut.get_time(), 'trading on', len(symbol_list), 'symbols')

    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    # support running multiple bots
    if bot_index > -1:
        list_of_symbol_lists = divide_list_into_n_parts(symbol_list, total_bots)
        symbol_list = list_of_symbol_lists[bot_index]

    # 1 thread per symbol
    for s in symbol_list:
        symbol = symbols_filtered[s]
        t = Thread(target=start_24hr_1min_drop_thread, args=[symbol, client])
        t.start()

def start_24hr_1min_drop_thread(symbol, client):
    while True:
        interval = '1m'
        file_number = 2000
        monitor_and_buy_for_24hr_1min_drop(symbol, interval, file_number, client)
        time.sleep(0.3)

def monitor_and_buy_for_24hr_1min_drop(symbol, interval, file_number, client):
    s = str(symbol['symbol'])

    current_state = ut.load_current_state(s, file_number, interval)
    version = '24hr_1min_drop_v0'
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + interval + '/program_state_' + interval + '_' + str(file_number) + '_' + s + '_V' + version + '.pklz'
    # current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + interval + '/program_state_' + interval + '_' + str(file_number) + '_' + s + '.pklz'

    if isinstance(current_state, dict):
        print('monitor_and_buy_for_24hr_1min_drop() loading state to sell coin..', current_state['symbol'])
        ut.buy_coin_from_state(current_state, strategy='24hr_1min_drop')
        return

    try:

        # TODO: get PARAMS from disk after auto-optimizer saves
            # best_params_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/best_params.pklz'
            # best_params = ut.pickle_read(best_params_path)
            # if best_params == False:
            #     print('ERROR no best_params found for', s)
            #     return
            # future_candles_length = best_params['future_candles_length']
            # buy_trigger_drop_percent_factor = best_params['buy_trigger_drop_percent_factor']
            # sell_trigger_gain_percent_factor = best_params['sell_trigger_gain_percent_factor']
        
        # PARAMS  777
        buy_trigger_drop_percent_factor = 0.5
        sell_trigger_gain_percent_factor = 0.2
        future_candles_length = 4 # 20180205
        btc_tradeable_volume_factor = 3 * 0.1 # multiplier of avg btc volume per minute over 24 hrs that we can buy & sell
        btc_tradeable_volume_factor = btc_tradeable_volume_factor * 0.1 # start testing at 1/10 of normal
        stop_time = datetime.datetime(2018, 2, 18, 20, 18)

        # DATA generated from previous 24 hours via cron (binance_24hr_1min_drop_daily_update.py)
        symbol_24hr_drop_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/24hr_1min_drops_by_symbol/'+s+'.pklz'
        data = ut.pickle_read(symbol_24hr_drop_path)
        if data == False:
            print('ERROR no biggest_drop_percent or best_gain_percent found for', s)
            return
        buy_trigger_drop_percent = data['biggest_drop_percent'] * buy_trigger_drop_percent_factor
        sell_trigger_gain_percent = data['best_gain_percent'] * sell_trigger_gain_percent_factor

        # get open price in first 2 secs of minute
        have_open_price = False
        while time.localtime().tm_sec < 2:
            if not have_open_price:
                open_price = get_current_price_from_ticker(s)
                open_price_time = int(time.time())
                open_price_time_readable = ut.get_time()
                have_open_price = True
            time.sleep(.2)

        if have_open_price and open_price == 0:
            print('ERROR', s, 'open_price is zero or not found', open_price)
            time.sleep(.2)
            return False

        # run for the remaing 58 seconds of the minute
        while time.localtime().tm_sec >= 2 and have_open_price:

            current_price = get_current_price_from_ticker(s)
            if current_price == False:
                break

            drop = open_price - current_price
            if drop == 0:
                drop_percent = 0
            else:
                drop_percent = drop / open_price
            
            # STILL ALIVE MSG (printing 3 or 4 per sec, good)
            # if s == 'ETHBTC' and time.localtime().tm_sec == 55:
            #     print(s, open_price, current_price, drop, drop_percent, ut.get_time())

            if drop_percent >= buy_trigger_drop_percent:

                # start buy
                price_to_buy = open_price - (buy_trigger_drop_percent * open_price)
                price_to_sell = price_to_buy + (sell_trigger_gain_percent * price_to_buy)
                time_to_sell_readable = ut.get_readable_time(int(time.time()+future_candles_length*60))

                # limit time window for testing
                epoch_stop_time = int((stop_time - datetime.datetime(1970, 1, 1)).total_seconds()) + 7 * 60 * 60
                epoch_now = int(time.time())
                if epoch_now > epoch_stop_time:
                    print('NO BUY', s, 'time window expired')
                    return False
                
                # calc buy params
                one_min_avg_volume = float(symbol['24hourVolume']) / (24*60)
                btc_qty = btc_tradeable_volume_factor * one_min_avg_volume
                base_qty = btc_qty / price_to_buy
                base_qty_min = float(symbol['filters'][1]['minQty'])
                base_qty_decimals = ut.get_min_decimals(base_qty_min)
                base_qty_for_order = ut.float_to_str(round(base_qty, base_qty_decimals))
                
                price_min = float(symbol['filters'][0]['minPrice'])
                price_decimals = ut.get_min_decimals(price_min)
                price_to_buy_for_order = ut.float_to_str(round(price_to_buy, price_decimals))
                price_to_sell_for_order = ut.float_to_str(round(price_to_sell, price_decimals))
                
                notional = float(base_qty_for_order) * float(price_to_buy_for_order)
                min_notional = float(symbol['filters'][2]['minNotional'])
                will_pass_min_notional = notional >= min_notional
                if not will_pass_min_notional:
                    print('CORRECTING VOLUME: notional too small', s, ut.float_to_str(base_qty_for_order), '*', ut.float_to_str(price_to_buy_for_order), '=', ut.float_to_str(notional), 'vs', ut.float_to_str(min_notional))
                    # print('ERROR: notional too small', s, ut.float_to_str(base_qty_for_order), '*', ut.float_to_str(price_to_buy_for_order), '=', ut.float_to_str(notional), 'vs', ut.float_to_str(min_notional))
                    # print('base_qty', base_qty)
                    # print('base_qty_min', base_qty_min)
                    # print('base_qty_decimals', base_qty_decimals)
                    # print('base_qty_for_order', base_qty_for_order)
                    base_qty = min_notional / float(price_to_buy_for_order)
                    base_qty_for_order = ut.float_to_str(round(base_qty, base_qty_decimals))
                    btc_qty = base_qty / float(price_to_buy_for_order)
                    notional = min_notional
                    return False

                # update state so we can continue where we left off if something happens
                current_state = {}
                current_state['state'] = 'buying'
                current_state['original_amount_to_buy'] = float(base_qty_for_order)
                current_state['largest_buy_segment'] = float(base_qty_for_order)
                current_state['largest_bitcoin_order'] = btc_qty
                current_state['part_of_bitcoin_to_use'] = btc_qty
                current_state['original_buy_time'] = int(time.time())
                current_state['original_buy_time_readable'] = ut.get_time()
                current_state['symbol'] = symbol['symbol']
                current_state['orderId'] = False
                current_state['executedQty'] = 0.0
                current_state['total_revenue'] = 0.0
                current_state['price_to_buy'] = price_to_buy
                current_state['price_to_sell'] = price_to_sell
                current_state['price_to_buy_for_order'] = price_to_buy_for_order
                current_state['price_to_sell_for_order'] = price_to_sell_for_order
                current_state['length'] = interval
                current_state['interval'] = interval
                current_state['file_number'] = str(file_number)
                current_state['client'] = client
                current_state['error_cancel_order'] = False
                current_state['quantity_decimals'] = base_qty_decimals
                current_state['price_decimals'] = price_decimals
                current_state['min_price'] = price_min
                current_state['min_quantity'] = base_qty_min
                current_state['minQty'] = float(symbol['filters'][1]['minQty'])
                current_state['minNotional'] = float(symbol['filters'][2]['minNotional'])
                current_state['sell_price_drop_factor'] = 1

                # strategy specific (support immediate sim vs reality feedaback)
                current_state['future_candles_length'] = future_candles_length
                current_state['open_price'] = open_price
                current_state['open_price_time'] = open_price_time
                current_state['open_price_time_readable'] = open_price_time_readable
                current_state['buy_time_triggered'] = int(time.time())
                current_state['buy_time_triggered_readable'] = ut.get_time()
                current_state['buy_trigger_drop_percent_factor'] = buy_trigger_drop_percent_factor
                current_state['sell_trigger_gain_percent_factor'] = sell_trigger_gain_percent_factor
                current_state['future_candles_length'] = future_candles_length
                current_state['buy_trigger_drop_percent'] = buy_trigger_drop_percent
                current_state['sell_trigger_gain_percent'] = sell_trigger_gain_percent
                current_state['btc_tradeable_volume_factor'] = btc_tradeable_volume_factor
                current_state['symbol_data'] = symbol
                current_state['version'] = version
                current_state['bet_size_usd'] = btc_qty * btc_usd_price
                current_state['bet_size_btc'] = btc_qty

                ut.pickle_write(current_state_path, current_state, '******could not write initial current_state******')

                # buy until the end of the minute
                time_to_give_up = int(time.time()) + ( 60 - time.localtime().tm_sec )
                price_to_buy_max = float(price_to_buy_for_order)
                amount_to_stop_buying = base_qty_for_order
                
                print('---BUY', s, '@', ut.float_to_str(price_to_buy, 8), 'sell @', ut.float_to_str(price_to_sell, 8), ut.get_time())
                print('---open', ut.float_to_str(open_price, 8), 'cur', ut.float_to_str(current_price, 8))
                print('---btc_qty', ut.float_to_str(btc_qty), 'btc_tradeable_volume_factor', btc_tradeable_volume_factor)
                print('---one_min_avg_volume', ut.float_to_str(one_min_avg_volume))
                # print('>>> BUY @', ut.float_to_str(price_to_buy, 8), s, ut.get_time())
                # print('>>> SELL @', ut.float_to_str(price_to_sell, 8), 'by', time_to_sell_readable)
                # print('>>> open', ut.float_to_str(open_price, 8))
                # print('>>> current', ut.float_to_str(current_price, 8))
                # print('>>> drop', ut.float_to_str(drop, 8))
                
                while True:

                    # if end of minute, start selling
                    if int(time.time()) >= time_to_give_up:
                        if current_state['orderId'] != False:
                            current_state = ut.cancel_buy_order(current_state)
                        break
                    
                    # place 1 limit buy order & wait
                    if current_state['orderId'] == False:
                        # must use price_to_buy_for_order
                        current_state = ut.create_buy_order_basic(current_state, price_to_buy_for_order, base_qty_for_order)
                    else:
                        buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
                        if buy_order_info['status'] == 'FILLED':
                            current_state['executedQty'] = current_state['executedQty'] + float(buy_order_info['executedQty'])
                            current_state['original_price'] = float(buy_order_info['price'])
                            current_state['state'] = 'buying'
                            current_state['orderId'] = False
                            ut.pickle_write(current_state_path, current_state, '******could not write state 2nd sell******')
                            if current_state['executedQty'] >= amount_to_stop_buying:
                                break

                    time.sleep(.2) # APIError(code=-1003): Too many requests; current limit is 1200

                # update state if no buy orders filled & start monitoring again
                if current_state['executedQty'] < current_state['min_quantity']:
                    print('NOT FILLED', s, ut.get_time())
                    ut.pickle_write(current_state_path, False, '******could not write state inside buy coin - no buy orders filled******')
                    return True

                # otherwise, sell the coin!
                current_state['original_quantity'] = current_state['executedQty']
                current_state['state'] = 'selling'
                
                # strategy specific (support immediate sim vs reality feedback)
                current_state['open_price'] = open_price
                current_state['buy_time_executed'] = int(time.time())
                current_state['buy_time_executed_readable'] = ut.get_time()
                current_state['buy_price'] = current_state['original_price']
                current_state['qty_base'] = current_state['executedQty']
                # TODO quy_btc is too high, don't know why
                current_state['qty_btc'] = current_state['buy_price'] * current_state['qty_base']
                current_state['sell_partial_fill_qty'] = -1
                
                ut.pickle_write(current_state_path, current_state, '******could not update state to selling******')
                coin_sold = sell_for_24hr_1min_drop(current_state)

                # sale complete
                if coin_sold:
                    print('SALE COMPLETE', s, ut.get_time())
                    ut.pickle_write(current_state_path, False)
                    return True
                else:
                    return False
            time.sleep(0.3)
        return False

    except Exception as e:
        print('some error - freeing coin:', symbol['symbol'])
        print(e)
        ut.print_exception()
        ut.pickle_write(current_state_path, False)
        time.sleep(60*4)
        return False


def sell_for_24hr_1min_drop(current_state):
    s = str(current_state['symbol'])
    print_current_price = True
    current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
    # current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz'

    if 'time_to_give_up' in current_state:
        time_to_give_up = current_state['time_to_give_up']
    else:
        time_to_give_up = int( time.time() + 60 * current_state['future_candles_length'] )
        current_state['time_to_give_up'] = time_to_give_up
        # print('time_to_give_up', ut.get_readable_time(time_to_give_up))
        ut.pickle_write(current_state_path, current_state)

    have_enough_to_sell = current_state['executedQty'] >= current_state['min_quantity']
    if not have_enough_to_sell:
        print('too little coin to sell, considering coin sold, exiting', current_state['symbol'], ut.get_time())
        ut.calculate_profit_and_free_coin(current_state, strategy='24hr_1min_drop')
        return True

    try:
        # continually check price & if order is filled
        while True:

            current_price = get_current_price_from_ticker(s)
            price_to_sell_for_order = ut.float_to_str(round(current_state['price_to_sell'], current_state['price_decimals']))
            
            # DELAYED PRINT
            if print_current_price:
                print('---------------START SELLING', s, 'current', ut.float_to_str(current_price, 8))
                print('---------------sell at', ut.float_to_str(current_state['price_to_sell'], 8))
                print('---------------bought at', ut.float_to_str(current_state['price_to_buy'], 8))
                print('---------------own', current_state['original_buy_time_readable'], 'to', ut.get_readable_time(time_to_give_up))
                print_current_price = False

            # XXX out of time, sell at market, if the limit sale order not yet filled cancel it first
            # out of time, sell with order book
            if int(time.time()) >= time_to_give_up:
                if current_state['orderId'] != False:
                    current_state = ut.cancel_sale_order(current_state)
                    if current_state['executedQty'] < current_state['min_quantity']:
                        break
                    else:
                        current_state['sell_partial_fill_qty'] = current_state['original_amount_to_buy'] - current_state['executedQty']
                current_state['traded_by_sell_trigger'] = False
                current_state['sell_time_triggered'] = int(time.time())
                current_state['sell_time_triggered_readable'] = ut.get_time()
                # current_state = ut.create_sale_order(current_state, 0, market=True)
                sold_coin, current_state = ut.sell_with_order_book(current_state, 0.0, minutes_until_sale=60)
                break
                
            # create 1 limit sale order & wait
            if current_price >= float(price_to_sell_for_order):
                if current_state['orderId'] == False:
                    print('SELL TRIGGERED BY PRICE', s, ut.float_to_str(current_price), '>=', ut.float_to_str(price_to_sell_for_order), ut.get_time())
                    current_state['traded_by_sell_trigger'] = True
                    current_state['sell_time_triggered'] = int(time.time())
                    current_state['sell_time_triggered_readable'] = ut.get_time()
                    current_state = ut.create_sale_order(current_state, price_to_sell_for_order)

            # update executed qty & check if filled
            if current_state['orderId'] != False:
                sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
                if sale_order_info['status'] == 'FILLED':
                    print('FILLING', s, ut.get_time(), current_state['original_quantity'], current_state['executedQty'], sale_order_info['price'], current_state['total_revenue'])
                    # print("current_state['original_quantity']", current_state['original_quantity'])
                    # print("current_state['executedQty']", current_state['executedQty'])
                    # print("sale_order_info['executedQty']", sale_order_info['executedQty'])
                    # print("sale_order_info['price']", sale_order_info['price'])
                    # print("current_state['total_revenue']", current_state['total_revenue'])
                    # pprint(sale_order_info)
                    current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
                    current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
                    current_state['state'] = 'selling'
                    current_state['orderId'] = False
                    current_state['sell_price'] = float(sale_order_info['price'])
                    ut.pickle_write(current_state_path, current_state, '******could not write state selling******')
                    if current_state['executedQty'] < current_state['min_quantity']:
                        print('FILLED', s, ut.get_time())
                        break

            time.sleep(.03)

        # sale is complete (it always completes), compare sim vs live
        current_state['sell_time_executed'] = int(time.time())
        current_state['sell_time_executed_readable'] = ut.get_time()
        current_state['profit_percent'] = (current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price'])/(current_state['original_quantity']*current_state['original_price'])
        current_state['profit_btc'] = current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price']
        get_live_vs_sim_stats(current_state)
        
        # calc profit, save trade, & delete current_state
        ut.calculate_profit_and_free_coin(current_state, strategy='24hr_1min_drop')
        return True
    except Exception as e:
        print(e)
        ut.print_exception()
        error_as_string = str(e)
        if error_as_string.find('Account has insufficient balance for requested action.') >= 0:
            print('error selling, but account has insufficient balance, so calculating profit and freeing coin')
            ut.calculate_profit_and_free_coin(current_state, strategy='24hr_1min_drop')
            return True
        if error_as_string.find('Filter failure: MIN_NOTIONAL') >= 0:
            print('error selling, MIN_NOTIONAL error, so probably coin has sold mostly, so calculating profit and freeing coin')
            ut.calculate_profit_and_free_coin(current_state, strategy='24hr_1min_drop')
            return True
        print('error selling')
        return False


def get_live_vs_sim_stats(current_state):
    s = current_state['symbol']
    # get last 20 min of candles (or so)
    epoch_now = int(time.time())
    epoch_ago = epoch_now - 60 * (current_state['future_candles_length'] + 2)
    start = epoch_ago * 1000
    stop = epoch_now * 1000
    url = 'https://api.binance.com/api/v1/klines?symbol='+ s +'&interval=1m&startTime='+str(start)+'&endTime='+str(stop)
    data = requests.get(url).json()
    
    # TODO print drop, time per candle
    gain_percent, gain_usd, trades = trade_on_drops(current_state['symbol_data'], data, current_state['future_candles_length'], current_state['buy_trigger_drop_percent'], current_state['sell_trigger_gain_percent'], current_state['btc_tradeable_volume_factor'])
    
    print('get_live_vs_sim_stats() len(trades)', len(trades), s)
    print('get_live_vs_sim_stats() url', url)
    for d in data:
        print('candle open', ut.get_readable_time(d[0]))
    
    # sim
    if len(trades) == 1:
        sim = trades[0]
        sim['profit_btc'] = sim['gain_btc']
        sim['profit_btc_readable'] = sim['gain_btc_readable']
        sim['profit_usd'] = sim['profit_btc'] * btc_usd_price
        sim['profit_usd_readable'] = ut.float_to_str(sim['profit_btc'] * btc_usd_price)
        sim['profit_percent'] = sim['gain_percent']
        sim['qty_btc'] = sim['volume_traded_btc']

        print('sim')
        pprint(sim)

    live = {}
    live['open_price'] = current_state['open_price']
    live['open_price_readable'] = ut.float_to_str(current_state['open_price'])
    live['open_price_time_readable'] = current_state['open_price_time_readable']
    live['buy_time_triggered'] = current_state['buy_time_triggered']
    live['buy_time_triggered_readable'] = current_state['buy_time_triggered_readable']
    live['buy_time_executed'] = current_state['buy_time_executed']
    live['buy_time_executed_readable'] = current_state['buy_time_executed_readable']
    live['buy_price'] = current_state['buy_price']
    live['buy_price_readable'] = ut.float_to_str(current_state['buy_price'])
    live['sell_time_triggered'] = current_state['sell_time_triggered']
    live['sell_partial_fill_qty'] = current_state['sell_partial_fill_qty']
    live['sell_time_executed'] = current_state['sell_time_executed']
    live['sell_time_executed_readable'] = ut.get_readable_time(current_state['sell_time_executed'])
    live['sell_price'] = current_state['sell_price']
    live['sell_price_readable'] = ut.float_to_str(current_state['sell_price'])
    live['qty_btc'] = current_state['qty_btc']
    live['profit_btc'] = current_state['profit_btc']
    live['profit_btc_readable'] = ut.float_to_str(current_state['profit_btc'])
    live['profit_usd'] = current_state['profit_btc'] * btc_usd_price
    live['profit_usd_readable'] = ut.float_to_str(current_state['profit_btc'] * btc_usd_price)
    live['profit_percent'] = current_state['profit_percent']
    live['profit_percent_readable'] = ut.float_to_str(live['profit_percent'])
    live['traded_by_sell_trigger'] = current_state['traded_by_sell_trigger']
    live['bet_size_usd'] = current_state['bet_size_usd']
    live['bet_size_usd_readable'] = ut.float_to_str(current_state['bet_size_usd'])
    
    print('live')
    pprint(live)
    
    if len(trades) != 1:
        print('>>>ERROR:', s, 'no trade or too many trades made in back test', len(trades))
        print('sim')
        print('buy_trigger_drop_percent', ut.float_to_str(current_state['buy_trigger_drop_percent']))
        do_print_each_candle = True
        gain_percent, gain_usd, trades = trade_on_drops(current_state['symbol_data'], data, current_state['future_candles_length'], current_state['buy_trigger_drop_percent'], current_state['sell_trigger_gain_percent'], current_state['btc_tradeable_volume_factor'], do_print_each_candle)
        if len(trades) > 1:
            print('sim MULTIPLE TRADES')
            for t in trades:
                pprint(t)
        return
    
    # live vs sim: computable data
    stats = {}
    stats['live_open_price_diff'] = live['open_price'] - sim['open_price']
    stats['live_open_price_diff_readable'] = ut.float_to_str(stats['live_open_price_diff'])
    stats['live_open_price_diff_percent'] = round(stats['live_open_price_diff']/sim['open_price'], 10)
    stats['live_open_price_diff_percent_readable'] = ut.float_to_str(stats['live_open_price_diff_percent'])
    stats['live_buy_time_triggered_delay'] = live['buy_time_triggered'] - sim['buy_time']
    stats['live_buy_time_executed_delay'] = live['buy_time_executed'] - sim['buy_time']
    stats['live_buy_execution_delay'] = live['buy_time_executed'] - live['buy_time_triggered']
    stats['live_buy_price_diff'] = live['buy_price'] - sim['buy_price']
    stats['live_buy_price_diff_readable'] = ut.float_to_str(stats['live_buy_price_diff'])
    stats['live_buy_price_diff_percent'] = round(stats['live_buy_price_diff'] / sim['buy_price'], 10)
    stats['live_buy_price_diff_percent_readable'] = ut.float_to_str(stats['live_buy_price_diff_percent'])
    stats['live_sell_time_triggered_delay'] = live['sell_time_triggered'] - sim['sell_time']
    stats['live_sell_time_executed_delay'] = live['sell_time_executed'] - sim['sell_time']
    stats['live_sell_execution_delay'] = live['sell_time_executed'] - live['sell_time_triggered']
    stats['live_sell_price_diff'] = live['sell_price'] - sim['sell_price']
    stats['live_sell_price_diff_readable'] = ut.float_to_str(stats['live_sell_price_diff'])
    stats['live_sell_price_diff_percent'] = round(stats['live_sell_price_diff'] / sim['sell_price'], 10)
    stats['live_sell_price_diff_percent_readable'] = ut.float_to_str(stats['live_sell_price_diff_percent'])
    stats['live_profit_btc_diff'] = live['profit_btc'] - sim['profit_btc']
    stats['live_profit_btc_diff_readable'] = ut.float_to_str(stats['live_profit_btc_diff'])
    stats['live_profit_percent_diff'] = live['profit_percent'] - sim['profit_percent']
    stats['live_profit_percent_diff_readable'] = ut.float_to_str(stats['live_profit_percent_diff'])
    stats['live_qty_btc_diff'] = live['qty_btc'] - sim['qty_btc']
    stats['live_qty_btc_diff_readable'] = ut.float_to_str(stats['live_qty_btc_diff'])
    stats['live_qty_btc_diff_percent'] = round(stats['live_qty_btc_diff'] / sim['qty_btc'], 10)
    stats['traded_by_sell_trigger_match'] = live['traded_by_sell_trigger'] == sim['traded_by_sell_trigger']
    stats['traded_by_sell_trigger_compare'] = str(live['traded_by_sell_trigger']) + '_' + str(sim['traded_by_sell_trigger'])
    if float(live['sell_partial_fill_qty']) > -1:
        stats['traded_by_sell_trigger_partial_fill_percent'] = round(live['sell_partial_fill_qty'] / current_state['original_amount_to_buy'], 10)
    else:
        stats['traded_by_sell_trigger_partial_fill_percent'] = 0
    
    # print('##############################################', s, 'LIVE vs SIM, STATS')
    # pprint(live)
    # pprint(sim)

    print('stats')
    pprint(stats)
    
    # TODO save to disk


def trade_on_drops(symbol, data, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor, do_print_each_candle=False, btc_usd_price=btc_usd_price):
    s = symbol['symbol']
    one_min_avg_volume = float(symbol['24hourVolume']) / (24*60)
    btc_tradeable_volume =  btc_tradeable_volume_factor * one_min_avg_volume
    trades = []
    sell_time = 0
    for i, c in enumerate(data):
        c = get_candle_as_dict(c)

        drop = c['open_price'] - c['low_price']
        if drop == 0:
            drop_percent = 0
        else:
            drop_percent = drop / c['open_price']
        
        if do_print_each_candle:
            print('--------c:', c['open_time_readable'])
            print('open_price', ut.float_to_str(c['open_price']))
            print('low_price', ut.float_to_str(c['low_price']))
            print('drop', ut.float_to_str(drop))
            print('drop_percent', ut.float_to_str(drop_percent))
            if drop_percent >= buy_trigger_drop_percent:
                print('DO BUY')
            print('i', i, 'of', len(data)-1)

        # do not allow overlapping trades (for now)
        no_overlap = c['open_time'] > sell_time
        if drop_percent >= buy_trigger_drop_percent and no_overlap:
            buy_price = (c['open_price'] - buy_trigger_drop_percent * c['open_price']) # * 1.002
            future_candles = get_future_candles(future_candles_length, data, i)
            if future_candles:
                if do_print_each_candle:
                    print('len(future_candles)', len(future_candles))
                traded_by_sell_trigger = False
                for f, f_c in enumerate(future_candles):
                    minute = f + 1
                    sell_trigger_price = (buy_price + sell_trigger_gain_percent * buy_price)
                    if f_c['high_price'] > sell_trigger_price:
                        sell_price = sell_trigger_price # * 0.997
                        sell_time = int(float(f_c['open_time']) / 1000)
                        sell_time_readable = f_c['open_time_readable']
                        traded_by_sell_trigger = True
                        break
                if not traded_by_sell_trigger:
                    sell_price = future_candles[-1]['close_price']
                    sell_time = future_candles[-1]['close_time']
                    sell_time_readable = future_candles[-1]['close_time_readable']
                gain = sell_price - buy_price
                gain_percent = gain / buy_price
                gain_btc = btc_tradeable_volume * gain_percent
                gain_btc_readable = ut.float_to_str(gain_btc)
                gain_usd = gain_btc * btc_usd_price
            
                trade = {
                    'gain_percent': gain_percent,
                    'gain_btc': gain_btc,
                    'gain_btc_readable': gain_btc_readable,
                    'gain_usd': gain_usd,
                    'volume_traded_btc': btc_tradeable_volume,
                    'minute': minute,
                    'open_price': c['open_price'],
                    'buy_time_readable': c['open_time_readable'],
                    'buy_time': c['open_time'],
                    'buy_price': buy_price,
                    'sell_time_readable': sell_time_readable,
                    'sell_time': sell_time,
                    'sell_price': sell_price,
                    'traded_by_sell_trigger': traded_by_sell_trigger,
                }
                trades.append(trade)
            else:
                print('ERROR: no future candles i', i, future_candles_length, len(data))

    gain_percent = sum(trade['gain_percent'] for trade in trades)
    gain_usd = sum(trade['gain_usd'] for trade in trades)
    return gain_percent, gain_usd, trades


################################################################################ HELPERS

def divide_list_into_n_parts(seq, n):
    avg = len(seq) / float(n)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def print_computer_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    the_ip = s.getsockname()[0]
    print('computer running on IP: ', the_ip)
    s.close()
    return the_ip

def get_computer_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    the_ip = s.getsockname()[0]
    s.close()
    return the_ip

def get_candle_as_dict(c):
    return {
        'open_time': int(float(c[0]) / 1000),
        'open_time_readable': ut.get_readable_time(int(c[0])),
        'open_price': float(c[1]),
        'high_price': float(c[2]),
        'low_price': float(c[3]),
        'close_price': float(c[4]),
        'volume': float(c[5]),
        'close_time': int(float(c[6]) / 1000),
        'close_time_readable': ut.get_readable_time(int(c[6])),
    }


def get_future_candles(future_candles_length, data, i):
    future_candles_exist = True
    future_candles = []
    for f in range(1, future_candles_length+1):
        try:
            f_c = data[i+f]
            f_c = get_candle_as_dict(f_c)
            future_candles.append(f_c)
        except IndexError:
            future_candles_exist = False
    # if future_candles_exist:
    #     return future_candles
    if len(future_candles) >= 1:
        return future_candles
    return False


def get_trimmed_symbols(symbols_dict, min_volume_btc):
    symbol_list = []
    symbols_filtered = {}
    for s in symbols_dict:
        symbol = symbols_dict[s]
        if float(symbol['24hourVolume']) >= min_volume_btc:
            symbols_filtered[s] = symbol
            symbol_list.append(s)
    return symbols_filtered, symbol_list


def get_outlier_drops(data, symbol, future_candles_length, drops_to_collect):
    outlier_drops = []
    smallest_drop_percent = 0
    for i, c in enumerate(data):
        c = get_candle_as_dict(c)

        drop = c['open_price'] - c['low_price']
        drop_percent = drop / c['open_price']

        if drop > 0 and drop_percent > smallest_drop_percent:

            future_candles = get_future_candles(future_candles_length, data, i)

            if future_candles:
                # calculate stats on future candles
                best_minute = 1
                best_gain = 0
                best_gain_percent = 0
                total_gain = 0
                total_gain_percent = 0
                for m, f_c in enumerate(future_candles):
                    minute = m + 1
                    gain = f_c['high_price'] - c['low_price']
                    gain_percent = gain / c['low_price']
                    total_gain += gain
                    total_gain_percent += gain_percent
                    if gain > best_gain:
                        best_gain = gain
                        best_gain_percent = best_gain / c['low_price']
                        best_minute = minute
                avg_gain_percent = total_gain_percent / future_candles_length

                # save & sort the biggest drops
                outlier_drops.append({
                    'best_gain_percent': best_gain_percent,
                    'avg_gain_percent': avg_gain_percent,
                    'best_minute': best_minute,
                    'drop_percent': drop_percent,
                    'candle': c,
                    'future_candles': future_candles,
                })
                outlier_drops = sorted(outlier_drops, key=lambda k: k['drop_percent'])
                if len(outlier_drops) > drops_to_collect:
                    del outlier_drops[0]
                smallest_drop_percent = outlier_drops[0]['drop_percent']
    return outlier_drops


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
            
            print('STARTING CANDLES DOWNLOAD', settings, ut.get_time())

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
            symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
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
            print('SAVING CANDLE DATA', settings, 'for', len(coins), 'symbols', ut.get_time())
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
                ut.pickle_write(candle_path, data)

    return True