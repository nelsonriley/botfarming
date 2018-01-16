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

should_check = {}
file_number = 10
total_files = 12
overlap = 3

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

while True:

    symbol = symbol_back_up
    try:
        loops = 0
        for symbol in symbol_data['symbols']:

            if symbol['quoteAsset'] == 'BTC':

                file_start_index = file_number
                file_end_index = (file_number+overlap)%total_files
                if file_end_index == 0:
                    file_end_index = total_files

                file_start_number = math.floor(total_btc_coins/total_files)*file_start_index
                file_end_number = file_end_index*math.floor(total_btc_coins/total_files)

                if file_end_index < overlap:
                    if loops >= file_start_number or loops < file_end_number:
                        if not ut.buy_coin(symbol):
                            print('here')
                            break
                else:
                    if loops >= file_start_number and loops < file_end_number:
                        if not ut.buy_coin(symbol):
                            print('here')
                            break
                loops += 1

    except Exception as e:
        print('error in wrapper')
        #print(e)
        continue
    #print('done')
