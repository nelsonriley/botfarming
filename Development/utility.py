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

def get_readable_time(time_to_get):
    return datetime.datetime.fromtimestamp(int(time_to_get)).strftime('%Y-%m-%d %H:%M:%S')

def get_time():
    return datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')


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


def cancel_sale_order(current_state, sale_order_info):

    current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
    current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])

    try:
        sale_canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=sale_order_info['orderId'])
    except Exception as e:
        print('could not cancel sale order, assuming sale order filled or manually canceled, calculating profit and freeing coin...')
        print(e)
        current_state['error_cancel_order'] = True
        return current_state

    current_state['state'] = 'selling'
    current_state['orderId'] = False
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state******')

    return current_state

def create_sale_order(current_state, price_to_sell):

    sale_order = current_state['client'].order_limit_sell(symbol=current_state['symbol'],quantity=current_state['executedQty'],price=price_to_sell)

    current_state['state'] = 'selling'
    current_state['orderId'] = sale_order['orderId']
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not write state 2nd sell******')

    return current_state

def calculate_profit_and_free_coin(current_state):

    print('coin sold, calculating profit and freeing coin', current_state['symbol'],get_time())
    percent_profit_from_trade = (current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price'])/(current_state['original_quantity']*current_state['original_price'])
    profit_from_trade = current_state['total_revenue'] - current_state['original_quantity']*current_state['original_price']
    print('profit was, absoulte profit, percent', profit_from_trade, percent_profit_from_trade, get_time())
    append_or_create_data('./binance_' + current_state['length'] + '_trades/'+ current_state['length'] + '_trade_data', [profit_from_trade, percent_profit_from_trade, current_state['symbol'],current_state['original_buy_time_readable'], get_time()])
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False)
    pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + current_state['symbol'] + '.pklz', False)


def save_buy_order_info_to_state(current_state, buy_order_info):
    current_state['executedQty'] = float(buy_order_info['executedQty'])
    current_state['original_quantity'] = float(buy_order_info['executedQty'])
    current_state['original_price'] = float(buy_order_info['price'])
    current_state['state'] = 'selling'
    current_state['orderId'] = False
    pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', current_state, '******could not update state to selling******')
    return current_state


def sell_coin(current_state):

    if current_state['executedQty'] != 0:

        print('selling..', current_state['symbol'], get_time())

        current_state = create_sale_order(current_state, current_state['price_to_sell'])

        minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
        print('sell_coin() 1st sale_order created, sleeping for', current_state['minutes_until_sale'] - minutes_since_start-1, current_state['symbol'])
        sleep_but_check_order(current_state, current_state['minutes_until_sale'] - minutes_since_start-1)
        print('sell_coin() awake from 1st sale attempt', current_state['symbol'])

        sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])

        if sale_order_info['status'] != 'FILLED':

            current_state = cancel_sale_order(current_state, sale_order_info)
            if current_state['error_cancel_order']:
                calculate_profit_and_free_coin(current_state)
                return

            current_state = create_sale_order(current_state, current_state['price_to_sell_2'])

            minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
            print('sell_coin() 2nd sale_order created, sleeping for', current_state['minutes_until_sale_2']-minutes_since_start-1, current_state['symbol'])
            sleep_but_check_order(current_state, current_state['minutes_until_sale_2']-minutes_since_start-1)
            print('sell_coin() awake from 2nd sale attempt', current_state['symbol'])

            sale_order_info_2 = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])

            if sale_order_info_2['status'] != 'FILLED':

                current_state = cancel_sale_order(current_state, sale_order_info_2)
                if current_state['error_cancel_order']:
                    calculate_profit_and_free_coin(current_state)
                    return

                current_state = create_sale_order(current_state, current_state['price_to_sell_3'])

                minutes_since_start = int(round((int(time.time()) - current_state['original_buy_time'])/60))
                print('sell_coin() 3rd sale_order created, sleeping for', current_state['minutes_until_sale_3']-minutes_since_start-1, current_state['symbol'])
                sleep_but_check_order(current_state, current_state['minutes_until_sale_3']-minutes_since_start-1)
                print('sell_coin() awake from 3rd sale attempt', current_state['symbol'])

                sale_order_info_3 = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])

                if sale_order_info_3['status'] != 'FILLED':

                    print('sell_coin() 3rd sale order not filled, creating MARKET sale order..', current_state['symbol'], get_time())

                    current_state = cancel_sale_order(current_state, sale_order_info_3)
                    if current_state['error_cancel_order']:
                        calculate_profit_and_free_coin(current_state)
                        return

                    final_sale_order = current_state['client'].order_market_sell(symbol=current_state['symbol'], quantity=current_state['executedQty'])

                    order_book = current_state['client'].get_order_book(symbol=current_state['symbol'])

                    current_state['total_revenue'] += float(final_sale_order['executedQty'])*float(order_book['bids'][0][0])


                else:
                    current_state['total_revenue'] += float(sale_order_info_3['executedQty']) * float(sale_order_info_3['price'])
            else:
                current_state['total_revenue'] += float(sale_order_info_2['executedQty']) * float(sale_order_info_2['price'])
        else:
            current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])


    calculate_profit_and_free_coin(current_state)
    return

