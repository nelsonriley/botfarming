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

trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}


sell_price_drop_factor = .997
buy_price_increase_factor = 1.002

if minutes == 1:

    sell_price_drop_factor = .997
    buy_price_increase_factor = 1.002

    lower_band_buy_factor = 200
    price_to_buy_factor = .978
    datapoints_trailing = 23

    minutes_until_sale = 4
    minutes_until_sale_2 = 12
    minutes_until_sale_3 = 45
    price_to_sell_factor = .994
    price_to_sell_factor_2 = .984
    price_to_sell_factor_3 = .965


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



for a in range(0, 1):

    #price_to_buy_factor = round(.92 + .01*price_to_buy_factor, 4)
    for b in range(0, 1):
            #price_to_sell_factor = round(price_to_buy_factor + .025 + .005*price_to_sell_factor, 4)

            for step_back in range(0, 8):


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


                    data = ut.pickle_read('./binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz')

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

                        # if float(candle[0]) < float(sale_time):
                        #     continue

                        if minutes == 1:
                            try:
                                gotdata = data[index + minutes_until_sale_3+1]
                            except IndexError:
                                break

                        if minutes == 30:
                            try:
                                 gotdata = data[index + 1]
                            except IndexError:
                                 break

                        # compare
                        if index > datapoints_trailing:

                            if symbol['symbol'] == 'WTCBTC' and candle[0] == 1516680720000:
                                print('here')

                            #print(float(candle[3]), float(candle[1]), price_to_buy_factor)
                            if float(candle[3]) < float(candle[1])*price_to_buy_factor:

                                #print('buying..', symbol['symbol'])

                                buy_price = float(candle[1])*price_to_buy_factor


                                if minutes == 1:

                                    data_for_sale = data
                                    index_for_sale = index

                                #print('')
                                #print('bought ' + symbol['symbol'] + ' at', time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.gmtime(data_for_sale[index_for_sale][0]/1000)))

                                #selling coin
                                sold_it = False
                                for i in range(1,minutes_until_sale):
                                    if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor:
                                        if candle[0] == 1516680420000 and symbol['symbol'] == 'LENDBTC':
                                            print('here')
                                        sale_price = float(candle[1])*price_to_sell_factor
                                        sale_index = index_for_sale + i
                                        sold_it = True
                                        break

                                if sold_it == False:
                                    for i in range(minutes_until_sale, minutes_until_sale_2):
                                        if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor_2:
                                            sale_price = float(candle[1])*price_to_sell_factor_2
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    for i in range(minutes_until_sale_2, minutes_until_sale_3):
                                        if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor_3:
                                            sale_price = float(candle[1])*price_to_sell_factor_3
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                if sold_it == False:
                                    sale_price = float(data_for_sale[index_for_sale + minutes_until_sale_3][4])*.98
                                    sale_index = index_for_sale + minutes_until_sale_3

                                percentage_made = (sale_price*sell_price_drop_factor-buy_price*buy_price_increase_factor)/buy_price*buy_price_increase_factor

                                sale_time = data_for_sale[sale_index][0]
                                #print('sold at', ut.get_readable_time(sale_time/1000))
                                #print('percentage_made', percentage_made)

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


                print("gain", current_gain)
                print('step_back', step_back)
                print('lower_band_buy_factor', lower_band_buy_factor)
                print('price_to_buy_factor, price to sell factors', price_to_buy_factor, price_to_sell_factor)
                print('other price to sell factors', price_to_sell_factor_2, price_to_sell_factor_3)
                print('minutes until sales', minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3)
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
                print()

            print()


print('best price to sell factors', best_price_to_sell_factor, best_price_to_sell_factor_2, best_price_to_sell_factor_3)
print('best minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)

print('done')
