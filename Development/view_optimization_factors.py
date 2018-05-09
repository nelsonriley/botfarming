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
import json
import math
from binance.client import Client
import utility_3 as ut

# length = '4h'
# min_gain = .05
# minutes = 4*60
#look_back_array = [1,2,3,4,5,7,9,11]
#optimization_length = 120

# length = '6h'
# min_gain = .15
# minutes = 6*60
# look_back_array = [1,2,3,4,5,7,9,11]
# optimization_length = 120

# length = '12h'
# min_gain = .19
# minutes = 12*60
# look_back_array = [1,2,3,4,5,7,9,11]
# optimization_length = 120

# length = '1d'
# min_gain = .2
# minutes = 24*60
# look_back_array = [1,2,3,4,5,7,9,11]
# optimization_length = 120
# version = '1_'

# length = '1m'
# min_gain = .001
# minutes = 1
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '2_'


# length = '5m'
# min_gain = .001
# minutes = 5
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '2_'

length = '15m'
min_gain = .001
minutes = 15
look_back_array = [1,5,9,15]
optimization_length = 360
version = '1_'

# length = '30m'
# min_gain = .001
# minutes = 30
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '2_'

# length = '1d'
# min_gain = .001
# minutes = 24*60
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '1_'

# length = '12h'
# min_gain = .001
# minutes = 12*60
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '1_'

# length = '6h'
# min_gain = .001
# minutes = 6*60
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '1_'

# length = '2h'
# min_gain = .001
# minutes = 2*60
# look_back_array = [1,3,5,7,9,11,13,15]
# optimization_length = 360
# version = '1_'

# length = '1h'
# min_gain = .001
# minutes = 1*60
# look_back_array = [1,5,9,15]
# optimization_length = 360
# version = '1_'



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
total_buy_sell_difference = 0

for s in symbols_trimmed:
    symbol = symbols_trimmed[s]
    print('')
    print('start symbol', symbol['symbol'], symbol['24hourVolume'])
    total_symbols += 1
    
    # if symbol['symbol'] == 'BCPTBTC':
    #      break
    
    for look_back in look_back_array:
        look_back_optimized = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/' + version + length  + '_optimal_for_' + symbol['symbol'] + '_' + str(look_back) + '.pklz')
        if look_back_optimized != False:
            print('look_back', look_back_optimized['look_back'], 'lowest_buy_factor', look_back_optimized['lowest_buy_factor'],'highest_sale_factor', look_back_optimized['highest_sale_factor'])
            # print('highest_sale_factor -  lowest_buy_factor', look_back_optimized['highest_sale_factor'] - look_back_optimized['lowest_buy_factor'])
            # print('modified_sale_factor', look_back_optimized['highest_sale_factor'] - look_back_optimized['lowest_buy_factor'] - (look_back_optimized['highest_sale_factor'] - look_back_optimized['lowest_buy_factor'])*.15)