def buy_coin_from_state(current_state):

    print('buy coin from state', current_state['symbol'])

    if (current_state['state'] == 'buying'):
        print('current state was buying', current_state['symbol'])
        buy_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])

        if float(buy_order_info['executedQty']) == 0:
            print('order not filled, canceling order and freeing coin')
            try:
                canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
            except Exception as e:
                print('error canceling order... freeing coin')
                print(e)

            pickle_write('./program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '.pklz', False, '******could not write state buy from stae******')
            pickle_write('./binance_is_invested_' + current_state['length'] + '/is_invested_' + current_state['length'] + '_' + current_state['symbol'] + '.pklz', False)
            return
        else:
            print('some or all of the buy order filled, executed qty', buy_order_info['executedQty'])
            current_state = save_buy_order_info_to_state(current_state, buy_order_info)
            try:
                canceled_order = current_state['client'].cancel_order(symbol=current_state['symbol'], orderId=current_state['orderId'])
            except Exception as e:
                print('error canceling order, but need to sell coin as some was executed')
                print(e)

    ##are selling...
    print('buy_coin_from_state() selling..', current_state['symbol'])

    if current_state['orderId'] > 0:

        print('sale order exisits canceling it..')
        sale_order_info = current_state['client'].get_order(symbol=current_state['symbol'],orderId=current_state['orderId'])
        current_state = cancel_sale_order(current_state, sale_order_info)
        if current_state['error_cancel_order']:
            calculate_profit_and_free_coin(current_state)
            return

    print('buy_coin_from_state() no open orders, selling coin..', current_state['symbol'])
    sell_coin(current_state)


def buy_coin(symbol, length, file_number, data=[]):

    #if (symbol['symbol'] == 'ETCBTC'):
    #print("started buy coin ", symbol['symbol'])

    #pickle_write('./program_still_running_' +length + '/'+symbol['symbol']+,True)

    current_state = load_current_state(symbol['symbol'], file_number, length)

    if isinstance(current_state,dict):
        print('loading state to sell coin..', current_state['symbol'])
        buy_coin_from_state(current_state)
        return

    try:

        if (length == '1m'):

            trail_vol_min = 3000
            price_to_start_buy = 1.003
            lower_band_buy_factor = .989
            price_to_buy_factor = .989
            bollingers_percentage_increase_factor = -.006
            datapoints_trailing = 22


            minutes_until_sale = 30
            minutes_until_sale_2 = 45
            minutes_until_sale_3 = 60
            price_to_sell_factor = .996
            price_to_sell_factor_2 = .985
            price_to_sell_factor_3 = .965
            part_of_bitcoin_to_use = .2

            minutes = 1

        if(length == '30m'):

            price_to_start_buy = 1.003
            price_to_buy_factor = .92
            datapoints_trailing = 1

            minutes_until_sale = 2
            minutes_until_sale_2 = 9
            minutes_until_sale_3 = 100

            price_to_sell_factor = .999
            price_to_sell_factor_2 = .981
            price_to_sell_factor_3 = .974

            # settings
            part_of_bitcoin_to_use = .2
            minutes = 30

        # get candles
        # data can now be passed in to allow parallel processing, but function still works if not passed in
        if len(data) == 0:
            end_time = int(time.time())*1000
            start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))
            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
            r = requests.get(url)
            data = r.json()
            # TODO data = get_smart_candles(data)
        if isinstance(data, basestring):
            print('API request failed, exiting', symbol['symbol'])
            return

        trailing_volumes = []
        trailing_movement = []
        trailing_lows = []
        trailing_highs = []

        for index, candle in enumerate(data):
            # compare (only last candle)
            if len(trailing_movement) >= datapoints_trailing:


                trailing_and_current_candles = data[index-datapoints_trailing:index]
                trailing_and_current_candles, smart_trailing_candles = fn.add_bollinger_bands_to_candles(trailing_and_current_candles)

                bollingers_percentage_increase = (trailing_and_current_candles[-1][14] - trailing_and_current_candles[-2][14])/trailing_and_current_candles[-2][14]
                lower_band_for_index = trailing_and_current_candles[-1][14]
                should_buy = float(candle[4]) < lower_band_for_index*lower_band_buy_factor*price_to_start_buy and bollingers_percentage_increase > bollingers_percentage_increase_factor and float(candle[4]) < float(candle[1])*price_to_buy_factor*price_to_start_buy and numpy.mean(trailing_volumes) > trail_vol_min



                #should_buy = float(candle[4]) < lower_band_for_index*lower_band_buy_factor*price_to_start_buy

                #should_buy = float(candle[4]) < float(candle[1])*price_to_buy_factor*price_to_start_buy
                #and trailing_slope_ok
                if should_buy:

                    try:
                        is_invested = pickle_read('./binance_is_invested_' + length +'/is_invested_'+ length + '_' + symbol['symbol'] + '.pklz')
                    except Exception as e:
                        is_invested = False

                    if is_invested == False:

                        print('buy', symbol['symbol'])

                        pickle_write('./binance_is_invested_' + length + '/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', True)

                        # init binance client
                        api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
                        api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
                        client = Client(api_key, api_secret)

                        price_to_buy = min(lower_band_for_index*lower_band_buy_factor, float(candle[1])*price_to_buy_factor)
                        price_to_sell = float(candle[1])*price_to_sell_factor
                        price_to_sell_2 = float(candle[1])*price_to_sell_factor_2
                        price_to_sell_3 = float(candle[1])*price_to_sell_factor_3

                        amount_to_buy = part_of_bitcoin_to_use/price_to_buy

                        price_decimals = get_min_decimals(symbol['filters'][0]['minPrice'])

                        price_to_buy = float_to_str(round(price_to_buy, price_decimals))
                        price_to_sell = float_to_str(round(price_to_sell, price_decimals))
                        price_to_sell_2 = float_to_str(round(price_to_sell_2, price_decimals))
                        price_to_sell_3 = float_to_str(round(price_to_sell_3, price_decimals))

                        decimals = get_min_decimals(symbol['filters'][1]['minQty'])
                        # decimals = get_min_decimals_new(symbol['filters'][2]['minNotional'])

                        amount_to_buy = float_to_str(round(amount_to_buy, decimals))

                        buy_order = client.order_limit_buy(symbol=symbol['symbol'],quantity=amount_to_buy,price=price_to_buy)

                        current_state = {}
                        current_state['state'] = 'buying'
                        current_state['original_buy_time'] = int(time.time())
                        current_state['symbol'] = symbol['symbol']
                        current_state['orderId'] = buy_order['orderId']
                        current_state['original_buy_time_readable'] = get_time()
                        current_state['executedQty'] = 0
                        current_state['total_revenue'] = 0
                        current_state['minutes_until_sale'] = minutes_until_sale
                        current_state['minutes_until_sale_2'] = minutes_until_sale_2
                        current_state['minutes_until_sale_3'] = minutes_until_sale_3
                        current_state['decimals'] = decimals
                        current_state['price_to_sell'] = price_to_sell
                        current_state['price_to_sell_2'] = price_to_sell_2
                        current_state['price_to_sell_3'] = price_to_sell_3
                        current_state['length'] = length
                        current_state['file_number'] = str(file_number)
                        current_state['client'] = client
                        current_state['error_cancel_order'] = False


                        pickle_write('./program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz', current_state, '******could not write state******')

                        time.sleep(3*1)

                        buy_order_info = client.get_order(symbol=current_state['symbol'],orderId=buy_order['orderId'])

                        if buy_order_info['status'] != 'FILLED':
                            time.sleep(15*1)
                            buy_order_info = client.get_order(symbol=current_state['symbol'],orderId=buy_order['orderId'])

                        if buy_order_info['status'] != 'FILLED':
                            time.sleep(15*1)
                            buy_order_info = client.get_order(symbol=current_state['symbol'],orderId=buy_order['orderId'])

                        if buy_order_info['status'] != 'FILLED':
                            time.sleep(27*1)
                            buy_order_info = client.get_order(symbol=current_state['symbol'],orderId=buy_order['orderId'])

                        if buy_order_info['status'] != 'FILLED':
                            canceled_order = client.cancel_order(symbol=current_state['symbol'], orderId=buy_order_info['orderId'])

                        if float(buy_order_info['executedQty']) == 0:
                            print('no one bought cancel order - freeing coin', current_state['symbol'])
                            pickle_write('./binance_is_invested_' + length + '/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', False)
                            pickle_write('./program_state_' + length + '/program_state_' + length + '_' + str(file_number) + '_' + symbol['symbol'] + '.pklz', False, '******could not write state inside buy coin - no one bought coin******')
                            return True

                        current_state = save_buy_order_info_to_state(current_state, buy_order_info)

                        sell_coin(current_state)


                        print('finished order - freeing coin', current_state['symbol'])

                        pickle_write('./binance_is_invested_' + length + '/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', False)

                        print('#########################')
                        return True

                    else:
                        print('coin invested skipping..', symbol['symbol'])


            # update
            if len(trailing_movement) <= datapoints_trailing:
                trailing_volumes.append(float(candle[5]))
                trailing_movement.append(abs(float(candle[4])-float(candle[1])))
                trailing_highs.append(float(candle[2]))
                trailing_lows.append(float(candle[3]))
            if len(trailing_movement) > datapoints_trailing:
                break

        return True

    except Exception as e:
        print('some error - freeing coin:', symbol['symbol'])
        print(e)
        print_exception()
        pickle_write('./binance_is_invested_' + length + '/is_invested_' + length + '_' + symbol['symbol'] + '.pklz', False)
        time.sleep(120)
        return False

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
        symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
        symbol_r = requests.get(symbol_url)

        symbol_data = symbol_r.json()

        total_btc_coins = 0

        for symbol in symbol_data['symbols']:
            if symbol['quoteAsset'] == 'BTC':
                total_btc_coins += 1

    except Exception as e:
            print(e)
            sys.exit()

    symbol_back_up = symbol
    current_state = []

    while True:

        symbol = symbol_back_up
        try:
            loops = 0

            file_start_index = file_number
            file_end_index = (file_number+overlap)%total_files
            if file_end_index == 0:
                file_end_index = total_files

            file_start_number = math.floor(total_btc_coins/total_files)*file_start_index
            file_end_number = file_end_index*math.floor(total_btc_coins/total_files)

            for symbol in symbol_data['symbols']:

                if symbol['quoteAsset'] == 'BTC':

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

            symbol = symbol_back_up

            loops = 0

            for symbol in symbol_data['symbols']:

                if symbol['quoteAsset'] == 'BTC':

                    if file_end_index < overlap:
                        if loops >= file_start_number or loops < file_end_number:
                            buy_coin(symbol, length, file_number)
                    else:
                        if loops >= file_start_number and loops < file_end_number:
                            buy_coin(symbol, length, file_number)

                    loops += 1

        except Exception as e:
            print('error in wrapper')
            print(e)
            print_exception()
            continue

