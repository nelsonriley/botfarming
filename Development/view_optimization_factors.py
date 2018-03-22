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

# length = '4h'
# min_gain = .05
# minutes = 4*60
#look_back_array = [1,2,3,4,5,7,9,11]
#optimization_length = 120

# length = '6h'
# min_gain = .15
# minutes = 6*60
#look_back_array = [1,2,3,4,5,7,9,11]
#optimization_length = 120

# length = '12h'
# min_gain = .19
# minutes = 12*60
#look_back_array = [1,2,3,4,5,7,9,11]
#optimization_length = 120

# length = '1d'
# min_gain = .2
# minutes = 24*60
#look_back_array = [1,2,3,4,5,7,9,11]
#optimization_length = 120

length = '1m'
min_gain = .001
minutes = 1
look_back_array = [1,3,5,7]
optimization_length = 360




######
symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
    
total_btc_coins = 0
symbols_trimmed = {}

for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 300:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol
        

total_gain = 0
total_symbols = 0
total_trades = 0

for s in symbols_trimmed:
    symbol = symbols_trimmed[s]
    print('')
    print(symbol['symbol'], symbol['24hourVolume'])
    total_symbols += 1
    
    for look_back in look_back_array:
        look_back_optimized = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/' + length  + '_optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '.pklz')
        if look_back_optimized != False and look_back_optimized['wins'] + look_back_optimized['losses'] > 0 and look_back_optimized['gain']/(look_back_optimized['wins'] + look_back_optimized['losses']) > min_gain:
            print(symbol['symbol'], 'look_back', look_back_optimized['look_back'],'gain', look_back_optimized['gain'], 'ave_gain', look_back_optimized['gain']/(look_back_optimized['wins'] + look_back_optimized['losses']), 'wins',  look_back_optimized['wins'], 'losses', look_back_optimized['losses'])
            print(symbol['symbol'], look_back_optimized['optimal_buy_factor'], look_back_optimized['optimal_sell_factor'], look_back_optimized['optimal_band_factor'], look_back_optimized['optimal_increase_factor'], look_back_optimized['optimal_minutes_until_sale'])
            if look_back_optimized['gain'] > 0:
                total_gain += look_back_optimized['gain']
                total_trades += look_back_optimized['wins'] + look_back_optimized['losses']
            
    
print('total_gain', total_gain)
print('total_symbols', total_symbols)
print('total_trades', total_trades)
print('trades per minute', float(total_trades)/(minutes*optimization_length))
print('trades per day', float(total_trades)/(float(minutes)*optimization_length/(24*60)))
