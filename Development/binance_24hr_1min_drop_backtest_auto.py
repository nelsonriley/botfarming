#!/usr/bin/python2.7
import sys
print 'python', sys.version
from pprint import pprint
import utility as ut
import utility_2 as ut2
import requests
import time
import os
import arrow
import datetime
from pytz import timezone

#################################################################################### PARAMS

# optimizing on 8 days
days = [
    # '20180129_24',
    # '20180130_24',
    # '20180131_24',
    # '20180201_24',
    # '20180202_24',
    # '20180203_24',
    '20180204_24',
    '20180205_24',
    '20180206_24'
]

future_candles_length = 15 # 20180205
buy_trigger_drop_percent_factor = 0.3 # 20180205
sell_trigger_gain_percent_factor = 0.25 # 20180205

btc_tradeable_volume_factor = 3 * 0.1 # multiplier of avg btc volume per minute over 24 hrs that we can buy & sell
btc_usd_price = 9000

min_volume_btc = 0
drops_to_collect = 1

print_trades = False

#################################################################################### RUN STRATEGY

symbols = ut.pickle_read('./botfarming/Development/binance_btc_symbols.pklz')
symbols_filtered, symbol_list = ut2.get_trimmed_symbols(symbols, min_volume_btc)


####################################################################################
# NOTES
    # 15min & 25min for future_candles_length had nearly identical results

all_day_results = {} # key = param combo, value = array of individual day results

# 3 combos takes 20min or so
# started @ 16:48 > 15:13
# for a in range(0, 3):
for a in [0.9,0.8,0.7]:

    # optimizing params: 15_0.9_0.8 = $3800
        # ('15_0.2_0.1', '$', 75852.41, 41.605, '%', 98999)
        # ('15_0.3_0.2', '$', 104511.47, 61.0679, '%', 47957) <--- LOCAL BEST
        # ('15_0.4_0.3', '$', 87807.07, 50.4541, '%', 24957)
        # ('15_0.5_0.4', '$', 76593.71, 39.4662, '%', 14306)
        # ('15_0.6_0.5', '$', 59957.12, 29.2469, '%', 21000) 2 trades/min
        # ('15_0.7_0.6', '$', 50382.33, 23.0861, '%', 4900) <--- START HERE 0.5 trades/min
        # ('15_0.75_0.65', '$', 47677.47, 21.6949, '%', 2800)
        # ('15_0.85_0.75', '$', 41578.04, 18.1444, '%') 0.166 trades/min
            # ('15_0.3_0.3', '$', 115735.12, 67.5115, '%', 47957)
            # ('15_0.3_0.15', '$', 80427.81, 46.3532, '%', 47957)
            # ('15_0.3_0.25', '$', 117912.85, 67.8962, '%', 47957) <--- BEST   4.7 trades/min    1 in 20 of all symbols being traded continuously
            # ('15_0.3_0.35', '$', 117869.66, 66.6428, '%', 47957)

    # start = 6
    # step = 6
    # future_candles_length = start + (a * step)

    # start = 0.8
    # step = 0.1
    # buy_trigger_drop_percent_factor = start + (a * step)
    buy_trigger_drop_percent_factor = a
    sell_trigger_gain_percent_factor = buy_trigger_drop_percent_factor - 0.1
    
    # sell_trigger_gain_percent_factor = a

    for d, day in enumerate(days):
        print('------------------------------', day, '-----------------------------')
        day_1 = day
        try:
            day_2 = days[d+1]
        except IndexError:
            break

        symbols_not_found_day_1 = []
        symbols_not_found_day_2 = []
        trades_by_symbol = []
        for s in symbols_filtered:
            symbol = symbols_filtered[s]

            if print_trades:
                print('------------------------------', s, '-----------------------------')

            data_1 = ut.pickle_read('./botfarming/Development/binance_training_data/'+ day_1 + '/'+ s +'_data_1m.pklz')
            if data_1 == False or len(data_1) < 30:
                if print_trades:
                    print('no data found day 1')
                symbols_not_found_day_1.append(s)
            else:
                outlier_drops = ut2.get_outlier_drops(data_1, symbol, future_candles_length, drops_to_collect)

                # print('OUTLIER DROPS')
                # print('drop_percent  best_minute  best_gain_percent  avg_gain_percent')
                # for d in outlier_drops:
                #     print(round(d['drop_percent'], 4), d['best_minute'], round(d['best_gain_percent'], 4), round(d['avg_gain_percent'], 4))
                # print('----------------------')

                buy_trigger_drop_percent = outlier_drops[-1]['drop_percent'] * buy_trigger_drop_percent_factor
                sell_trigger_gain_percent = outlier_drops[-1]['best_gain_percent'] * sell_trigger_gain_percent_factor

                # gain_percent, gain_usd, trades = ut2.trade_on_drops(symbol, data_1, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor)
                # print('GAIN ON CURRENT DAY DATA', s, round(gain_percent, 4), len(trades), round(gain_usd, 2))

                data_2 = ut.pickle_read('./botfarming/Development/binance_training_data/'+ day_2 + '/'+ s +'_data_1m.pklz')
                if data_2 == False or len(data_2) < 30:
                    if print_trades:
                        print('no data found day 2')
                    symbols_not_found_day_2.append(s)
                else:
                    gain_percent, gain_usd, trades = ut2.trade_on_drops(symbol, data_2, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor, btc_usd_price)
                    if print_trades:
                        print('GAIN ON NEXT DAY DATA', s, round(gain_percent, 4), len(trades), round(gain_usd, 2))

                    if gain_percent != 0:
                        symbol_trades = {
                            'gain_percent': gain_percent,
                            'gain_usd': gain_usd,
                            'volume_traded_btc': sum(trade['volume_traded_btc'] for trade in trades),
                            'trade_count': len(trades),
                            'trades': trades
                        }
                        trades_by_symbol.append(symbol_trades)

        #################################################################################### GET DAY RESULTS

        gain_percent = round(sum(trades['gain_percent'] for trades in trades_by_symbol), 4)
        gain_usd = round(sum(trades['gain_usd'] for trades in trades_by_symbol), 2)
        total_trades = sum(trades['trade_count'] for trades in trades_by_symbol)
        trades_per_symbol = round(total_trades / len(trades_by_symbol), 3)
        volume_traded_btc = round(sum(trades['volume_traded_btc'] for trades in trades_by_symbol), 4)
        avg_volume_btc = round(volume_traded_btc / total_trades, 6)
        avg_gain_percent = round(gain_percent / total_trades, 4)

        day_results = {
            'day': day_2,
            'gain_percent': gain_percent,
            'gain_usd': gain_usd,
            'total_trades': total_trades,
            'trades_per_symbol': trades_per_symbol,
            'volume_traded_btc': volume_traded_btc,
            'avg_volume_btc': avg_volume_btc,
            'avg_gain_percent': avg_gain_percent,
            # params
            'future_candles_length': future_candles_length,
            'buy_trigger_drop_percent_factor': buy_trigger_drop_percent_factor,
            'sell_trigger_gain_percent_factor': sell_trigger_gain_percent_factor
        }

        print('--------------------------------------------------------', day_2, 'Day Results')
        print('TOTAL_GAIN_PERCENT', gain_percent, len(trades_by_symbol), '$', gain_usd)
        print('symbols_traded', len(trades_by_symbol))
        print('total_trades', total_trades)
        print('trades_per_symbol', trades_per_symbol)
        print('avg_volume_btc', avg_volume_btc)
        print('avg_gain_percent', avg_gain_percent)
        print('most recent buy_trigger_drop_percent', round(buy_trigger_drop_percent, 7))
        print('most recent sell_trigger_gain_percent', round(sell_trigger_gain_percent, 7))
        print('symbols_not_found_day_1', len(symbols_not_found_day_1), symbols_not_found_day_1)
        print('symbols_not_found_day_2', len(symbols_not_found_day_2), symbols_not_found_day_2)

        #################################################################################### AGGREGATE RESULTS

        # param_combo = 'future_candles_length_'+str(future_candles_length)
        param_combo = str(future_candles_length)+'_'+str(buy_trigger_drop_percent_factor)+'_'+str(sell_trigger_gain_percent_factor)
        if param_combo not in all_day_results:
            all_day_results[param_combo] = []
        all_day_results[param_combo].append(day_results)


