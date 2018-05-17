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
import utility_3 as ut
import json
import math
from operator import itemgetter
from os import listdir
from os.path import isfile, join



    
# if bot_trades == False:
#ut.pickle_write(path, [])
#bot_trades = ut.pickle_read(path)

total_profit_segment = 0
total_trades_segment = 0
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

 # sort by 'original_buy_time'

#pprint(bot_trades[0])

all_trades_made_within_a_period_of_time = []
trades_made_within_a_period_of_time_profit = 0

last_neg_buy_time = {}
trades_reduced = []


real_total_profit = 0

first_loop = True

path = '/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/'
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

look_backs = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']


final_total_trades = 0
final_profit = 0
final_profit_a = 0
final_profit_b = 0
final_total_trades_a = 0
final_total_trades_b = 0

profit_by_std = {}

max_time = 0

for look_back in look_backs:
    
    print('look_back', look_back)
    
    bot_trades = []
    
    for file in onlyfiles:
        if file.startswith(look_back + "_0"):
            #print('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            trade = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            if len(trade) == 14:
                trade.append(look_back)
                trade.append(trade[0])
                trade[0] = ut.convert_date_to_epoch(trade[0])
                #trade[10] = ut.convert_date_to_epoch(trade[10])
                bot_trades.append(trade)
                
    total_profit = 0
    total_trades = 0
    total_profit_a = 0
    total_trades_a = 0
    total_profit_b = 0
    total_trades_b = 0
    
    for i, bot_trade in enumerate(bot_trades):
        
        if bot_trade[9] > max_time:
            max_time = bot_trade[9]
        
        
        if bot_trade[9] > 1526562889 and bot_trade[3] > -.25 and bot_trade[6] == 0 and bot_trade[14] == '5m':
            #print(bot_trade[2])1525874697,1525989553
            # if (bot_trade[3] < -.01):
            #     bot_trade[2] = bot_trade[4]*-.01
            
            #pprint(bot_trade)
            
            if bot_trade[3] < -.02:
                pprint(bot_trade)
            
            if bot_trade[12] not in profit_by_std:
                profit_by_std[bot_trade[12]] = bot_trade[2]
            else:
                profit_by_std[bot_trade[12]] += bot_trade[2]
            
            total_profit += bot_trade[2] # 'absolute profit', bot_trade[2], 'percentage profit', bot_trade[3]
            total_trades += 1
            final_total_trades += 1
            final_profit += bot_trade[2]
    
            if bot_trade[6] == 1:
                total_profit_a += bot_trade[2]
                total_trades_a += 1
                final_profit_a += bot_trade[2]
                final_total_trades_a += 1
            else:
                total_profit_b += bot_trade[2]
                total_trades_b += 1
                final_profit_b += bot_trade[2]
                final_total_trades_b += 1
        
        

    print('total_profit', total_profit)
    print('total_trades', total_trades)
    print('total_profit_a', total_profit_a)
    print('total_trades_a', total_trades_a)
    print('total_profit_b', total_profit_b)
    print('total_trades_b', total_trades_b)
    
print('')

print('final_profit', final_profit)
print('final_total_trades', final_total_trades)
print('final_profit_a', final_profit_a)
print('final_total_trades_a', final_total_trades_a)
print('final_profit_b', final_profit_b)
print('final_total_trades_b', final_total_trades_b)
print('max_time', max_time)
print('current_time', int(time.time()))
print('time of last commit', int(time.time())-9*60*60)

pprint(profit_by_std)

sys.exit()


#for look_back in look_backs:
    
#print('look_back', look_back)

bot_trades = []

max_profit = -999999
best_not_trade_value = -1
best_hours_to_not_trade = -1


for look_back in look_backs:
    for file in onlyfiles:
        if file.startswith(look_back + "_0"):
            #print('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            trade = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_all_trades_history/' + file)
            if len(trade) == 11:
                trade.append(look_back)
                trade[0] = ut.convert_date_to_epoch(trade[0])
                trade[10] = ut.convert_date_to_epoch(trade[10])
                bot_trades.append(trade)

