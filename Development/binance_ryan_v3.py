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
# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())


minutes = 1
day = '20180122'
step_backs = 8




trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}

symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')

total_btc_coins = 0
symbols_trimmed = {}

for s in symbols:
    symbol = symbols[s]
    if float(symbol['24hourVolume']) > 450:
        total_btc_coins += 1
        symbols_trimmed[s] = symbol


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

#1.04

sell_price_drop_factor = .997
buy_price_increase_factor = 1.002

price_to_buy_factor_array = [0,.978, .976, .974, .972, .969, .966, .963, .96, .957, .961]
price_to_sell_factor_array = [0,.994, .993, .992, .991, .989, .989, .988, .987, .986, .991]
price_to_sell_factor_2_array = [0,.984, .984, .984, .983, .984, .983, .982, .982, .982, .981]
price_to_sell_factor_3_array = [0,.965, .965, .965, .965, .965, .964, .964, .963, .963, .963]
lower_band_buy_factor_array = [0,1.04, 1.07, 1.09, 1.11, 1.14, 1.16, 1.18, 1.2, 1.22, 200]

datapoints_trailing = 45

minutes_until_sale = 4
minutes_until_sale_2 = 12
minutes_until_sale_3 = 45

combined_results = {}

#7 best = 0.954, 0.986, 1.10
#  '0.956_0.986_1.19': 0.63213434907428168   DONE
look_backs = 9
datapoints_trailing = 22*look_backs
a_options = 1
b_options = 5
combinations_tested = a_options * b_options
seconds_per_combination = 27
print(combinations_tested, 'combinations to be tested')
print('estimated time:', round(combinations_tested * seconds_per_combination / 60, 2), 'minutes')
for step_back in range(0, 8):
    for a in range(0, a_options):
        #price_to_buy_factor_array[look_backs] = .956 + .002*a
        price_to_buy_factor_array[look_backs] = .956

        for b in range(0, b_options):
                #price_to_sell_factor_array[look_backs] = .986 + .001*b
                price_to_sell_factor_array[look_backs] = 0.986

                lower_band_buy_factor_array[look_backs] = 1.16 + .01*b
                # lower_band_buy_factor_array[look_backs] = 1.10

                wins = 0
                losses = 0
                current_gain = 0

                current_movement_win = []
                current_movement_loss = []

                percentage_made_win = []
                percentage_made_loss = []


                #pprint(symbol_data)
                #symbol_data['symbols'] = [{'quoteAsset': 'BTC', 'symbol': 'SNGLSBTC'}]
                for s in symbols_trimmed:
                    symbol = symbols_trimmed[s]

                    data = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz')

                    # if data != False:
                    #     print(path)
                    if not data:
                        continue

                    trailing_closes = []
                    trailing_volumes = []
                    trailing_movement = []
                    trailing_lows = []
                    trailing_highs = []


                    first = True
                    sale_time = 0
                    for index,candle in enumerate(data):

                        #print(symbol['symbol'])

                        #if float(candle[0]) < float(sale_time):
                        #    continue

                        try:
                            gotdata = data[index + minutes_until_sale_3+1]
                        except IndexError:
                            break

                        # compare
                        if index > datapoints_trailing:

                            will_buy = False
                            for look_back in range(10-look_backs, 11-look_backs):
                                look_back = 10 - look_back

                                compare_price = float(data[index-look_back+1][1])
                                buy_price = compare_price*price_to_buy_factor_array[look_back]

                                if float(candle[3]) < buy_price:

                                    #print('symbol,', symbol['symbol'])


                                    if lower_band_buy_factor_array[look_back] < 100:
                                        candles_for_look_back = fn.get_n_minute_candles(look_back, data[index-22*look_back-1:index])
                                        candles_for_look_back, smart_trailing_candles = fn.add_bollinger_bands_to_candles(candles_for_look_back)
                                        lower_band_for_index = candles_for_look_back[-1][14]
                                        #print('lower_band_for_index', lower_band_for_index)
                                        band_ok_value = lower_band_for_index*lower_band_buy_factor_array[look_back]
                                        band_ok = float(candle[3]) < band_ok_value
                                    else:
                                        band_ok = True

                                    if band_ok:
                                        #print(symbol['symbol'])
                                        will_buy = True
                                        break

                            if will_buy:

                                if lower_band_buy_factor_array[look_back] < 100:
                                    buy_price = min(band_ok_value,buy_price)
                                else:
                                    buy_price = buy_price

                                data_for_sale = data
                                index_for_sale = index

                                #selling coin
                                sold_it = False
                                for i in range(1,minutes_until_sale):
                                    sale_price = compare_price*price_to_sell_factor_array[look_back]
                                    if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                        sale_index = index_for_sale + i
                                        sold_it = True
                                        break

                                if sold_it == False:
                                    for i in range(minutes_until_sale, minutes_until_sale_2):
                                        sale_price = compare_price*price_to_sell_factor_2_array[look_back]
                                        if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    for i in range(minutes_until_sale_2, minutes_until_sale_3):
                                        sale_price = compare_price*price_to_sell_factor_3_array[look_back]
                                        if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    sale_price = float(data_for_sale[index_for_sale + minutes_until_sale_3][4])*.98
                                    sale_index = index_for_sale + minutes_until_sale_3


                                percentage_made = (sale_price*sell_price_drop_factor-buy_price*buy_price_increase_factor)/buy_price*buy_price_increase_factor

                                #print('symbol, sale price, buy price, percentage made', symbol['symbol'], buy_price, sale_price, percentage_made)

                                sale_time = data_for_sale[sale_index][0]

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

                the_key = str(price_to_buy_factor_array[look_back]) + '_' + str(price_to_sell_factor_array[look_back]) + '_' + str(lower_band_buy_factor_array[look_back])
                if the_key in combined_results:
                    combined_results[the_key] += current_gain
                else:
                    combined_results[the_key] = current_gain


                print("gain", current_gain)
                print('step_back', step_back)
                print('lower_band_buy_factor', lower_band_buy_factor_array[look_back])
                print('price_to_buy_factor, price to sell factors', price_to_buy_factor_array[look_back], price_to_sell_factor_array[look_back])
                print('other price to sell factors', price_to_sell_factor_2_array[look_back], price_to_sell_factor_3_array[look_back])
                print('minutes until sales', minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3)
                print('wins:',wins)
                print(numpy.mean(percentage_made_win))
                print('losses:',losses)
                print(numpy.mean(percentage_made_loss))
                if losses != 0:
                    print('wins/losses', wins/losses)
                print()

pprint(combined_results)
fn.print_ascii()
# end
print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
elapsed = int(time.time()) - start_time
print('elapsed:', elapsed, 'seconds')
combinations_tested = a_options * b_options
print(combinations_tested, 'combinations tested')
print(round(elapsed/combinations_tested, 2), 'seconds per combination')