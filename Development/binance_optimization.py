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
import utility_2 as ut2
import functions_financial as fn

print('starting..')

minutes = 1
day = '20180122'
step_backs = 8
day = '20180126'
day = '20180126_a'
day = '20180126_b'
day = '20180127'
day = '20180130'
day = '20180130_a'
day = '20180130_b'
day = '20180131'
day = '20180131_b'
day = '20180201'
day = '20180201_a'
day = '20180201_c'
day = '20180202'

step_backs = 1
continuous_mode = True
continous_length = 1
step_back = 0
datapoints_trailing = 230
min_volume = 0
minutes = 1

# get previous 24 hours data
epoch_now = int(time.time())
epoch_24hrs_ago = epoch_now - 24*60*60
readable_time_now = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y-%m-%d %H:%M')
readable_time_24hrs_ago = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y-%m-%d %H:%M')
readable_time_now_folder = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y%m%d_%H:%M')
readable_time_24hrs_ago_folder = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y%m%d_%H:%M')
day = readable_time_24hrs_ago_folder + '_to_' + readable_time_now_folder
print('fetching previous 24hrs of data', day)
save_params = [
    [day, readable_time_24hrs_ago, readable_time_now]
]
ut2.save_data(save_params, datapoints_trailing, min_volume, minutes)

################################################################################ RUN OPTIMIZER

trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}

symbols = ut.pickle_read('./binance_btc_symbols.pklz')

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

price_to_buy_factor_array = [0,.977, .969, .973, .965, .962, .96, .958, .95, .956, .95]
price_to_sell_factor_array = [0,.995, .993, .987, .995, .992, .989, .991, .986, .986, .986]
price_to_sell_factor_2_array = [0,.982, .98, .984, .985, .984, .983, .982, .982, .982, .981]
price_to_sell_factor_3_array = [0,.965, .974, .965, .971, .965, .964, .964, .963, .963, .963]
lower_band_buy_factor_array = [0,1.01, 1.15, 1.09, 1.055, 1.09, 1.12, 1.15, 1.16, 1.19, 1.19]
minutes_until_sale_array = [0,6,6,4,6,4,4,4,4,4]
minutes_until_sale_2_array = [0,20,24,12,22,12,12,12,12,12]


minutes_until_sale_3 = 45

combined_results = {}

trades = {}
trades_started = {}

optimizing = 1
all_trades_count = 0
best_gain = -999999
optimal_buy_factor = 0
optimal_sell_factor = 0

optimizing_array= [2,4,1]

for look_back in optimizing_array:
    look_back_optimized = ut.pickle_read('./optimization_factors/optimal_for_' + str(look_back) + '.pklz')
    price_to_buy_factor_array[look_back] = look_back_optimized[1]
    price_to_sell_factor_array[look_back] = look_back_optimized[2]
    price_to_sell_factor_2_array[look_back] = look_back_optimized[3]
    price_to_sell_factor_3_array[look_back] = look_back_optimized[4]
    minutes_until_sale_array[look_back] = look_back_optimized[5]
    minutes_until_sale_2_array[look_back] = look_back_optimized[6]
    lower_band_buy_factor_array[look_back] = look_back_optimized[7]


