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

    print('total_btc_coins with volume >', min_symbol_volume, '---', total_btc_coins)

except Exception as e:
    print(e)
    sys.exit()