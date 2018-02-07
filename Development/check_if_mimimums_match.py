#!/usr/bin/python2.7
import sys
print('python', sys.version)

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime
import utility as ut
import functions_financial as fn

symbols = ut.pickle_read('./botfarming/Development/binance_btc_symbols.pklz')

total_btc_coins = 0
symbols_trimmed = {}

for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol

total_data_points = 0
for s in symbols_trimmed:
    symbol = symbols_trimmed[s]

    #print symbol['symbol']
    our_one_minute_minimums = ut.pickle_read('./botfarming/Development/candle_minimums/candle_minimum_' + symbol['symbol'])

    url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval=1m&startTime=1517442420000&endTime=1517528820000'
    r = requests.get(url)
    data = r.json()


    for index,one_minutes in enumerate(our_one_minute_minimums):
        if index > 2:
            total_data_points += 1
            if (one_minutes[1] - float(data[index-2][3]))/float(data[index-2][3]) > .001:
                print(symbol['symbol'], (one_minutes[1] - float(data[index-2][3]))/float(data[index-2][3]))
                print()

            # print(ut.get_readable_time(one_minutes[0] - 60), one_minutes[1])
            # print(ut.get_readable_time(data[index-2][0]), data[index-2][3])
            # print((one_minutes[1] - float(data[index-2][3]))/float(data[index-2][3]))
            # print()



print total_data_points








