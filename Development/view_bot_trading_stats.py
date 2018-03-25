#!/usr/bin/python2.7
import sys
print 'python', sys.version

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import utility as ut
import json
import math
from os import listdir
from os.path import isfile, join





    
# if bot_trades == False:
#ut.pickle_write(path, [])
#bot_trades = ut.pickle_read(path)
total_profit = 0
total_trades = 0
total_profit_a = 0
total_trades_a = 0
total_profit_b = 0
total_trades_b = 0
profit_with_limit = 0
profit_with_limit_2 = 0
profit_with_limit_3 = 0
profit_with_limit_4 = 0
# start_epoch = 1517024439
# start_epoch = 1517353200

start_counting = False

bot_trades = []
    
path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/'
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
for file in onlyfiles:
    if file.startswith("1m_0"):
        bot_trades.append(ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file))
        
for bot_trade in bot_trades:
    
    start_counting = True
    if start_counting == True:# and bot_trade[4] < .7: # and bot_trade[5] == 17: # and bot_trade[5] != 11 and bot_trade[5] != 9:
        print('bit coin invested', bot_trade[4], 'look_back', bot_trade[5], 'look_back_gains', bot_trade[7], 'look_back_wins', bot_trade[8], 'look_back_losses', bot_trade[9], 'price_to_buy_factor', bot_trade[10])
        
        #print('time start', bot_trade[0], 'symbol', bot_trade[1], 'asolute profit', bot_trade[2], 'percentage profit', bot_trade[3], 'bit coin invested', bot_trade[4], 'look_back', bot_trade[5], 'a_b', bot_trade[6], 'look_back_gains', bot_trade[7], 'look_back_wins', bot_trade[8], 'look_back_losses', bot_trade[9], 'price_to_buy_factor', bot_trade[10], 'price_to_sell_factor', bot_trade[11], 'original_buy_time', bot_trade[12], 'sell time', bot_trade[13])
        total_profit += bot_trade[2]
        total_trades += 1
    
        if bot_trade[6] == 0:
            total_profit_a += bot_trade[2]
            total_trades_a += 1
    
        if bot_trade[6] == 1:
            total_profit_b += bot_trade[2]
            total_trades_b += 1
    
    
    
    
    
    
    # look_back_optimized = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/optimization_factors/optimal_for_' + bot_trade[1] + '_1.pklz')
    # if look_back_optimized != False:
    #     print(bot_trade[1], look_back_optimized[9], look_back_optimized[10], look_back_optimized[11])
    #     if float(look_back_optimized[11]) != 0:
    #         win_loss_ratio = float(look_back_optimized[10])/float(look_back_optimized[11])
    #     else:
    #         win_loss_ratio = 999
    #     print win_loss_ratio
    # print('')
    
    # print(bot_trade['time_buy_epoch'], bot_trade['time_buy_human'], bot_trade['symbol'], bot_trade['profit_btc'], bot_trade['profit_percent'], bot_trade['invested_btc'], bot_trade['look_back'], bot_trade['volume_ten_candles_btc'], bot_trade['volume_twentyfour_hr_btc'])
    #if win_loss_ratio > 4:
    # profit_with_limit += bot_trade['profit_percent']*min(.35,bot_trade['invested_btc'])
    # profit_with_limit_2 += bot_trade['profit_percent']*min(.4,bot_trade['invested_btc'])
    # profit_with_limit_3 += bot_trade['profit_percent']*min(.45,bot_trade['invested_btc'])
    # profit_with_limit_4 += bot_trade['profit_percent']*min(.5,bot_trade['invested_btc'])


print(total_profit)
print(total_trades)

print(total_profit_a)
print(total_trades_a)

print(total_profit_b)
print(total_trades_b)

# global total_trades_overall
# total_trades_overall = 0

# global all_trades
# all_trades = {}

# global overall_profit
# overall_profit = 0

# def print_trade_totals(length):

#     trades_by_symbol = {}
#     trades_by_size = {}
#     trades_by_size['under_1000'] = {}
#     trades_by_size['under_1000']['sum'] = 0
#     trades_by_size['under_1000']['number_of_trades'] = 0
#     trades_by_size['over_1000'] = {}
#     trades_by_size['over_1000']['sum'] = 0
#     trades_by_size['over_1000']['number_of_trades'] = 0
#     symbols = ut.pickle_read('./botfarming/Development/binance_btc_symbols.pklz')
#     #pprint(symbols)

#     file_path = './botfarming/Development/binance_' + length + '_trades/' + length + '_trade_data'
#     f = gzip.open(file_path,'rb')
#     data_points = pickle.load(f)
#     #pprint(data_points)
#     f.close()

#     total_profit = 0
#     total_trades = 0
#     start_counting = False
#     for data in data_points:
#         if data[4].find('2018-01-24 20') >= 0 or data[4].find('2018-01-24 21') >= 0 or data[4].find('2018-01-24 22') >= 0 or data[4].find('2018-01-24 23') >= 0 or data[4].find('2018-01-25') >= 0 or start_counting:
#             start_counting = True
#             global total_trades_overall
#             total_trades_overall += 1
#             total_trades += 1
#             global all_trades
#             all_trades[data[3]] = data

#             pprint(data)
#             global overall_profit
#             overall_profit += data[0]


#             if data[1] > -.2 and len(data) > 5:
#                 if float(symbols[data[3]]['24hourVolume']) < 600:
#                     trades_by_size['under_1000']['sum'] += data[0]
#                     trades_by_size['under_1000']['number_of_trades'] += 1
#                 else:
#                     trades_by_size['over_1000']['sum'] += data[0]
#                     trades_by_size['over_1000']['number_of_trades'] += 1
#                 if data[2] in trades_by_symbol:
#                     trades_by_symbol[data[3]]['sum_of_trades'] += data[0]
#                     trades_by_symbol[data[3]]['total_trades'] += 1
#                     trades_by_symbol[data[3]]['average_per_trade'] = trades_by_symbol[data[3]]['sum_of_trades']/trades_by_symbol[data[3]]['total_trades']
#                 else:
#                     trades_by_symbol[data[3]] = {}
#                     trades_by_symbol[data[3]]['sum_of_trades'] = data[0]
#                     trades_by_symbol[data[3]]['24_hour_volume'] = symbols[data[3]]['24hourVolume']
#                     trades_by_symbol[data[3]]['total_trades'] = 1
#                     trades_by_symbol[data[3]]['average_per_trade'] = data[0]/1


#             total_profit += data[0]
#             #else:
#                 #pprint(data)


#     print('totals for look back', length)
#     try:
#         print('over 1000 average', trades_by_size['over_1000']['sum']/trades_by_size['over_1000']['number_of_trades'], trades_by_size['over_1000']['number_of_trades'])
#     except Exception as e:
#         print('no trades over 1000')
#     try:
#         print('under 1000 average', trades_by_size['under_1000']['sum']/trades_by_size['under_1000']['number_of_trades'], trades_by_size['under_1000']['number_of_trades'])
#     except Exception as e:
#         print('no trades under 1000')
#     print('total_profit', total_profit)
#     print('total_trades', total_trades)
#     #print('trades_by_symbol')
#     #pprint(trades_by_symbol)
#     print('')

# for x in range(1,7):
#     print_trade_totals(str(x))

# print(overall_profit)

# print('total_trades_overall', total_trades_overall)
# pprint(all_trades)



