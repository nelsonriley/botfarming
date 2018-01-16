
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
file_number = 0

while True:

    symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
    symbol_r = requests.get(symbol_url)
    symbol_data = symbol_r.json()

    total_btc_coins = 0

    for symbol in symbol_data['symbols']:
        if symbol['quoteAsset'] == 'BTC':
            total_btc_coins += 1

    loops = 0
    for symbol in symbol_data['symbols']:

        if symbol['quoteAsset'] == 'BTC':
            loops += 1
            if (loops >= math.floor(total_btc_coins/12)*file_number and loops < math.floor(total_btc_coins/12)*(file_number+1)):
                ut.buy_coin_test(symbol['symbol'])


    #print('done')
