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

def pickle_read(file_path):
    f = gzip.open(file_path,'rb')
    data = pickle.load(f)
    f.close()
    return data

def pickle_write(file_path, data, error_message='pickle could not write'):
    try:
        f = gzip.open(file_path,'wb')
        pickle.dump(data,f)
        f.close()
    except Exception as e:
        print(e)
        print(error_message)


symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()


step_back = 0
minutes = 1
day = '20180116'

trailing_and_current_candles_array = {}
smart_trailing_candles_array = {}


if minutes == 1:

    final_sale_factor = 1.005

    trail_vol_min = 1000
    lower_band_buy_factor = .984
    price_to_buy_factor = .977
    bollingers_percentage_increase_factor = -.006
    datapoints_trailing = 22

    minutes_until_sale = 4
    minutes_until_sale_2 = 12
    minutes_until_sale_3 = 45
    price_to_sell_factor = .988
    price_to_sell_factor_2 = .981
    price_to_sell_factor_3 = .9625



if minutes == 30:

    trail_vol_min = 600
    price_to_buy_factor = .92
    datapoints_trailing = 22
    max_trailing_slope = .01

    minutes_until_sale = 2
    minutes_until_sale_2 = 9
    minutes_until_sale_3 = 100
    price_to_sell_factor = .999
    price_to_sell_factor_2 = .981
    price_to_sell_factor_3 = .974


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