for optimizing in optimizing_array:

    best_gain = -999999
    optimal_buy_factor = price_to_buy_factor_array[optimizing]
    optimal_sell_factor = price_to_sell_factor_array[optimizing]
    optimal_band_factor = lower_band_buy_factor_array[optimizing]
    optimal_minutes_until_sale = minutes_until_sale_array[optimizing]
    optimal_minutes_until_sale_2 = minutes_until_sale_2_array[optimizing]
    optimal_sell_factor_2 = price_to_sell_factor_2_array[optimizing]
    optimal_sell_factor_3 = price_to_sell_factor_3_array[optimizing]


    #for iteration in range(0,2):
    for iteration in range(0,7):
        print('##################################### New Iteration', iteration, '###########')
        print('optimizing:', optimizing ,'optimal_buy_factor, optimal_sell_factor, optimal_band_factor,', optimal_buy_factor, optimal_sell_factor, optimal_band_factor)
        print('minutes_until_sale, minutes_until_sale_2', optimal_minutes_until_sale, optimal_minutes_until_sale_2)
        print('optimal_sell_factor_2, optimal_sell_factor_3', optimal_sell_factor_2, optimal_sell_factor_3)
        print('##################################### New Iteration', iteration, '###########')

        price_to_buy_factor_array[optimizing] = optimal_buy_factor
        price_to_sell_factor_array[optimizing] = optimal_sell_factor
        lower_band_buy_factor_array[optimizing] = optimal_band_factor
        minutes_until_sale_array[optimizing] = optimal_minutes_until_sale
        minutes_until_sale_2_array[optimizing] = optimal_minutes_until_sale_2
        price_to_sell_factor_2_array[optimizing] = optimal_sell_factor_2
        price_to_sell_factor_3_array[optimizing] = optimal_sell_factor_3

        if iteration == 0:
            a_range = 3
            b_range = 3
            change_size = .002
            starting_buy_factor =  optimal_buy_factor - change_size
            starting_sell_factor = optimal_sell_factor - change_size
        elif iteration == 1 or iteration == 4:
            a_range = 3
            b_range = 3
            change_size = .001
            starting_buy_factor =  optimal_buy_factor - change_size
            starting_sell_factor = optimal_sell_factor - change_size
        elif iteration == 2:
            a_range = 1
            b_range = 7
            change_size = .015
            starting_band = optimal_band_factor - .045
        elif iteration == 3 or iteration == 6:
            starting_minutes_until_sale = optimal_minutes_until_sale - 2
            starting_minutes_until_sale_2 = optimal_minutes_until_sale_2 - 4
            a_range = 3
            b_range = 3
        elif iteration == 5:
            starting_sell_factor_2 = optimal_sell_factor_2 - .003
            starting_sell_factor_3 = optimal_sell_factor_3 - .003
            a_range = 4
            b_range = 4


        for a in range(0, a_range):
            if iteration == 0 or iteration == 1 or iteration == 4:
                price_to_buy_factor_array[optimizing] = starting_buy_factor + change_size*a
            elif iteration == 3 or iteration == 6:
                minutes_until_sale_array[optimizing] = starting_minutes_until_sale + a*2
            elif iteration == 5:
                price_to_sell_factor_3_array[optimizing] = starting_sell_factor_3 + .002*a

            for b in range(0, b_range):
                if iteration == 0 or iteration == 1 or iteration == 4:
                    price_to_sell_factor_array[optimizing] = starting_sell_factor + change_size*b
                elif iteration == 2:
                    lower_band_buy_factor_array[optimizing] = starting_band + change_size*b
                elif iteration == 3 or iteration == 6:
                    minutes_until_sale_2_array[optimizing] = starting_minutes_until_sale_2 + b*4
                elif iteration == 5:
                    price_to_sell_factor_2_array[optimizing] = starting_sell_factor_2 + .002*b

                #minutes_until_sale = 2

                #print('********', minutes_until_sale_2_array[optimizing])

                if minutes_until_sale_array[optimizing] >= minutes_until_sale_2_array[optimizing] or minutes_until_sale_array[optimizing] < 2:
                    continue

                trades_count = 0

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

                    if continuous_mode:
                        data = ut.pickle_read('./binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m.pklz')
                        if data == False:
                            print('no data for symbol', symbol['symbol'])
                            continue
                        continous_length = len(data)
                    else:
                        data = ut.pickle_read('./binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz')

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
                    for index, candle in enumerate(data):

                        #print(symbol['symbol'])

                        # prevent bots buying at same time
                        if float(candle[0]) < float(sale_time):
                            continue

                        #**cuts approx 45 min off whatever data is made available
                        try:
                            gotdata = data[index + minutes_until_sale_3+1]
                        except IndexError:
                            break

                        # compare
                        if index > datapoints_trailing:

                            # if symbol['symbol'] == 'ETHBTC':
                            #     print('---------------------->', ut.get_readable_time(candle[0]/1000))

                            will_buy = False

                            #look back schedule 2,1,4 or 2,4,1
                            look_back_schedule = [2,4,1]
                            #look_back_schedule = [6,1,8,10,9,4,5,2,7,3]

                            current_look_back = 0
                            for look_back in look_back_schedule:

                                compare_price = float(data[index-look_back][4])
                                buy_price = compare_price*price_to_buy_factor_array[look_back]

                                if float(candle[3]) < buy_price:

                                    # print('symbol,', symbol['symbol'])

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
                                        current_look_back = look_back
                                        break

                            if will_buy:

                                if lower_band_buy_factor_array[look_back] < 100:
                                    buy_price = min(band_ok_value,buy_price)
                                else:
                                    buy_price = buy_price

                                data_for_sale = data
                                index_for_sale = index

                                trades_started[ut.get_readable_time(candle[0]/1000)] = [symbol['symbol'], look_back, buy_price]

                                #selling coin
                                sold_it = False

                                try:
                                    gotdata = data[index + minutes_until_sale_array[look_back]+1]
                                except IndexError:
                                    print('no data for sale_1', symbol['symbol'])
                                    break

                                for i in range(1,minutes_until_sale_array[look_back]):
                                    sale_price = compare_price*price_to_sell_factor_array[look_back]
                                    if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                        sale_index = index_for_sale + i
                                        sold_it = True
                                        break

                                if sold_it == False:
                                    try:
                                        gotdata = data[index + minutes_until_sale_2_array[look_back]+1]
                                    except IndexError:
                                        print('no data for sale_2', symbol['symbol'])
                                        break
                                    for i in range(minutes_until_sale_array[look_back], minutes_until_sale_2_array[look_back]):
                                        sale_price = compare_price*price_to_sell_factor_2_array[look_back]
                                        if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    try:
                                        gotdata = data[index + minutes_until_sale_3+1]
                                    except IndexError:
                                        print('no data for sale_3', symbol['symbol'])
                                        break
                                    for i in range(minutes_until_sale_2_array[look_back], minutes_until_sale_3):
                                        sale_price = compare_price*price_to_sell_factor_3_array[look_back]
                                        if float(data_for_sale[index_for_sale + i][2]) > sale_price:
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    sale_price = float(data_for_sale[index_for_sale + minutes_until_sale_3][4])*.98
                                    sale_index = index_for_sale + minutes_until_sale_3


                                percentage_made = (sale_price*sell_price_drop_factor-buy_price*buy_price_increase_factor)/buy_price*buy_price_increase_factor

                                sale_time = data_for_sale[sale_index][0]

                                ####### so far this seems to be an improvement, need to test again tomorrow, then put live if good
                                # if percentage_made < -.012:
                                #       sale_time += 2*60*60*1000



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

                # end symbol_loop, calc results
                current_gain = numpy.sum(percentage_made_win)+numpy.sum(percentage_made_loss)


                if current_gain > best_gain:
                    best_gain = current_gain
                    optimal_buy_factor = price_to_buy_factor_array[optimizing]
                    optimal_sell_factor = price_to_sell_factor_array[optimizing]
                    optimal_band_factor = lower_band_buy_factor_array[optimizing]
                    optimal_minutes_until_sale = minutes_until_sale_array[optimizing]
                    optimal_minutes_until_sale_2 = minutes_until_sale_2_array[optimizing]
                    optimal_sell_factor_2 = price_to_sell_factor_2_array[optimizing]
                    optimal_sell_factor_3 = price_to_sell_factor_3_array[optimizing]
                    print('###################NEW OPTIMAL for ', optimizing ,' optimal_buy_factor, optimal_sell_factor', optimal_buy_factor, optimal_sell_factor, optimal_band_factor)
                    print('###################NEW OPTIMAL for ', optimizing ,' optimal_minutes_until_sale, optimal_minutes_until_sale_2', optimal_minutes_until_sale, optimal_minutes_until_sale_2)
                    print('###################NEW OPTIMAL for ', optimizing ,' optimal_sell_factor_2, optimal_sell_factor_3', optimal_sell_factor_2, optimal_sell_factor_3)


                the_key = str(price_to_buy_factor_array[optimizing]) + '_' + str(price_to_sell_factor_array[optimizing]) + '_' + str(lower_band_buy_factor_array[optimizing])
                combined_results[the_key] = current_gain


                trades_count += wins + losses
                print('----------------------------------------------')
                print('trades_count', trades_count)
                print("gain", current_gain)
                print('step_back', step_back)
                print('lower_band_buy_factor', lower_band_buy_factor_array[optimizing])
                print('price_to_buy_factor, price to sell factors', price_to_buy_factor_array[optimizing], price_to_sell_factor_array[optimizing])
                print('other price to sell factors', price_to_sell_factor_2_array[optimizing], price_to_sell_factor_3_array[optimizing])
                print('minutes until sales', minutes_until_sale_array[optimizing], minutes_until_sale_2_array[optimizing], minutes_until_sale_3)
                print('wins:',wins)
                print(numpy.mean(percentage_made_win))
                print('losses:',losses)
                print(numpy.mean(percentage_made_loss))
                if losses != 0:
                    print('wins/losses', wins/losses)
                print()

    price_to_buy_factor_array[optimizing] = optimal_buy_factor
    price_to_sell_factor_array[optimizing] = optimal_sell_factor
    lower_band_buy_factor_array[optimizing] = optimal_band_factor
    minutes_until_sale_array[optimizing] = optimal_minutes_until_sale
    minutes_until_sale_2_array[optimizing] = optimal_minutes_until_sale_2
    price_to_sell_factor_2_array[optimizing] = optimal_sell_factor_2
    price_to_sell_factor_3_array[optimizing] = optimal_sell_factor_3
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')
    print('results for', optimizing,'optimal buy, optimal sell, optimal band,', optimal_buy_factor, optimal_sell_factor,optimal_band_factor)
    print('optimal minutes, optimal minutes 2', optimal_minutes_until_sale, optimal_minutes_until_sale_2)
    print('optimal sell 2, optimal sell 3', optimal_sell_factor_2, optimal_sell_factor_3)
    optimization_factors = [optimizing, optimal_buy_factor, optimal_sell_factor, optimal_sell_factor_2, optimal_sell_factor_3, optimal_minutes_until_sale, optimal_minutes_until_sale_2, optimal_band_factor]
    ut.pickle_write('./optimization_factors/optimal_for_' + str(optimizing) + '.pklz', optimization_factors)
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')
    print('###################################################################')


print('optimal_buy_factor,optimal_sell_factor, optimal_band_factor', optimal_buy_factor, optimal_sell_factor, optimal_band_factor)
pprint(combined_results)