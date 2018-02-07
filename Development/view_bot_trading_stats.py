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

path = './botfarming/Development/binance_all_trades_history/binance_all_trades_history.pklz'
bot_trades = ut.pickle_read(path)
# if bot_trades == False:
#ut.pickle_write(path, [])
#bot_trades = ut.pickle_read(path)

total_profit = 0
total_trades = 0
profit_with_limit = 0
profit_with_limit_2 = 0
profit_with_limit_3 = 0
profit_with_limit_4 = 0
# start_epoch = 1517024439
# start_epoch = 1517353200


for bot_trade in bot_trades:
    print(bot_trade[0], bot_trade[1], bot_trade[2], bot_trade[3], bot_trade[4], bot_trade[5])

    # print(bot_trade['time_buy_epoch'], bot_trade['time_buy_human'], bot_trade['symbol'], bot_trade['profit_btc'], bot_trade['profit_percent'], bot_trade['invested_btc'], bot_trade['look_back'], bot_trade['volume_ten_candles_btc'], bot_trade['volume_twentyfour_hr_btc'])
    total_profit += bot_trade[2]
    total_trades += 1
    # profit_with_limit += bot_trade['profit_percent']*min(.35,bot_trade['invested_btc'])
    # profit_with_limit_2 += bot_trade['profit_percent']*min(.4,bot_trade['invested_btc'])
    # profit_with_limit_3 += bot_trade['profit_percent']*min(.45,bot_trade['invested_btc'])
    # profit_with_limit_4 += bot_trade['profit_percent']*min(.5,bot_trade['invested_btc'])


print(total_profit)
print(total_trades)

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



