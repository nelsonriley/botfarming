#!/usr/bin/python2.7

import requests
from pprint import pprint
import numpy
import sys
import os
import datetime
import time
import utility as ut
import functions_financial as fn

def run_data_set(symbols, minutes, day, step_back, datapoints_trailing, price_to_buy_factor, price_to_sell_factor, price_to_sell_factor_2, price_to_sell_factor_3, minutes_until_sale, minutes_until_sale_2, minutes_until_sale_3, lower_band_buy_factor):

    # vars to return
    wins = 0
    losses = 0
    percentage_made_win = []
    percentage_made_loss = []

    if lower_band_buy_factor < 100:
        datapoints_trailing = 1

    for s in symbols:
        symbol = symbols[s]

        file_path = './binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz'
        data = ut.pickle_read(file_path)
        if isinstance(data, dict):
            print('ERROR... Data is misconfigured')
            print(file_path)
            pprint(data)
            return

        trailing_closes = []
        trailing_volumes = []
        trailing_movement = []
        trailing_lows = []
        trailing_highs = []

        first = True
        sale_time = 0
        for index, candle in enumerate(data):

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

            if index > datapoints_trailing:
                # Bollinger Schema
                # candles[i][12] = upper_band
                # candles[i][13] = middle_band
                # candles[i][14] = lower_band
                # candles[i][15] = stan_dev
                if lower_band_buy_factor < 100:
                    trailing_and_current_candles = data[index-datapoints_trailing:index]
                    trailing_and_current_candles, smart_trailing_candles = fn.add_bollinger_bands_to_candles(trailing_and_current_candles)
                    lower_band_for_index = trailing_and_current_candles[-1][14]
                    band_ok_value = lower_band_for_index * lower_band_buy_factor
                    band_ok = float(candle[3]) < band_ok_value
                else:
                    band_ok = True
                    band_ok_value = 99999

                price_to_buy_ok = float(candle[3]) < float(candle[1])*price_to_buy_factor

                do_buy = band_ok and price_to_buy_ok

                if do_buy:

                    buy_price = min(band_ok_value, float(candle[1])*price_to_buy_factor)

                    if minutes > 1:

                        minutes_into_future = 60
                        if minutes == 30:
                            minutes_into_future = 210

                        start_time_period = (candle[0])
                        end_time_period = start_time_period + 1*60*minutes_into_future*1000

                        sale_data_path = './binance_training_data/'+ day + '/sale_data_' + str(minutes) + 'm_'+ symbol['symbol'] +'_start_' + str(start_time_period) + '_end_' + str(end_time_period) +'.pklz'

                        data_for_sale = ut.pickle_read(sale_data_path)

                        # watch for bad saved data
                        if isinstance(data_for_sale, dict):
                            print('ERROR... Bad Data Saved. Deleting this file:')
                            print(sale_data_path)
                            pprint(data_for_sale)
                            os.remove(sale_data_path)
                            data_for_sale = False

                        if not data_for_sale:
                            print('getting one minute data', symbol['symbol'])
                            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval=1m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period)
                            data_for_sale = requests.get(url).json()

                            # watch for too many API requests
                            if isinstance(data_for_sale, dict):
                                print('ERROR... API Failed')
                                print(url)
                                pprint(data_for_sale)
                                return
                            ut.pickle_write(sale_data_path, data_for_sale, 'trying to save data for sale')

                        for index_for_sale in range(0, minutes+1):
                            if float(data_for_sale[index_for_sale][3]) < buy_price:
                                break

                        if index_for_sale == minutes:
                            print('should have found lower price earlier some weird error')

                        if len(data_for_sale) < 60:
                            continue

                    if minutes == 1:

                        data_for_sale = data
                        index_for_sale = index

                    #selling coin
                    sold_it = False
                    for i in range(1,minutes_until_sale):
                        if float(data_for_sale[index_for_sale + i][2]) > float(candle[1])*price_to_sell_factor:
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

                    percentage_made = (sale_price*.998-buy_price*1.002)/buy_price*1.002

                    sale_time = data_for_sale[sale_index][0]

                    if percentage_made > 0:
                        percentage_made_win.append(percentage_made)
                        wins += 1
                    else:
                        percentage_made_loss.append(percentage_made)
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

    return wins, losses, percentage_made_win, percentage_made_loss

################################################################################