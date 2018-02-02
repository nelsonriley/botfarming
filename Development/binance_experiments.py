#!/usr/bin/python2.7
import sys
print 'python', sys.version
from pprint import pprint
import utility as ut
import requests
import time
import os
import arrow
import datetime
from pytz import timezone

#################################################################################### Helpers

def get_candle_as_dict(c):
    return {
        'open_time': int(c[0]),
        'open_time_readable': ut.get_readable_time(int(c[0])),
        'open_price': float(c[1]),
        'high_price': float(c[2]),
        'low_price': float(c[3]),
        'close_price': float(c[4]),
        'volume': float(c[5]),
        'close_time': int(c[6])
    }

def get_future_candles(future_candles_length, data, i):
    future_candles_exist = True
    future_candles = []
    for f in range(1, future_candles_length+1):
        try:
            f_c = data[i+f]
            f_c = get_candle_as_dict(f_c)
            future_candles.append(f_c)
        except IndexError:
            future_candles_exist = False
    if future_candles_exist:
        return future_candles
    return False

def get_outlier_drops(data, symbol):
    outlier_drops = []
    smallest_drop_percent = 0
    for i, c in enumerate(data):
        c = get_candle_as_dict(c)

        drop = c['open_price'] - c['low_price']
        drop_percent = drop / c['open_price']

        if drop > 0 and drop_percent > smallest_drop_percent:

            future_candles = get_future_candles(future_candles_length, data, i)

            if future_candles:
                # calculate stats on future candles
                best_minute = 1
                best_gain = 0
                best_gain_percent = 0
                total_gain = 0
                total_gain_percent = 0
                for m, f_c in enumerate(future_candles):
                    minute = m + 1
                    gain = f_c['high_price'] - c['low_price']
                    gain_percent = gain / c['low_price']
                    total_gain += gain
                    total_gain_percent += gain_percent
                    if gain > best_gain:
                        best_gain = gain
                        best_gain_percent = best_gain / c['low_price']
                        best_minute = minute
                avg_gain_percent = total_gain_percent / future_candles_length

                # save & sort the biggest drops
                outlier_drops.append({
                    'best_gain_percent': best_gain_percent,
                    'avg_gain_percent': avg_gain_percent,
                    'best_minute': best_minute,
                    'drop_percent': drop_percent,
                    'candle': c,
                    'future_candles': future_candles,
                })
                outlier_drops = sorted(outlier_drops, key=lambda k: k['drop_percent'])
                if len(outlier_drops) > drops_to_collect:
                    del outlier_drops[0]
                smallest_drop_percent = outlier_drops[0]['drop_percent']
    return outlier_drops

def trade_on_drops(symbol, data, buy_trigger_drop_percent, sell_trigger_gain_percent):
    s = symbol['symbol']
    one_min_avg_volume = float(symbol['24hourVolume']) / (24*60)
    btc_tradeable_volume =  btc_tradeable_volume_factor * one_min_avg_volume
    trades = []
    for i, c in enumerate(data):
        c = get_candle_as_dict(c)

        drop = c['open_price'] - c['low_price']
        drop_percent = drop / c['open_price']

        if drop_percent > buy_trigger_drop_percent:
            buy_price = c['open_price'] - buy_trigger_drop_percent * c['open_price']
            sell_price = 0
            future_candles = get_future_candles(future_candles_length, data, i)
            if future_candles:
                traded_by_sell_trigger = False
                for f, f_c in enumerate(future_candles):
                    minute = f + 1
                    sell_price = buy_price + sell_trigger_gain_percent * buy_price
                    if f_c['high_price'] > sell_price:
                        traded_by_sell_trigger = True
                        break
                if not traded_by_sell_trigger:
                    sell_price = future_candles[-1]['close_price']
                gain = sell_price - buy_price
                gain_percent = gain / buy_price
                gain_btc = btc_tradeable_volume * gain_percent
                gain_usd = gain_btc * btc_usd_price
                trade = {
                    'gain_percent': gain_percent,
                    'minute': minute,
                    'buy_time_readable': c['open_time_readable'],
                    'gain_btc': gain_btc,
                    'gain_usd': gain_usd,
                    'volume_traded_btc': btc_tradeable_volume
                }
                trades.append(trade)

    gain_percent = sum(trade['gain_percent'] for trade in trades)
    gain_usd = sum(trade['gain_usd'] for trade in trades)
    return gain_percent, gain_usd, trades

