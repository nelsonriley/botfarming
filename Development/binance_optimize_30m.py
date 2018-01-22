#!/usr/bin/python2.7

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
import binance_optimization as optimize
import socket
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print('Computer Name:', hostname)
print('IP Address:', ip_address)

trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}

best_gain = 0
best_price_to_buy_factor = 0
best_bollingers_percentage_increase_factor = 0
best_lower_band_buy_factor = 0
best_price_to_sell_factor = 0
best_price_to_sell_factor_2 = 0
best_price_to_sell_factor_3 = 0
best_minutes_until_sale = 0
best_minutes_until_sale_2 = 0
best_minutes_until_sale_3 = 0

# Volume
volume_minimum = 450
symbols = ut.pickle_read('./binance_btc_symbols.pklz')
total_btc_coins = 0
symbols_trimmed = {}
for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > volume_minimum:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol

# Settings
minutes = 30
day = '20180118'
step_backs = 1
# Params
price_to_buy_factor = .90
price_to_sell_factor = .99
price_to_sell_factor_2 = 0.98
price_to_sell_factor_3 = 0.97 # 9.18
minutes_until_sale = 75 # 75, 115, 155 8.22       55, 80, 100  7.33
minutes_until_sale_2 = 115
minutes_until_sale_3 = 155
lower_band_buy_factor = 9999
datapoints_trailing = 1
############################################################################## Param Test Section
for a in range(0, 1):
    # price_to_buy_factor = round(.89 + .01 * a, 4)
    # lower_band_buy_factor = round(1.15 + .02 * a, 4)
    # minutes_until_sale = 75 + 5 * a
    # price_to_sell_factor_2_factor = round(0.98 + .01 * a, 3)
    for b in range(0, 1):
        # price_to_sell_factor = round(price_to_buy_factor + .07 + .01 * b, 4)
        # minutes_until_sale_2 = minutes_until_sale + 35 + 5 * b
        # minutes_until_sale_3 = minutes_until_sale_2 + 40
        # price_to_sell_factor_3_factor = round(0.98 + .01 * b, 3)
        # price_to_sell_factor_2 = round(price_to_sell_factor * price_to_sell_factor_2_factor, 3)
        # price_to_sell_factor_3 = round(price_to_sell_factor_2 * price_to_sell_factor_3_factor, 3)

        # Param Overrides go here

        gain_for_period = {}
        gain_for_period[0] = 0
        gain_for_period[1] = 0
        gain_for_period[2] = 0

        for step_back in range(0, step_backs):

            # run on all symbols
            wins, losses, percentage_made_win, percentage_made_loss = optimize.run_data_set(symbols_trimmed, minutes, day, step_back, datapoints_trailing, price_to_buy_factor, price_to_sell_factor, price_to_sell_factor_2, price_to_sell_factor_3, minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3, lower_band_buy_factor)

            current_gain = numpy.sum(percentage_made_win)+numpy.sum(percentage_made_loss)
            gain_for_period[step_back] += current_gain
            if current_gain > best_gain:
                print("NEW BEST:")
                best_gain = current_gain
                best_lower_band_buy_factor = lower_band_buy_factor
                best_price_to_buy_factor = price_to_buy_factor
                best_price_to_sell_factor = price_to_sell_factor
                best_price_to_sell_factor_2 = price_to_sell_factor_2
                best_price_to_sell_factor_3 = price_to_sell_factor_3
                best_minutes_until_sale = minutes_until_sale
                best_minutes_until_sale_2 = minutes_until_sale_2
                best_minutes_until_sale_3 = minutes_until_sale_3

            print("GAIN", current_gain)
            if (step_backs > 1):
                print('step_back', step_back)
            print('price_to_buy_factor', price_to_buy_factor)
            print('price_to_sell_factor', price_to_sell_factor)
            print('price_to_sell_factor_2', price_to_sell_factor_2)
            print('price_to_sell_factor_3', price_to_sell_factor_3)
            print('minutes_to_sales', minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3)
            print('lower_band_buy_factor', lower_band_buy_factor)
            print('BEST gain:', best_gain)
            print('BEST lower_band_buy_factor', best_lower_band_buy_factor)
            print('BEST price_to_buy_factor, price_to_sell_factor', best_price_to_buy_factor, best_price_to_sell_factor)
            print('BEST other price to sell factors', best_price_to_sell_factor_2, best_price_to_sell_factor_3)
            print('BEST minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)
            print('wins:',wins)
            print(numpy.mean(percentage_made_win))
            print('losses:',losses)
            print(numpy.mean(percentage_made_loss))
            if losses != 0:
                print('wins/losses', wins/losses)
            print('----------------------------------------')

        print('gain across periods:', gain_for_period[0]+gain_for_period[1]+gain_for_period[2])
        print()

print('best price to sell factors', best_price_to_sell_factor, best_price_to_sell_factor_2, best_price_to_sell_factor_3)
print('best minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)
print('done')
