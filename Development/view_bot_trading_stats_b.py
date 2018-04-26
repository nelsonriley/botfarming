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
from operator import itemgetter
from os import listdir
from os.path import isfile, join
 
## SCHEMA ##
# 'time start', bot_trade[0]
# 'symbol', bot_trade[1]
# 'asolute profit', bot_trade[2]
# 'percentage profit', bot_trade[3]
# 'bit coin invested', bot_trade[4]
# 'look_back', bot_trade[5]
# 'a_b', bot_trade[6]
# 'price_to_buy_factor', bot_trade[7]
# 'price_to_sell_factor', bot_trade[8]
# 'original_buy_time', bot_trade[9]
# 'sell time', bot_trade[10])

symbols_saved = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')

path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/'
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

look_backs = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']
look_backs = ['1m']

for look_back in look_backs:
    
    print('look_back', look_back)
    
    bot_trades = []
    
    for file in onlyfiles:
        if file.startswith(look_back + "_0"):
            #print('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            trade = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            if len(trade) == 11:
                trade.append(look_back)
                trade[0] = ut.convert_date_to_epoch(trade[0])
                trade[10] = ut.convert_date_to_epoch(trade[10])
                bot_trades.append(trade)
                
    total_profit = 0
    total_trades = 0
    
    # get avg profit per trade
    # get 24 hr volume
    
    data_by_symbol = {} 
    
    for i, bot_trade in enumerate(bot_trades):
    
        # Sat Mar 31 1522540800
        # Sunday, April 22, 2018 12:00:00 PM  1524420000
        if bot_trade[0] > 1524420000 and bot_trade[1] != 'CTRBTC':
            total_profit += bot_trade[2] # 'absolute profit', bot_trade[2], 'percentage profit', bot_trade[3]
            total_trades += 1
            
            if bot_trade[1] not in data_by_symbol:
                data_by_symbol[bot_trade[1]] = {
                    'symbol': bot_trade[1],
                    '24_hour_volume': float(symbols_saved[bot_trade[1]]['24hourVolume']),
                    'trade_count': 0,
                    'trade_profit_percent_sum': 0,
                    'avg_profit_percent': 0
                }
                
            data = data_by_symbol[bot_trade[1]]
            data['trade_count'] += 1.0
            data['trade_profit_percent_sum'] += bot_trade[3]
            data['avg_profit_percent'] = data['trade_profit_percent_sum'] / data['trade_count']
            
            ## SCHEMA ##
            # 'time start', bot_trade[0]
            # 'symbol', bot_trade[1]
            # 'asolute profit', bot_trade[2]
            # 'percentage profit', bot_trade[3]
            # 'bit coin invested', bot_trade[4]
            # 'look_back', bot_trade[5]
            # 'a_b', bot_trade[6]
            # 'price_to_buy_factor', bot_trade[7]
            # 'price_to_sell_factor', bot_trade[8]
            # 'original_buy_time', bot_trade[9]
            # 'sell time', bot_trade[10])
            
    for symbol in data_by_symbol:
        pprint(data_by_symbol[symbol])
        print('--------------')
        
    for symbol in data_by_symbol:
        d = data_by_symbol[symbol]
        print d['symbol'], ',', d['24_hour_volume'], ',', d['avg_profit_percent'], ',', d['trade_count'], ',', d['trade_profit_percent_sum']
    

    print('total_profit', total_profit)
    print('total_trades', total_trades)
    
print('')