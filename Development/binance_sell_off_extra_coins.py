#!/usr/bin/python2.7
import sys
print 'python', sys.version

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import utility_3 as ut
import json
import math
from os import listdir
from os.path import isfile, join
from binance.client import Client

coins_not_to_sell = {}


while True:
    try:
    
        symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
    
        total_btc_coins = 0
        symbols_trimmed = {}
        min_symbol_volume = 300
        global socket_list
        socket_list = []
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
                    print('')
                    print('coin has state..', current_state['symbol'], current_state['executedQty']*current_state['price_to_buy'], current_state['executedQty'])
                    coins_not_to_sell[current_state['symbol']] = 1
    
    
        api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
        api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
        client = Client(api_key, api_secret)
        
        acct_info = client.get_account()
        
        for balance in acct_info['balances']:
            pprint(balance)
            if balance['asset'] != 'BTC' and balance['asset'] != 'BNB' and balance['asset'] != 'XVG':
                try:
                    symbol = symbols[balance['asset']+'BTC']
                    if balance['asset'] + 'BTC' in coins_not_to_sell:
                        print('do not sell', balance['asset'])
                    elif float(balance['free']) > 0:
                        print('sell', balance['asset'])
                        min_quantity = max(float(symbol['filters'][1]['minQty']), float(symbol['filters'][2]['minNotional']))
                        print('min_quantity', min_quantity)
                        if float(balance['free']) > float(min_quantity):
                            quantity_decimals = ut.get_min_decimals(symbol['filters'][1]['minQty'])
                            print('quantity_decimals', quantity_decimals)
                            if float(quantity_decimals) == 0:
                                quantity_for_sale = str(math.floor(float(balance['free'])))
                            else:
                                quantity_for_sale = ut.float_to_str(ut.round_down(float(balance['free']),quantity_decimals),quantity_decimals)
                            print('quantity_for_sale', quantity_for_sale)
                            sale_order = client.order_market_sell(symbol=symbol['symbol'], quantity=quantity_for_sale)
                            pprint(sale_order)
                except Exception as e:
                    print(e)
                    #for balance in acct_info['balances']:
        print('sleeping..')
        time.sleep(30*60)
    except Exception as e:
        print(e)
    