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

minutes = 1
day = '20180122'
step_backs = 8

# get list of symbols
trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}
total_btc_coins = 0
symbols_trimmed = {}
symbols = ut.pickle_read('./binance_btc_symbols.pklz')
for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol


sell_price_drop_factor = .997
buy_price_increase_factor = 1.002
datapoints_trailing = 23
minutes_until_sale = 4
minutes_until_sale_2 = 12
minutes_until_sale_3 = 45

# save total gain for each param combination tested across all step backs
combined_results = {}


buy_price_levels = [.978]
sell_price_levels = range(0,3)
sell_price_levels[0] = [.994,.984,.965]

for step_back in range(0, 8):

    # track best params per step back
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

    for a in range(0, 1):
        #price_to_buy_factor_array[2] = .975 + .003*a
        for b in range(0, 1):
                buy_price_levels[0] = .978

                wins = 0
                losses = 0
                current_gain = 0

                current_movement_win = []
                current_movement_loss = []

                percentage_made_win = []
                percentage_made_loss = []


                for s in symbols_trimmed:
                    symbol = symbols_trimmed[s]

                    # get 1 min data
                    path = './binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz'
                    data = ut.pickle_read(path)
                    if not data:
                        continue

                    trailing_closes = []
                    trailing_volumes = []
                    trailing_movement = []
                    trailing_lows = []
                    trailing_highs = []

                    first = True
                    sale_time = 0
                    for index, candle in enumerate(data):

                        try:
                            gotdata = data[index + minutes_until_sale_3+1]
                        except IndexError:
                            break

                        # start triggering trades when enough history is available
                        if index > datapoints_trailing:

                            low_price = float(candle[3])
                            compare_price = float(candle[1])

                            buy_prices = []
                            sell_prices = []
                            for n in range(0, len(buy_price_levels)):
                                buy_price = compare_price * buy_price_levels[n]
                                if low_price < buy_price:
                                    buy_prices.append(buy_price)
                                    sell_prices_for_n = []
                                    for s in range(0,3):
                                        sell_prices_for_n.append(compare_price*sell_price_levels[n][s])
                                    sell_prices.append(sell_prices_for_n)

                            for p in range(0, len(buy_prices)):

                                buy_price = buy_prices[p]
                                sale_price = 0
                                sale_index = 0

                                #selling coin
                                sold_it = False
                                for i in range(1,minutes_until_sale):
                                    if float(data[index + i][2]) > sell_prices[p][0]:
                                        sale_price = sell_prices[p][0]
                                        sale_index = index + i
                                        sold_it = True
                                        break

                                if sold_it == False:
                                    for i in range(minutes_until_sale, minutes_until_sale_2):
                                        if float(data[index + i][2]) > sell_prices[p][1]:
                                            sale_price = sell_prices[p][1]
                                            sale_index = index + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    for i in range(minutes_until_sale_2, minutes_until_sale_3):
                                        if float(data[index + i][2]) > sell_prices[p][2]:
                                            sale_price = sell_prices[p][2]
                                            sale_index = index + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    sale_price = float(data[index + minutes_until_sale_3][4])*.98
                                    sale_index = index + minutes_until_sale_3


                                percentage_made = (sale_price*sell_price_drop_factor-buy_price*buy_price_increase_factor)/buy_price*buy_price_increase_factor

                                sale_time = data[sale_index][0]

                                if percentage_made > 0:
                                    #current_movement_win.append(current_movement_percentage)
                                    percentage_made_win.append(percentage_made)
                                    #print('win')
                                    wins += 1
                                else:
                                    #current_movement_loss.append(current_movement_percentage)
                                    percentage_made_loss.append(percentage_made)
                                    #print('loss')
                                    losses += 1

                        # update
                        if len(trailing_volumes) <= datapoints_trailing:
                            trailing_volumes.append(float(candle[5]))
                            trailing_movement.append(abs(float(candle[4])-float(candle[1])))
                            trailing_highs.append(float(candle[2]))
                            trailing_lows.append(float(candle[3]))
                            trailing_closes.append(float(candle[4]))
                        if len(trailing_volumes) > datapoints_trailing:
                            del trailing_volumes[0]
                            del trailing_movement[0]
                            del trailing_highs[0]
                            del trailing_lows[0]
                            del trailing_closes[0]



                current_gain = numpy.sum(percentage_made_win)+numpy.sum(percentage_made_loss)

                # the_key = str(price_to_buy_factor_array[look_back]) + '_' + str(price_to_sell_factor_array[look_back]) + '_' + str(lower_band_buy_factor_array[look_back])
                # if the_key in combined_results:
                #     combined_results[the_key] += current_gain
                # else:
                #     combined_results[the_key] = current_gain

                if current_gain > best_gain:
                    print("NEW BEST:")
                    best_gain = current_gain
                    best_minutes_until_sale = minutes_until_sale
                    best_minutes_until_sale_2 = minutes_until_sale_2
                    best_minutes_until_sale_3 = minutes_until_sale_3


                print("gain", current_gain)
                print('step_back', step_back)
                # print('lower_band_buy_factor', lower_band_buy_factor_array[look_back])
                # print('price_to_buy_factor, price to sell factors', price_to_buy_factor_array[look_back], price_to_sell_factor_array[look_back])
                # print('other price to sell factors', price_to_sell_factor_2_array[look_back], price_to_sell_factor_3_array[look_back])
                # print('minutes until sales', minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3)
                # print('BEST gain:', best_gain)
                # print('BEST lower_band_buy_factor', best_lower_band_buy_factor)
                # print('BEST price_to_buy_factor, price_to_sell_factor', best_price_to_buy_factor, best_price_to_sell_factor)
                # print('BEST other price to sell factors', best_price_to_sell_factor_2, best_price_to_sell_factor_3)
                # print('BEST minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)
                print('wins:',wins)
                print(numpy.mean(percentage_made_win))
                print('losses:',losses)
                print(numpy.mean(percentage_made_loss))
                if losses != 0:
                    print('wins/losses', wins/losses)
                print()

    print('###################################################################')
    print('BEST PARAMS for step_back =', step_back)
    print('gain:', best_gain)
    print('price_to_buy_factor', best_price_to_buy_factor)
    print('price_to_sell_factor', best_price_to_sell_factor)
    print('price_to_sell_factor_2', best_price_to_sell_factor_2)
    print('price_to_sell_factor_3', best_price_to_sell_factor_3)
    print('lower_band_buy_factor', best_lower_band_buy_factor)
    print('minutes_until_sale (1,2,3):', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)
    pprint(combined_results)
    print('###################################################################')

print('best price to sell factors', best_price_to_sell_factor, best_price_to_sell_factor_2, best_price_to_sell_factor_3)
print('best minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)

pprint(combined_results)
print('done')