for step_back in range(1, 3):
            for price_to_sell_factor_2 in range(0, 1):
                price_to_sell_factor_2 = round(.988 + .002*price_to_sell_factor_2, 4)



    # for price_to_sell_factor in range(0, 1):
    #     price_to_sell_factor = round(.988 + .001*price_to_sell_factor, 4)
    #     for lower_band_buy_factor in range(0, 1):
    #         lower_band_buy_factor = round(.984 + .002*lower_band_buy_factor,4)
    #         for price_to_buy_factor in range(0, 1):
    #             price_to_buy_factor = round(.977 + .002*price_to_buy_factor, 4)


                trail_vol_min = 1000
                lower_band_buy_factor = .984
                price_to_buy_factor = .977
                bollingers_percentage_increase_factor = -.006

                minutes_until_sale = 4
                minutes_until_sale_2 = 12
                minutes_until_sale_3 = 45
                price_to_sell_factor = .988
                price_to_sell_factor_2 = .981
                price_to_sell_factor_3 = .960


                #if minutes == 1:
            # if minutes_until_sale_2 <= minutes_until_sale or minutes_until_sale_3 <= minutes_until_sale or minutes_until_sale_3 <= minutes_until_sale_2:
            #     continue

                wins = 0
                losses = 0
                current_gain = 0

                current_movement_win = []
                current_movement_loss = []

                percentage_made_win = []
                percentage_made_loss = []


                #pprint(symbol_data)
                #symbol_data['symbols'] = [{'quoteAsset': 'BTC', 'symbol': 'SNGLSBTC'}]
                for symbol in symbol_data['symbols']:
                    if symbol['quoteAsset'] == 'BTC':
                        #and symbol['symbol'] == 'SNGLSBTC':

                        try:
                            if minutes == 30:
                                f = gzip.open('./binance_training_data/30m_20180114_0000_to_1900/'+ symbol['symbol'] +'.pklz','rb')
                                #f = gzip.open('./binance_training_data/'+ day +'/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz','rb')
                            if minutes == 1:
                                #print './binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz'
                                data = ut.pickle_read('./binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz')


                        except Exception as e:
                            #print('error with coin:')
                            continue

                        trailing_closes = []
                        trailing_volumes = []
                        trailing_movement = []
                        trailing_lows = []
                        trailing_highs = []


                        first = True
                        sale_time = 0
                        for index,candle in enumerate(data):

                            if float(candle[0]) < float(sale_time):
                                continue

                            if minutes == 1:
                                try:
                                    gotdata = data[index + minutes_until_sale_3+5]
                                except IndexError:
                                    break

                            if minutes == 30:
                                try:
                                     gotdata = data[index + 1]
                                except IndexError:
                                     break

                            # compare
                            if index > datapoints_trailing:
                                # if symbol['symbol'] == 'MTHBTC':
                                #     print('mean trailing volume', numpy.mean(trailing_volumes))


                                #get bollinger data
                                # if symbol['symbol'] + '_' + str(candle[0]) in trailing_and_current_candles_array.keys():
                                #
                                #     trailing_and_current_candles = trailing_and_current_candles_array[symbol['symbol'] + '_' + str(candle[0])]
                                #     smart_trailing_candles = smart_trailing_candles_array[symbol['symbol'] + '_' + str(candle[0])]
                                # else:
                                #     trailing_and_current_candles = data[index-datapoints_trailing:index]
                                #     trailing_and_current_candles, smart_trailing_candles = fn.add_bollinger_bands_to_candles(trailing_and_current_candles)
                                #     trailing_and_current_candles_array[symbol['symbol'] + '_' + str(candle[0])] = trailing_and_current_candles
                                #     smart_trailing_candles_array[symbol['symbol'] + '_' + str(candle[0])] = smart_trailing_candles

                                trailing_and_current_candles = data[index-datapoints_trailing:index]
                                trailing_and_current_candles, smart_trailing_candles = fn.add_bollinger_bands_to_candles(trailing_and_current_candles)


                                bollingers_percentage_increase = (trailing_and_current_candles[-1][14] - trailing_and_current_candles[-2][14])/trailing_and_current_candles[-2][14]
                                lower_band_for_index = trailing_and_current_candles[-1][14]

                                band_ok = float(candle[3]) < lower_band_for_index*lower_band_buy_factor
                                bollinger_increase_ok = bollingers_percentage_increase > bollingers_percentage_increase_factor
                                price_to_buy_ok = float(candle[3]) < float(candle[1])*price_to_buy_factor
                                trailing_vol_ok = numpy.mean(trailing_volumes) > trail_vol_min

                                will_buy = band_ok and bollinger_increase_ok and price_to_buy_ok and trailing_vol_ok
                                #will_buy = float(candle[3]) < float(candle[1])*price_to_buy_factor
                                #and numpy.mean(trailing_volumes) > trail_vol_min
                                #and numpy.mean(trailing_closes) < price_lower_previous_factor*float(candle[1])*price_to_buy_factor

                                if will_buy:

                                    #print('index, middle_for_index, lower_for_index, low for index, time', index, middle_band_for_index, lower_band_for_index, candle[3], ut.get_readable_time(candle[0]/1000))


                                    #print('buying..', symbol['symbol'])

                                    #buy_price = float(candle[1])*price_to_buy_factor
                                    buy_price = min(lower_band_for_index*lower_band_buy_factor,float(candle[1])*price_to_buy_factor)

                                    if minutes == 30:

                                        start_time_period = (candle[0])
                                        end_time_period = start_time_period + 3*60*60*1000

                                        sale_data_path = './binance_training_data/'+ day + '/sale_data_' + str(minutes) + 'm_'+ symbol['symbol'] +'_start_' + str(start_time_period) + '_end_' + str(end_time_period) +'.pklz'

                                        try:
                                            data_for_sale = pickle_read(sale_data_path)
                                        except Exception as e:
                                            print('getting one minute data', symbol['symbol'])
                                            r = requests.get('https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval=1m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period))
                                            data_for_sale = r.json()
                                            pickle_write(sale_data_path, data_for_sale, 'trying to save data for sale')


                                        for index_for_sale in range(0, 31):
                                            if float(data_for_sale[index_for_sale][3]) < buy_price:
                                                break

                                        if index_for_sale == 30:
                                            print('should have found lower price earlier some wierd error')

                                        if len(data_for_sale) < 120:
                                            continue


                                    if minutes == 1:

                                        data_for_sale = data
                                        index_for_sale = index

                                    #print('')
                                    #print('bought ' + symbol['symbol'] + ' at', time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.gmtime(data_for_sale[index_for_sale][0]/1000)))

                                    #selling coin
                                    sold_it = False
                                    for i in range(1,minutes_until_sale):
                                        if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor*final_sale_factor:
                                            sale_price = float(candle[1])*price_to_sell_factor
                                            sale_index = index_for_sale + i
                                            sold_it = True
                                            break

                                    if sold_it == False:
                                        for i in range(minutes_until_sale, minutes_until_sale_2):

                                            if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor_2*final_sale_factor:
                                                sale_price = float(candle[1])*price_to_sell_factor_2
                                                sale_index = index_for_sale + i
                                                sold_it = True
                                                break

                                    if sold_it == False:
                                        for i in range(minutes_until_sale_2, minutes_until_sale_3):

                                            if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor_3*final_sale_factor:
                                                sale_price = float(candle[1])*price_to_sell_factor_3
                                                sale_index = index_for_sale + i
                                                sold_it = True
                                                break

                                    if sold_it == False:
                                        sale_price = float(data_for_sale[index_for_sale + minutes_until_sale_3][4])*.98
                                        sale_index = index_for_sale + minutes_until_sale_3

                                    percentage_made = (sale_price-buy_price)/buy_price

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
                    best_bollingers_percentage_increase_factor = bollingers_percentage_increase_factor
                    best_price_to_buy_factor = price_to_buy_factor
                    best_price_to_sell_factor = price_to_sell_factor
                    best_price_to_sell_factor_2 = price_to_sell_factor_2
                    best_price_to_sell_factor_3 = price_to_sell_factor_3
                    best_minutes_until_sale = minutes_until_sale
                    best_minutes_until_sale_2 = minutes_until_sale_2
                    best_minutes_until_sale_3 = minutes_until_sale_3


                print("gain", current_gain)
                print('step_back', step_back)
                print('price to sell factors', price_to_sell_factor, price_to_sell_factor_2, price_to_sell_factor_3)
                print('minutes until sales', minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3)
                print('lower_band_buy_factor, bollingers_percentage_increase_factor, price_to_buy_factor', lower_band_buy_factor, bollingers_percentage_increase_factor, price_to_buy_factor)
                print('datapoints_trailing', datapoints_trailing)
                print('BEST gain:', best_gain)
                print('BEST lower_band_buy_factor, bollingers_percentage_increase_factor, price_to_buy_factor', best_lower_band_buy_factor, best_bollingers_percentage_increase_factor, best_price_to_buy_factor)
                print('BEST price to sell factors', best_price_to_sell_factor, best_price_to_sell_factor_2, best_price_to_sell_factor_3)
                print('BEST minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)
                print('wins:',wins)
                print(numpy.mean(percentage_made_win))
                print('losses:',losses)
                print(numpy.mean(percentage_made_loss))
                if losses != 0:
                    print('wins/losses', wins/losses)
                print()



print('best price to sell factors', best_price_to_sell_factor, best_price_to_sell_factor_2, best_price_to_sell_factor_3)
print('best minutes until sales', best_minutes_until_sale, best_minutes_until_sale_2, best_minutes_until_sale_3)

print('done')
