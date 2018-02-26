#!/usr/bin/python2.7

# sell off all symbols if something went wrong with the bot

import sys
print('python', sys.version)
import pickle
import gzip
import time
import os
import datetime
from pprint import pprint
import utility as ut
import utility_2 as ut2
import numpy
from binance.client import Client
from binance.websockets import BinanceSocketManager

# nelson
api_key = '1tD2w1Vner9qgObI1FaeUaCkJQ5m2i34UyrbSWE3l20tIX66tnHDmAYUQp8HwLtq'
api_secret = 'Zst9mdv9MkLxB5JNoSYNkcuO2dWXhln3gHKxgqQZhNdzfxel4OEbEun8BW2TC5Fv'
client = Client(api_key, api_secret)

symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')

info = client.get_account()
# pprint(info)
sell_count = 0
print('STARTING', ut.get_time())
for i, b in enumerate(info['balances']):
    if i < 99999: # 60
        if b['asset'] == 'BTC' or b['asset'] == 'BNB':
            continue
        base_qty = float(b['free'])
        s = b['asset']+'BTC'
        for k in symbols:
            symbol = symbols[k]
            if symbol['symbol'] == s:
                symbol = symbol
                break
        if base_qty > 0 and base_qty >= float(symbol['filters'][1]['minQty']):
            print('SELLING', s, 'base_qty', base_qty)
            sell_count += 1
            # cancel any existing orders
            orders = client.get_open_orders(symbol=s)
            for o in orders:
                result = client.cancel_order(symbol=s, orderId=o['orderId'])
            # then sell coin
            current_state = {}
            current_state['symbol'] = s
            current_state['sell_price_drop_factor'] = 1
            current_state['original_buy_time'] = int(time.time()) - 5
            current_state['client'] = client
            current_state['orderId'] = False
            current_state['length'] = '1m'
            current_state['file_number'] = '2000'
            current_state['version'] = '24hr_1min_drop_v0'
            current_state['min_price'] = float(symbol['filters'][0]['minPrice'])
            current_state['minQty'] = float(symbol['filters'][1]['minQty'])
            current_state['min_quantity'] = float(symbol['filters'][1]['minQty'])
            current_state['minNotional'] = float(symbol['filters'][2]['minNotional'])
            current_state['price_decimals'] = ut.get_min_decimals(current_state['min_price'])
            base_qty_min = float(symbol['filters'][1]['minQty'])
            base_qty_decimals = ut.get_min_decimals(base_qty_min)
            base_qty_for_order = ut.float_to_str(ut2.roundDown(base_qty, base_qty_decimals))
            current_state['executedQty'] = float(base_qty_for_order)
            current_state['total_revenue'] = 0
            
            # pprint(current_state)

            mode = 'fast'
            sold_coin, current_state = ut.sell_with_order_book(current_state, 0.0, minutes_until_sale=60, mode=mode)
            if sold_coin:
                print('SOLD', s, ut.get_time())
                current_state_path = '/home/ec2-user/environment/botfarming/Development/program_state_' + current_state['length'] + '/program_state_' + current_state['length'] + '_' + current_state['file_number'] + '_' + current_state['symbol'] + '_V' + current_state['version'] + '.pklz'
                ut.pickle_write(current_state_path, False)

print('FINISHED', ut.get_time(), 'sold', sell_count, 'coins')
sys.exit()











# symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
# print('btc symbols found:', len(symbols))

for s in symbols:
    if s != 'BNBBTC':
        # print(s)
        
        if s == 'GTOBTC':
            orders = client.get_open_orders(symbol=s)
            pprint(orders)
            # for o in orders:
            #     result = client.cancel_order(symbol=s, orderId=o['orderId'])
            
            balance = client.get_asset_balance(asset=s)
            pprint(balance)
            # {
            #     "asset": "BTC",
            #     "free": "4723846.89208129",
            #     "locked": "0.00000000"
            # }
            
            # sold_coin, current_state = ut.sell_with_order_book(current_state, 0.0, minutes_until_sale=60)
            
            # sale_order_info = client.get_order(symbol=s)
            # pprint(sale_order_info)
        
        # if sale_order_info['status'] == 'FILLED':
        #     sold_coin, current_state = ut.sell_with_order_book(current_state, 0.0, minutes_until_sale=60)
        #     # print('FILLING', s, ut.get_time(), current_state['original_quantity'], current_state['executedQty'], sale_order_info['price'], current_state['total_revenue'])
        #     current_state['executedQty'] = current_state['executedQty'] - float(sale_order_info['executedQty'])
        #     current_state['total_revenue'] += float(sale_order_info['executedQty']) * float(sale_order_info['price'])
        #     current_state['state'] = 'selling'
        #     current_state['orderId'] = False
        #     current_state['sell_price'] = float(sale_order_info['price'])
        #     ut.pickle_write(current_state_path, current_state, '******could not write state selling******')
        #     if current_state['executedQty'] < current_state['min_quantity']:
        #         print('FILLED', s, ut.get_time())

# sell_with_order_book()