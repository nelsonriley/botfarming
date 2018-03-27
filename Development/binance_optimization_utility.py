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
import utility_3 as ut
import functions_financial as fn
import os


def run_optimizer(length, minutes, max_price_to_buy_factor, buy_sell_starting_gap, minutes_until_sale, minutes_until_sale_3, default_change_size_1, default_change_size_2):

    if length == '1m':
        max_price_to_buy_factor = .98
    if length == '5m':
        max_price_to_buy_factor = .96
    if length == '15m':
        max_price_to_buy_factor = .945
    if length == '30m':
        max_price_to_buy_factor = .93
    if length == '1h':
        max_price_to_buy_factor = .9
    if length == '2h':
        max_price_to_buy_factor = .87
    if length == '6h':
        max_price_to_buy_factor = .83
    if length == '12h':
        max_price_to_buy_factor = .8
    if length == '1d':
        max_price_to_buy_factor = .75
    
    
    while True:
    
        print('starting..')
        
        ################################################################################ RUN OPTIMIZER
        
        symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
        
        total_btc_coins = 0
        symbols_trimmed = {}
        
        for s in symbols:
            symbol = symbols[s]
            if float(symbol['24hourVolume']) > 300:
                total_btc_coins += 1
                symbols_trimmed[s] = symbol
        
        optimizing_array= [1,3,5,7,9,11,13,15]
        
        
        symbols_started = 0
        for s in symbols_trimmed:
            symbols_started += 1
            print('total symbols', total_btc_coins, 'symbols started: ', symbols_started)
            
            symbol = symbols_trimmed[s]
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print('starting', symbol['symbol'])
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            
            #Get Data
            symbols_trimmed_one = {}
            for s_one in symbols:
                symbol_one = symbols[s_one]
                if symbol_one['symbol'] == symbol['symbol']:
                    symbols_trimmed_one[s] = symbol_one
            
            continuous_mode = True
            continous_length = 1
            datapoints_trailing = 7
            min_volume = 0
            
            epoch_now = int(time.time())
            #Let's get 2600 minutes ago
            epoch_24hrs_ago = epoch_now - 360*minutes*60
            readable_time_now = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y-%m-%d %H:%M')
            readable_time_24hrs_ago = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y-%m-%d %H:%M')
            readable_time_now_folder = datetime.datetime.fromtimestamp(epoch_now-7*60*60).strftime('%Y%m%d_%H:%M')
            readable_time_24hrs_ago_folder = datetime.datetime.fromtimestamp(epoch_24hrs_ago-7*60*60).strftime('%Y%m%d_%H:%M')
            day = readable_time_24hrs_ago_folder + '_to_' + readable_time_now_folder
            print('fetching previous 24hrs of data', day)
            save_params = [
                [day, readable_time_24hrs_ago, readable_time_now]
            ]
            ut.save_data(save_params, datapoints_trailing, min_volume, minutes, symbols_trimmed_one)
        
           
            for optimizing in optimizing_array:
                
                lowest_buy_factor = 1
            
                print('##################################### New LOOK_BACK', optimizing, '###########', symbol['symbol'], 'total symbols', total_btc_coins, 'symbols started: ', symbols_started)
                    
                data = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ symbol['symbol'] +'_data_'+str(minutes)+'m.pklz')
                if data == False:
                    print('no data for symbol', symbol['symbol'])
                    continue
                continous_length = len(data)
                
                # if data != False:
                #     print(path)
                if not data:
                    continue

                for index, candle in enumerate(data):

                    try:
                        if optimizing == 1:
                            total_of_prices = 6*float(data[index-1][4])+2*float(data[index-2][4])+float(data[index-3][4])
                            total_counts_of_prices = 9
                        else:
                            for x in range(1,optimizing+1):
                                total_of_prices += float(data[index-x][4])*x**2
                                total_counts_of_prices += x**2
                            
                            for x in range(1,optimizing):
                                total_of_prices += float(data[index-2*optimizing+x][4])*x**2
                                total_counts_of_prices += x**2
                    except Exception as e:
                        print(e)
                        continue  
                    
                    compare_price = float(total_of_prices)/float(total_counts_of_prices)
                            
                    buy_price = compare_price*max_price_to_buy_factor

                    if float(candle[3]) < buy_price:
                                
                        low_buy_factor = float(candle[3])/compare_price
                        
                        if low_buy_factor < lowest_buy_factor:
                            lowest_buy_factor = low_buy_factor

                            try:
                                max_price = -1
                                for i in range(1,minutes_until_sale):
                                    if float(data[index + i][2]) > max_price:
                                        max_price = float(data[index + i][2]) 
                                        highest_sale_factor = min(max_price/compare_price, .99)
                            except IndexError:
                                break
                
                
                if lowest_buy_factor != 1:
                    optimization_factors = {}
                    optimization_factors['look_back'] = optimizing
                    optimization_factors['optimal_buy_factor'] = lowest_buy_factor
                    optimization_factors['optimal_sell_factor'] = highest_sale_factor
                    ut.pickle_write('/home/ec2-user/environment/botfarming/Development/optimization_factors/1_' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(optimizing) + '.pklz', optimization_factors)
                    print('lowest_buy_factor', lowest_buy_factor)
                    print('highest_sale_factor', highest_sale_factor)
                    print('###################################################################')
                    print('###################################################################')
                    print('###################################################################')
                    print('###################################################################')
                    print('###################################################################')
    
    
            os.remove('/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ symbol['symbol'] +'_data_'+str(minutes)+'m.pklz')
    
        if length == '1d':
            time.sleep(4*60*60)
        if length == '12h':
            time.sleep(3*60*60)
        if length == '6h':
            time.sleep(2*60*60)
        if length == '2h':
            time.sleep(1*60*60)
        if length == '1h':
            time.sleep(30*60)
        if length == '30m':
            time.sleep(20*60)