#################################################################################### CALC AGGREGATE RESULTS

all_param_results = {}
print('---------------------------------------------------------------- all_param_results')
for param_combo in all_day_results:
    days = len(day_results)
    daily_results = all_day_results[param_combo]

    gain_percent = round(sum(day_result['gain_percent'] for day_result in daily_results), 4)
    gain_usd = round(sum(day_result['gain_usd'] for day_result in daily_results), 4)
    total_trades = sum(day_result['total_trades'] for day_result in daily_results)
    trades_per_symbol = sum(day_result['trades_per_symbol'] for day_result in daily_results)
    avg_volume_btc = round(sum(day_result['avg_volume_btc'] for day_result in daily_results) / days, 4)
    avg_gain_percent = round(sum(day_result['avg_gain_percent'] for day_result in daily_results) / days, 4)
    
    trades_per_day = int(total_trades / days)
    trades_per_hour = round(total_trades / days / 24, 1)
    trades_per_minute = round(total_trades / days / 24 / 60, 2)

    param_result = {
        'gain_percent': gain_percent,
        'gain_usd': gain_usd,
        'total_trades': total_trades,
        'trades_per_symbol': trades_per_symbol,
        'avg_volume_btc': avg_volume_btc,
        'avg_gain_percent': avg_gain_percent,
        'trades_per_day': trades_per_day,
        'trades_per_hour': trades_per_hour,
        'trades_per_minute': trades_per_minute,
        # params
        'future_candles_length': daily_results[0]['future_candles_length'],
        'buy_trigger_drop_percent_factor': daily_results[0]['buy_trigger_drop_percent_factor'],
        'sell_trigger_gain_percent_factor': daily_results[0]['sell_trigger_gain_percent_factor']
    }
    all_param_results[param_combo] = param_result

    print('-----------------------------------------', param_combo)
    print(param_combo, 'cumulative', len(day_results), 'day results:')
    pprint(param_result)


print('---------------------------------------------------------------- all_param_results synopsis')

biggest_gain = 0
best_params = False
for param_combo in all_param_results:
    result = all_param_results[param_combo]
    if result['gain_usd'] > biggest_gain:
        biggest_gain = result['gain_usd']
        best_params = result
    r = result
    print(param_combo, '$', r['gain_usd'], r['gain_percent'], '%', r['total_trades'], 'day', r['trades_per_day'], 'hr', r['trades_per_hour'], 'min', r['trades_per_minute'])

print('---------------------------------------------------------------- best_params (to save)')
pprint(best_params)

# TODO: save best_params to disk
# best_params_path = './botfarming/Development/binance_24hr_1min_drop/best_params.pklz'
# ut.pickle_write(best_params_path, best_params, 'ERROR could not save best_params for 24hr 1min drop strategy')

print('done @', ut.get_time())
