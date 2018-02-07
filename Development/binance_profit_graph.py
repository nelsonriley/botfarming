#!/usr/bin/python2.7
#
#
#
#
#
################################
#DON'T RUN FILE
################################



import sys
print 'python', sys.version

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

while True:
    api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
    api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
    client = Client(api_key, api_secret)

    asset_balance = client.get_asset_balance(asset='BTC')
    # pprint(asset_balance)
    account_btc_balance = float(asset_balance['free']) + float(asset_balance['locked'])
    print('account_btc_balance', account_btc_balance)

    ryan_btc_before_bots = 1.76225309 + 2.00011051 + 2.26803360 + 1.75044720 + 1.44937472
    #9.23021912


    ryans_symbols = {
        'TRXBTC': 575806,
        'ADABTC': 0,
        'XRPBTC': 9734.518,
        'BNBBTC': 850.6494634,
        'NEOBTC': 240.93049
        }

    prices = client.get_all_tickers()
    # pprint(prices)

    # calc ryan's long term investment value in btc
    btc_dollar_price = 1
    ryan_positions_sum_in_btc = 0
    for p in prices:
        if p['symbol'] == 'BTCUSDT':
            btc_dollar_price = float(p['price'])
        if p['symbol'] in ryans_symbols:
            btc_price = float(p['price'])
            qty = ryans_symbols[p['symbol']]
            btc = btc_price * qty
            ryan_positions_sum_in_btc += btc

    # calc total for all positions held
    total_positions_sum_in_btc = 0
    for p in prices:
        amt = 0
        if p['symbol'][-3:] == 'BTC':
            balance = client.get_asset_balance(asset=p['symbol'][0:len(p['symbol']) - 3])
            if balance:
                btc_price = float(p['price'])
                amt = float(balance['free']) + float(balance['locked'])
                if amt:
                    # print(p['symbol'], amt, btc_price * amt)
                    total_positions_sum_in_btc += btc_price * amt

    # print('total_positions_sum_in_btc', total_positions_sum_in_btc)
    # print('btc account balance', account_btc_balance)
    # print('ryan_positions_sum_in_btc', ryan_positions_sum_in_btc)
    total_profit_so_far = total_positions_sum_in_btc + account_btc_balance - ryan_positions_sum_in_btc - ryan_btc_before_bots
    total_profit_dollars = round(total_profit_so_far * btc_dollar_price, 2)

    epoch = time.time() - 7 * 60 * 60
    the_time = datetime.datetime.fromtimestamp(epoch)
    readable_time = the_time.strftime('%Y-%m-%d %H:%M:%S')

    data = {
        'epoch': epoch,
        'readable_time': readable_time,
        'datetime': the_time,
        'profit': total_profit_so_far,
        'profit_dollars': total_profit_dollars,
        'period_profit': 0
    }

    is_file = os.path.isfile('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graph.pklz')
    if is_file:
        #read
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graph.pklz','rb')
        data_points = pickle.load(f)
        f.close()
        data['period_profit'] = round(total_profit_so_far - data_points[-1]['profit'], 8)
        data_points.append(data)
        #write
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graph.pklz','wb')
        pickle.dump(data_points, f)
        f.close()
        print('file updated')
    else:
        #save the file first time
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profit_graph.pklz','wb')
        pickle.dump([data], f)
        f.close()
        print('file created')

    pprint(data)
    time.sleep(15*60)