def get_trimmed_symbols(symbols_dict, min_volume_btc):
    symbol_list = []
    symbols_filtered = {}
    for s in symbols_dict:
        symbol = symbols_dict[s]
        if float(symbol['24hourVolume']) >= min_volume_btc:
            symbols_filtered[s] = symbol
            symbol_list.append(s)
    return symbols_filtered, symbol_list

#################################################################################### PARAMS

days = [
    '20180129_c',
    '20180130_c',  # ('TOTAL_GAIN_PERCENT', 2.0255, 53, 3217.01)
    '20180131_c',  # ('TOTAL_GAIN_PERCENT', 2.0254, 64, 4891.32)
    '20180201'     # ('TOTAL_GAIN_PERCENT', 1.9119, 63, 3206.04)
]
drops_to_collect = 2
future_candles_length = 20
min_volume_btc = 0
btc_tradeable_volume_factor = 3 * 0.1 # multiplier of avg btc volume per min over 24 hrs that we can buy & sell
btc_usd_price = 9000
buy_trigger_drop_percent_factor = 0.9
sell_trigger_gain_percent_factor = 0.8

print_trades = False

#################################################################################### RUN STRATEGY

symbols = ut.pickle_read('./binance_btc_symbols.pklz')
symbols_filtered, symbol_list = get_trimmed_symbols(symbols, min_volume_btc)

for d, day in enumerate(days):
    print('------------------------------', day, '-----------------------------')
    day_1 = day
    try:
        day_2 = days[d+1]
    except IndexError:
        break

    symbols_not_found_day_1 = []
    symbols_not_found_day_2 = []
    all_trades = []
    for s in symbols_filtered:
        symbol = symbols_filtered[s]

        if print_trades:
            print('------------------------------', s, '-----------------------------')

        data_1 = ut.pickle_read('./binance_training_data/'+ day_1 + '/'+ s +'_data_1m.pklz')
        if data_1 == False or len(data_1) < 30:
            if print_trades:
                print('no data found day 1')
            symbols_not_found_day_1.append(s)
        else:
            outlier_drops = get_outlier_drops(data_1, symbol)

            # print('OUTLIER DROPS')
            # print('drop_percent  best_minute  best_gain_percent  avg_gain_percent')
            # for d in outlier_drops:
            #     print(round(d['drop_percent'], 4), d['best_minute'], round(d['best_gain_percent'], 4), round(d['avg_gain_percent'], 4))
            # print('----------------------')

            buy_trigger_drop_percent = outlier_drops[-1]['drop_percent'] * buy_trigger_drop_percent_factor
            sell_trigger_gain_percent = outlier_drops[-1]['best_gain_percent'] * sell_trigger_gain_percent_factor

            # gain_percent, gain_usd, trades = trade_on_drops(symbol, data_1, buy_trigger_drop_percent, sell_trigger_gain_percent)
            # print('GAIN ON CURRENT DAY DATA', s, round(gain_percent, 4), len(trades), round(gain_usd, 2))

            data_2 = ut.pickle_read('./binance_training_data/'+ day_2 + '/'+ s +'_data_1m.pklz')
            if data_2 == False or len(data_2) < 30:
                if print_trades:
                    print('no data found day 2')
                symbols_not_found_day_2.append(s)
            else:
                gain_percent, gain_usd, trades = trade_on_drops(symbol, data_2, buy_trigger_drop_percent, sell_trigger_gain_percent)
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
                    all_trades.append(symbol_trades)

    #################################################################################### GET RESULTS

    gain_percent = round(sum(trade['gain_percent'] for trade in all_trades), 4)
    gain_usd = round(sum(trade['gain_usd'] for trade in all_trades), 2)
    total_trades = sum(trade['trade_count'] for trade in all_trades)
    trades_per_symbol = round(total_trades / len(all_trades), 3)
    volume_traded_btc = round(sum(trade['volume_traded_btc'] for trade in all_trades), 4)
    avg_volume_btc = round(volume_traded_btc / total_trades, 6)
    avg_gain_percent = round(gain_percent / total_trades, 4)
    print('--------------------------------------------------------', day_2, 'Results')
    print('TOTAL_GAIN_PERCENT', gain_percent, len(all_trades), '$', gain_usd)
    print('symbols_traded', len(all_trades))
    print('total_trades', total_trades)
    print('trades_per_symbol', trades_per_symbol)
    print('avg_volume_btc', avg_volume_btc)
    print('avg_gain_percent', avg_gain_percent)
    print('symbols_not_found_day_1', len(symbols_not_found_day_1), symbols_not_found_day_1)
    print('symbols_not_found_day_2', len(symbols_not_found_day_2), symbols_not_found_day_2)

