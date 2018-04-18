#!/usr/bin/python2.7
import sys
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


def run_optimizer(lengths):

    while True:
        
        for length in lengths:
            
            if length == '1m':
                data_length_multiplier = 360 # 6 hours      # 3x as long, but 12 sections
                minutes = 1
                minutes_until_sale = 12
            if length == '5m':
                data_length_multiplier = 60*24*2/5 # 2 days
                minutes = 5
                minutes_until_sale = 12
            if length == '15m':
                data_length_multiplier = 60*24*7/15 # 1 wk
                minutes = 15
                minutes_until_sale = 12
            if length == '30m':
                data_length_multiplier = 60*24*14/30 # 2 wks
                minutes = 30
                minutes_until_sale = 12
            if length == '1h':
                data_length_multiplier = 60*24*14/60 # 2 wks
                minutes = 60
                minutes_until_sale = 12
            if length == '2h':
                data_length_multiplier = 60*24*30/120 # 1 month
                minutes = 60 * 2
                minutes_until_sale = 8
            if length == '6h':
                data_length_multiplier = 60*24*45/360 # 1.5 months
                minutes = 60 * 6
                minutes_until_sale = 4
            if length == '12h':
                data_length_multiplier = 60*24*90/720 # 3 months
                minutes = 60 * 12
                minutes_until_sale = 3
            if length == '1d':
                data_length_multiplier = 60*24*120/1440 # 4 months
                minutes = 60 * 24
                minutes_until_sale = 2
    
            print('starting..')
            
            ################################################################################ RUN OPTIMIZER
            
            symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
            
            symbols_trimmed = {}
            total_btc_coins = 0
            for s in symbols:
                symbol = symbols[s]
                if float(symbol['24hourVolume']) > 300:
                    total_btc_coins += 1
                    symbols_trimmed[s] = symbol
            print('total symbols', total_btc_coins)
            
            symbols_started = 0
            for s in symbols_trimmed:
                symbols_started += 1
                print('symbols_started', symbols_started)
                
                #get data in right format for save function (could fix this)
                symbol = symbols_trimmed[s]
                symbols_trimmed_one = {}
                for s_one in symbols:
                    symbol_one = symbols[s_one]
                    if symbol_one['symbol'] == symbol['symbol']:
                        symbols_trimmed_one[s] = symbol_one
                
                # 777
                optimizing_array= [1,3,5,7,9,11,13,15]
                end_time = int(time.time())
                results = get_optimization_factors(optimizing_array, data_length_multiplier, end_time, symbol, symbols_trimmed_one, length, minutes, minutes_until_sale)
                
                for i, result in enumerate(results):
                    optimization_factors_path = '/home/ec2-user/environment/botfarming/Development/optimization_factors/1_' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(result['look_back']) + '.pklz'
                    
                    ut.pickle_write(optimization_factors_path, result)
                    print('###################################################################')
                    print('###################################################################')
                    print('######### LOOK_BACK', result['look_back'], '###########', symbol['symbol'])
                    print('lowest_buy_factor', result['lowest_buy_factor'])
                    print('highest_sale_factor', result['highest_sale_factor'])
                   
    
                

# 777
def get_optimization_factors(optimizing_array, data_length_multiplier, end_time, symbol, symbols_trimmed_one, length, minutes, minutes_until_sale):

    continuous_mode = True
    continous_length = 1
    datapoints_trailing = 7
    min_volume = 0
    
    end_of_period = end_time
    one_period_ago = end_of_period - data_length_multiplier*minutes*60
    readable_time_end_of_period = datetime.datetime.fromtimestamp(end_of_period-7*60*60).strftime('%Y-%m-%d %H:%M')
    readable_time_start_of_period = datetime.datetime.fromtimestamp(one_period_ago-7*60*60).strftime('%Y-%m-%d %H:%M')
    readable_time_end_of_period_folder = datetime.datetime.fromtimestamp(end_of_period-7*60*60).strftime('%Y%m%d_%H:%M')
    readable_time_start_of_period_folder = datetime.datetime.fromtimestamp(one_period_ago-7*60*60).strftime('%Y%m%d_%H:%M')
    period = readable_time_start_of_period_folder + '_to_' + readable_time_end_of_period_folder
    #print('##########  fetching sample period data', period, 'for', symbol['symbol'], length)
    save_params = [
        [period, readable_time_start_of_period, readable_time_end_of_period]
    ]
    ut.save_data(save_params, datapoints_trailing, min_volume, minutes, symbols_trimmed_one)
    symbol_data_path = '/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ symbol['symbol'] +'_data_'+str(minutes)+'m.pklz'   

    results = []
    for optimizing in optimizing_array:
        
        lowest_buy_factor = 1
        highest_sale_factor = 1
        
        data = ut.pickle_read(symbol_data_path)
        if data == False:
            print('no data for symbol', symbol['symbol'])
            continue
        continous_length = len(data)
        
        if not data:
            continue

        for index, candle in enumerate(data):

            # ERROR: local variable 'total_of_prices' referenced before assignment
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
                    
            low_buy_factor = float(candle[3])/compare_price
            
            if low_buy_factor < lowest_buy_factor:
                lowest_buy_factor = low_buy_factor

                try:
                    max_price = -1
                    for i in range(1,minutes_until_sale):
                        if float(data[index + i][2]) > max_price:
                            max_price = float(data[index + i][2]) 
                            highest_sale_factor = max_price/compare_price
                except IndexError:
                    break

        result = {}
        result['look_back'] = optimizing
        result['lowest_buy_factor'] = lowest_buy_factor
        result['highest_sale_factor'] = highest_sale_factor
        results.append(result)

    if os.path.isfile(symbol_data_path):
        os.remove(symbol_data_path)

    return results
    

