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
import utility as ut
import json
import math
from binance.client import Client

length = '12h'


######
symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
    
total_btc_coins = 0
symbols_trimmed = {}

for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol
        

total_gain = 0
total_symbols = 0
look_back_array = [1,2,4]
for s in symbols_trimmed:
    symbol = symbols_trimmed[s]
    print('')
    print(symbol['symbol'], symbol['24hourVolume'])
    total_symbols += 1
    
    for look_back in look_back_array:
        look_back_optimized = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/' + length  + '_optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '.pklz')
        if look_back_optimized != False and look_back_optimized['wins'] + look_back_optimized['losses'] > 2 and look_back_optimized['gain']/(look_back_optimized['wins'] + look_back_optimized['losses']) > .06:
            print(symbol['symbol'], look_back_optimized['look_back'], look_back_optimized['gain'], look_back_optimized['wins'], look_back_optimized['losses'])
            print(symbol['symbol'], look_back_optimized['optimal_buy_factor'], look_back_optimized['optimal_sell_factor'], look_back_optimized['optimal_band_factor'], look_back_optimized['optimal_increase_factor'], look_back_optimized['optimal_minutes_until_sale'])
            if look_back_optimized['gain'] > 0:
                total_gain += look_back_optimized['gain']
            
    
print('total_gain', total_gain)
print('total_symbols', total_symbols)
