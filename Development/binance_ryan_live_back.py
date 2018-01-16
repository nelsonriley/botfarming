
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

while True:

    symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
    symbol_r = requests.get(symbol_url)
    symbol_data = symbol_r.json()

    #print('running')

    print(int(time.time())%60)

    total_btc_coins = 0

    for symbol in symbol_data['symbols']:
        if symbol['quoteAsset'] == 'BTC':
            total_btc_coins += 1

    loops = 0
    for symbol in symbol_data['symbols']:

        if symbol['quoteAsset'] == 'BTC':
            loops += 1
            if (loops >= math.floor(total_btc_coins/12)*file_number and loops < math.floor(total_btc_coins/12)*(file_number+1)):
                seconds_into_minute = int(time.time())%60
                if (seconds_into_minute < 30):
                    should_check[symbol['symbol']] = True

    seconds_into_minute = int(time.time())%60
    if (seconds_into_minute < 30):
        time.sleep(30 - seconds_into_minute)

    loops = 0
    for symbol in symbol_data['symbols']:

        if symbol['quoteAsset'] == 'BTC':
            loops += 1
            if (loops >= math.floor(total_btc_coins/12)*file_number and loops < math.floor(total_btc_coins/12)*(file_number+1)):
                try:
                    gotdata = should_check[symbol['symbol']]
                except KeyError:
                    should_check[symbol['symbol']] = True

                if should_check[symbol['symbol']] == True:
                    should_check[symbol['symbol']] = ut.buy_coin(symbol['symbol'])
                    print(should_check[symbol['symbol']])

    #print('done')