def run_optimizer_multi(lengths):
    while True:
        
        for length in lengths:
            
            symbols = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/3_binance_btc_symbols.pklz')
            symbols_trimmed = {}
            total_btc_coins = 0
            for s in symbols:
                symbol = symbols[s]
                if float(symbol['24hourVolume']) > 300:
                    total_btc_coins += 1
                    symbols_trimmed[s] = symbol
            print('total symbols', total_btc_coins)
    
            if length == '1m':
                data_length_multiplier = 360 # 6 hours      # 3x as long, but 12 sections
                minutes = 1
                minutes_until_sale = 12
            if length == '5m':
                data_length_multiplier = 60*24*2/5 # 2 days
                minutes = 5
                minutes_until_sale = 12
            if length == '15m':
                data_length_multiplier = 60*24*7/15 # 1 wk
                minutes = 15
                minutes_until_sale = 12
            if length == '30m':
                data_length_multiplier = 60*24*14/30 # 2 wks
                minutes = 30
                minutes_until_sale = 12
            if length == '1h':
                data_length_multiplier = 60*24*14/60 # 2 wks
                minutes = 60
                minutes_until_sale = 12
            if length == '2h':
                data_length_multiplier = 60*24*30/120 # 1 month
                minutes = 60 * 2
                minutes_until_sale = 8
            if length == '6h':
                data_length_multiplier = 60*24*45/360 # 1.5 months
                minutes = 60 * 6
                minutes_until_sale = 4
            if length == '12h':
                data_length_multiplier = 60*24*90/720 # 3 months
                minutes = 60 * 12
                minutes_until_sale = 3
            if length == '1d':
                data_length_multiplier = 60*24*120/1440 # 4 months
                minutes = 60 * 24
                minutes_until_sale = 2
            hours_per_period = round(float(data_length_multiplier*minutes/60.0), 3)
            
            symbols_started = 0
            for s in symbols_trimmed:
                symbols_started += 1
                print('########## symbols_started', symbols_started, 'for', length, ut.get_time())
                
                #get data in right format for save function (could fix this)
                symbol = symbols_trimmed[s]
                symbols_trimmed_one = {}
                for s_one in symbols:
                    symbol_one = symbols[s_one]
                    if symbol_one['symbol'] == symbol['symbol']:
                        symbols_trimmed_one[s] = symbol_one
                
                # 777
                optimizing_array = [1,3,5,7,9,11,13,15]
                results_by_look_back = {}
                for lb in optimizing_array:
                    results_by_look_back[str(lb)] = []
            
                step_back_periods = 12
                for step_back in range(0, step_back_periods):
                    end_time = int(time.time()) - data_length_multiplier * step_back * minutes * 60
                    results = get_optimization_factors(optimizing_array, data_length_multiplier, end_time, symbol, symbols_trimmed_one, length, minutes, minutes_until_sale)
                    for r in results:
                        results_by_look_back[str(r['look_back'])].append(r)
                    # results = [r, r, r...]
                        # r['lowest_buy_factor'] = lowest_buy_factor
                        # r['highest_sale_factor'] = highest_sale_factor
                        # r['look_back'] = optimizing
                        # r['optimal_buy_factor'] = lowest_buy_factor
                        # r['optimal_sell_factor'] = highest_sale_factor
                
                for lb in results_by_look_back:
                    lowest_buy_factors = []
                    highest_sale_factors = []
                    results = results_by_look_back[lb]
                    for r in results:
                        lowest_buy_factors.append(r['lowest_buy_factor'])
                        highest_sale_factors.append(r['highest_sale_factor'])
                    lowest_buy_factor_stats = fn.std_dev(lowest_buy_factors)
                    highest_sale_factor_stats = fn.std_dev(highest_sale_factors)
                    
                    if lowest_buy_factor_stats == False or highest_sale_factor_stats == False:
                        continue
                    # print('#####################################################')
                    # print('LOWEST BUY FACTORS ######## LOOK_BACK', lb, s, step_back_periods, '*', hours_per_period, 'hrs')
                    # pprint(lowest_buy_factor_stats)
                    # print(lowest_buy_factors)
                    # print('HIGHEST SALE FACTORS ######## LOOK_BACK', lb, s, step_back_periods, '*', hours_per_period, 'hrs')
                    # pprint(highest_sale_factor_stats)
                    # print(highest_sale_factors)
                    # print('#####################################################')
            
                    result = {}
                    result['lowest_buy_factor_std_dev'] = lowest_buy_factor_stats['std_dev']
                    result['lowest_buy_factor_min'] = lowest_buy_factor_stats['min']
                    result['highest_sale_factor_std_dev'] = highest_sale_factor_stats['std_dev']
                    result['highest_sale_factor_min'] = highest_sale_factor_stats['min']
                    result['look_back'] = int(lb)
                    result['lowest_buy_factor'] = lowest_buy_factor_stats['mean']
                    result['highest_sale_factor'] = highest_sale_factor_stats['mean']
            
                    optimization_factors_path = '/home/ec2-user/environment/botfarming/Development/optimization_factors/2_' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(result['look_back']) + '.pklz'
                    ut.pickle_write(optimization_factors_path, result)
                    
                    optimization_factors_path_2 = '/home/ec2-user/environment/botfarming/Development/optimization_factors/1_' + length + '_optimal_for_' + symbol['symbol'] + '_' + str(result['look_back']) + '.pklz'
                    ut.pickle_write(optimization_factors_path_2, result)