bot_trades = sorted(bot_trades, key=itemgetter(9))

all_trades_counted = []




for a in range(0, 60):
    
    
    
    seconds_before_blacklisting_2 = 1*a

    
    for b in range(0,40):
        #not_trade_value_2 = -.001*b
        
        
        blacklist_for_hours_2 = .5*b
        
        
        for c in range(0,1):
            
            
            not_trade_value_2 = -.035
            hours_to_not_trade_2 = 6
            seconds_before_blacklisting = 190
            blacklist_for_hours = 1.4
            number_to_stop_trading = 3
            minutes_to_stop_trading = 24
            look_back_minutes = 25
            hours_to_not_trade = 10
            not_trade_value = -.02
            
            
            
        
            do_not_buy_time_start = {}
            do_not_buy_time_end = {}
            recent_trades = {}
            recent_trade = 0
            do_not_buy_time_end_2 = {}
            
            total_profit = 0
            total_trades = 0
            
            all_trades_counted_temp = []
            
            last_few_trade_start_times = []
            
            do_not_trade_time_general = 0
            do_not_trade_time_general_2 = 0
            do_not_trade_time_general_3 = 0
            do_not_trade_times = {}
            
            #print 'START'
            
            for i, bot_trade in enumerate(bot_trades):
                #s = bot_trade[1]
                #start_time = ut.get_time_formats(bot_trade[9])
                
                if bot_trade[9] > 1522540800: # and bot_trade[1] != 'CTRBTC': # and start_time['epoch'] < 1523299178:
                
                    if first_loop == True:
                        pprint(bot_trade)
                        first_loop = False
                        
                    ## if trade triggered on same symbol in X minutes or less
                    ## don't start trade + blacklist symbol for Y hours
                    
                    
                    
                    ##

                    # Calc total profit
                    if (bot_trade[1] not in do_not_buy_time_end_2 or float(bot_trade[9]) > float(do_not_buy_time_end_2[bot_trade[1]])) and bot_trade[9] > do_not_trade_time_general_2: #bot_trade[9] > do_not_trade_time_general_2: # and (bot_trade[1] not in do_not_buy_time_end_2 or float(bot_trade[9]) > float(do_not_buy_time_end_2[bot_trade[1]])): # and bot_trade[9] > do_not_trade_time_general and (bot_trade[1] not in do_not_buy_time_end or float(bot_trade[9]) > float(do_not_buy_time_end[bot_trade[1]]) or float(bot_trade[9]) < float(do_not_buy_time_start[bot_trade[1]])):
                        
                        if bot_trade[3] > -.5:
                            total_profit += bot_trade[2] # 'absolute profit', bot_trade[2], 'percentage profit', bot_trade[3]
                            total_trades += 1
                        
                            all_trades_counted_temp.append(bot_trade)

                        ## if X trades (all symbols) started within Y minutes
                        ## stop all trades for Z minutes
                            
                        last_few_trade_start_times.append(bot_trade[9])
                        
                        while True:
                            if last_few_trade_start_times[0] < bot_trade[9] - look_back_minutes*60:
                                del last_few_trade_start_times[0]
                            else:
                                break
                                
                        if len(last_few_trade_start_times) >= number_to_stop_trading:
                            #pprint(last_few_trade_start_times)
                            do_not_trade_time_general = bot_trade[9] + minutes_to_stop_trading*60
                        
                        ##
                        
                        if bot_trade[1] in do_not_buy_time_end and float(bot_trade[9]) > float(do_not_buy_time_end[bot_trade[1]]):
                            do_not_buy_time_start[bot_trade[1]] = 0
                            
                            
                        if bot_trade[3] < not_trade_value and bot_trade[3] > -.5:
                            #do_not_trade_time_general_2 = bot_trade[10] + hours_to_not_trade*60*60
                            do_not_buy_time_end[bot_trade[1]] = bot_trade[10] + hours_to_not_trade*60*60
                            do_not_buy_time_start[bot_trade[1]] = bot_trade[10]
                        
                        
                        if bot_trade[3] < not_trade_value_2 and bot_trade[3] > -.5:
                            do_not_trade_time_general_2 = bot_trade[10] + hours_to_not_trade_2*60*60
                            
                        if bot_trade[1] in recent_trades:
                            if bot_trade[9] - recent_trades[bot_trade[1]] < seconds_before_blacklisting:
                                do_not_buy_time_end_2[bot_trade[1]] = bot_trade[9] + blacklist_for_hours*60*60
                                
                        if bot_trade[9] - recent_trade < seconds_before_blacklisting_2:
                            do_not_trade_time_general_3 = bot_trade[9] + blacklist_for_hours_2*60*60
                                
                                
                        recent_trades[bot_trade[1]] = bot_trade[9]
                        
                        recent_trade = bot_trade[9]
                            
                         
            if a == 0 and b == 0:
                print('original profit at base', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
            
            #print('original profit at base', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
            
            #print('original profit at base', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
            
            
            # if hours_to_not_trade > 8 and hours_to_not_trade < 10 and not_trade_value < -.08 and not_trade_value > -.1:
            #     print('for special total profit', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
            
                
            if total_profit > max_profit:
                max_profit = total_profit
                best_hours_to_not_trade = hours_to_not_trade
                best_not_trade_value = not_trade_value
                all_trades_counted = all_trades_counted_temp
                print('****new best total profit', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
                print('number_to_stop_trading', number_to_stop_trading, 'minutes_to_stop_trading', minutes_to_stop_trading, 'look_back_minutes', look_back_minutes)
                print('seconds_before_blacklisting', seconds_before_blacklisting, 'blacklist_for_hours', blacklist_for_hours)
                print('hours_to_not_trade_2', hours_to_not_trade_2, 'not_trade_value_2', not_trade_value_2)
                print('blacklist_for_hours_2', blacklist_for_hours_2, 'seconds_before_blacklisting_2', seconds_before_blacklisting_2)
        
            # if not_trade_value_2 == -.04:
            #     print('****new good total profit', total_profit, 'hours_not_to_trade', hours_to_not_trade, 'not_trade_value', not_trade_value, 'total_trades', total_trades)
            #     print('number_to_stop_trading', number_to_stop_trading, 'minutes_to_stop_trading', minutes_to_stop_trading, 'look_back_minutes', look_back_minutes)
            #     print('seconds_before_blacklisting', seconds_before_blacklisting, 'blacklist_for_hours', blacklist_for_hours)
            #     print('hours_to_not_trade_2', hours_to_not_trade_2, 'not_trade_value_2', not_trade_value_2)
        


real_total_profit += max_profit
print('max profit', max_profit, 'hours_not_to_trade', best_hours_to_not_trade, 'not_trade_value', best_not_trade_value)
print('') 

look_backs = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']


for look_back in look_backs:
    print(look_back)
    total_profit = 0
    total_trades = 0
    for trade in all_trades_counted:
        if look_back == trade[11] and trade[3] > -.5:
            total_profit += trade[2]
            total_trades += 1
            
    
    print('total_profit', total_profit)
    print('total_trades', total_trades)
            
    
#print('real_total_profit', real_total_profit)
              
        # Consider blacklisting a symbol for some period of time after negative trade
        # trade_is_negative = bot_trade[2] < 0
        # if not s in last_neg_buy_time:
        #     last_neg_buy_time[s] = 0
        # if start_time['epoch'] - last_neg_buy_time[s] <= 24 * 60 * 60:
        #     pass
        # else:
        #     trades_reduced.append(bot_trade)
        #     if trade_is_negative:
        #         last_neg_buy_time[s] = start_time['epoch']
        #     else:
        #         last_neg_buy_time[s] = 0
    
        
        # Study trades of same symbol with close start times
        # trades_made_within_a_period_of_time = 1
        # start_seconds = bot_trade[9]
        # hist_index = i
        # held_for_seconds = 0
        # first_trade_in_set = []
        # while True and i > 5:
        #     hist_index += -1
        #     if bot_trade[9] - bot_trades[hist_index][9] <= 120 and bot_trade[1] == bot_trades[hist_index][1]:
        #         trades_made_within_a_period_of_time += 1
        #         held_for_seconds = bot_trade[9] - bot_trades[hist_index][9]
        #         first_trade_in_set = bot_trades[hist_index]
        #         continue
        #     break
        # if trades_made_within_a_period_of_time == 2:
        #     trades_reduced.append(first_trade_in_set)
        # if trades_made_within_a_period_of_time >= 2: # and bot_trade[1] != 'CTRBTC':
        #     all_trades_made_within_a_period_of_time.append(str(trades_made_within_a_period_of_time)+'_'+bot_trade[1]+' '+str(bot_trade[0])+' held for seconds '+str(held_for_seconds))
        #     trades_made_within_a_period_of_time_profit += bot_trade[2]
    
    
        # Look at CTR Trades we lost a bunch of money on
        # if bot_trade[9] >= 1522709297 and bot_trade[1] == 'CTRBTC':# 1522684266 and bot_trade[10] == '1m' and bot_trade[8] - bot_trade[7]  > .015:# and bot_trade[7] < .976: #and bot_trade[5] != 9:
        #     print('')
            
        #     # pprint(bot_trade)
            
        #     # start_time = ut.get_time_formats(bot_trade[9])
        #     # end_time = ut.get_time_formats(bot_trade[13])
        #     # start_to_end_s = end_time['epoch'] - start_time['epoch']
        #     # start_to_end_m = start_to_end_s / 60.0
        #     # print(start_time['human'], end_time['human'], start_to_end_m, start_to_end_s)
            
        #     print('time start', bot_trade[0], 'symbol', bot_trade[1], 'asolute profit', bot_trade[2], 'percentage profit', bot_trade[3], 'bit coin invested', bot_trade[4], 'look_back', bot_trade[5], 'a_b', bot_trade[6], 'price_to_buy_factor', bot_trade[7], 'price_to_sell_factor', bot_trade[8], 'original_buy_time', bot_trade[9], 'sell time', bot_trade[10])
            
        #     total_profit_segment += bot_trade[2]
        #     total_trades_segment += 1
            
        #     if bot_trade[6] == 1:
        #         total_profit_a += bot_trade[2]
        #         total_trades_a += 1
        #     else:
        #         total_profit_b += bot_trade[2]
        #         total_trades_b += 1
            
        
        # if start_counting == True and bot_trade[5] == 17 and bot_trade[10] < .986: # and bot_trade[5] == 17: # and bot_trade[5] != 11 and bot_trade[5] != 9:
        #     print('bit coin invested', bot_trade[4], 'look_back', bot_trade[5], 'look_back_gains', bot_trade[7], 'look_back_wins', bot_trade[8], 'look_back_losses', bot_trade[9], 'price_to_buy_factor', bot_trade[10])
        
        #     total_profit += bot_trade[2]
        #     total_trades += 1
        
        #     
        
        
        
        
        
        
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



# print('all_trades_made_within_a_period_of_time', len(all_trades_made_within_a_period_of_time))
# pprint(all_trades_made_within_a_period_of_time)
# print('trades_made_within_a_period_of_time_profit', trades_made_within_a_period_of_time_profit)

# print()
# print('trades_reduced', len(trades_reduced))
# trades_reduced_profit = sum(l[2] for l in trades_reduced)
# print('trades_reduced_profit', trades_reduced_profit)

# print()
# print('total profit segment', total_profit_segment)
# print('total trades segment', total_trades_segment)

# print()
# print('total profit a', total_profit_a)
# print('total_trades a', total_trades_a)

# print()
# print('total profit b', total_profit_b)
# print('total_trades b', total_trades_b)

# print(total_profit_b)
# print(total_trades_b)

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

