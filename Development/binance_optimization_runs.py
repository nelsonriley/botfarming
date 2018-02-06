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

print('starting..')

minutes = 1
day = '20180202_b'

step_backs = 1
continuous_mode = True
continous_length = 1
datapoints_trailing = 0
step_back = 0


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

#1.04

sell_price_drop_factor = .997
buy_price_increase_factor = 1.002

minutes_until_sale = 999999
minutes_until_sale_2 = 20
minutes_until_sale_3 = 45

price_to_sell_factor = .995
price_to_sell_factor_2 = .982
price_to_sell_factor_3 = .965


combined_results = {}

trades = {}
trades_started = {}

optimizing = 1
all_trades_count = 0
best_gain = -999999
optimal_buy_factor = 0
optimal_sell_factor = 0

optimizing_array= [2]
for optimizing in optimizing_array:
    for a in range(0,1):
        sell_drop_factor = .99 + .001*a

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

                    will_buy = False


                    look_back_schedule = [2]

                    for look_back in look_back_schedule:

                        drop_factor = .969
                        sell_factor = .993
                        rise_factor = 1.01
                        # sell_drop_factor = .997

                        compare_price = float(data[index-look_back][4])
                        buy_price = compare_price*drop_factor

                        if float(candle[3]) < buy_price:
                            will_buy = True
                            break


                    if will_buy:

                        buy_price = buy_price

                        try:
                            for i in range(1,minutes_until_sale):
                                sale_price = compare_price*.993
                                if float(data[index + i][2]) > sale_price:
                                    sale_index = index + i
                                    sold_it = True
                                    break
                        except IndexError:
                            print('could not sell', symbol['symbol'])
                            sale_price = float(data[index + i-1][4])
                            sale_index = index + i-1



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

        # end symbol_loop, calc results
        current_gain = numpy.sum(percentage_made_win)+numpy.sum(percentage_made_loss)


        if current_gain > best_gain:
            best_gain = current_gain
            print('###################NEW OPTIMAL')
            print('sell_drop_factor', sell_drop_factor)
            print('#############################')



        the_key = 'results'
        combined_results[the_key] = current_gain


        trades_count += wins + losses
        print('----------------------------------------------')
        print('trades_count', trades_count)
        print("gain", current_gain)
        print('sell_drop_factor', sell_drop_factor)
        print('wins:',wins)
        print(numpy.mean(percentage_made_win))
        print('losses:',losses)
        print(numpy.mean(percentage_made_loss))
        if losses != 0:
            print('wins/losses', wins/losses)
        print()



pprint(combined_results)