def run_bot_parallel(length):

    print('running bot w concurrent requests')
    try:
        symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
        symbol_r = requests.get(symbol_url)
        symbol_data = symbol_r.json()

    except Exception as e:
            print(e)
            sys.exit()

    print('fetching all symbols in parallel')

    if (length == '1m'):
        datapoints_trailing = 10
        minutes = 1
    if (length == '30m'):
        datapoints_trailing = 1
        minutes = 30

    try:

        end_time = int(time.time())*1000
        start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))

        for index, symbol in enumerate(symbol_data['symbols']):
            if symbol['quoteAsset'] == 'BTC':
                url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+length+'&startTime='+str(start_time)+'&endTime='+str(end_time)
                call_back_args = [url,symbol,length]
                t = Thread(target=get_candles_then_buy_coin, args=call_back_args)
                t.start()

    except Exception as e:
        print('error in wrapper run_bot_parallel()')
        print(e)
        print_exception()


# "worker"
def get_candles_then_buy_coin(url, symbol, length):
    while True:
        try:
            r = requests.get(url)
            data = r.json()
            buy_coin(symbol, length, 1000, data)
        except Exception as e:
            print(e)
            print("error in worker, continuing")
        now = datetime.datetime.now()
        if length == '1m':
            if now.second > 45:
                time.sleep(3)
            else:
                time.sleep(8)
        if length == '30m':
            time.sleep(15)


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