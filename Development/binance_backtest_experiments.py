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

###################### USE THIS FILE TO DEVELOP BINANCE STRATEGIES AS BACKTESTS



# #################################################################################### 24hr_1min_drop_strategy:
# #################################################################################### Helpers

# def trade_on_drops(symbol, data, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor):
#     s = symbol['symbol']
#     one_min_avg_volume = float(symbol['24hourVolume']) / (24*60)
#     btc_tradeable_volume =  btc_tradeable_volume_factor * one_min_avg_volume
#     trades = []
#     for i, c in enumerate(data):
#         c = ut2.get_candle_as_dict(c)

#         drop = c['open_price'] - c['low_price']
#         drop_percent = drop / c['open_price']

#         if drop_percent > buy_trigger_drop_percent:
#             buy_price = (c['open_price'] - buy_trigger_drop_percent * c['open_price']) * 1.002
#             future_candles = ut2.get_future_candles(future_candles_length, data, i)
#             if future_candles:
#                 traded_by_sell_trigger = False
#                 for f, f_c in enumerate(future_candles):
#                     minute = f + 1
#                     sell_trigger_price = (buy_price + sell_trigger_gain_percent * buy_price)
#                     if f_c['high_price'] > sell_trigger_price:
#                         sell_price = sell_trigger_price * 0.997
#                         traded_by_sell_trigger = True
#                         break
#                 if not traded_by_sell_trigger:
#                     sell_price = future_candles[-1]['close_price']
#                 gain = sell_price - buy_price
#                 gain_percent = gain / buy_price
#                 gain_btc = btc_tradeable_volume * gain_percent
#                 gain_usd = gain_btc * btc_usd_price
#                 trade = {
#                     'gain_percent': gain_percent,
#                     'gain_btc': gain_btc,
#                     'gain_usd': gain_usd,
#                     'volume_traded_btc': btc_tradeable_volume,
#                     'minute': minute,
#                     'buy_time_readable': c['open_time_readable']
#                 }
#                 trades.append(trade)

#     gain_percent = sum(trade['gain_percent'] for trade in trades)
#     gain_usd = sum(trade['gain_usd'] for trade in trades)
#     return gain_percent, gain_usd, trades

# #################################################################################### PARAMS

# days = [
#     '20180124_c',
#     '20180125_c',
#     '20180126_c',
#     '20180127_c',
#     '20180128_c',
#     '20180129_c',
#     # '20180130_c',  # ('TOTAL_GAIN_PERCENT', 2.0255, 53, 3217.01)
#     # '20180131_c',  # ('TOTAL_GAIN_PERCENT', 2.0254, 64, 4891.32)
#     # '20180201'     # ('TOTAL_GAIN_PERCENT', 1.9119, 63, 3206.04)
# ]
# drops_to_collect = 1
# future_candles_length = 20 # 1
# min_volume_btc = 0
# btc_tradeable_volume_factor = 3 * 0.1 # multiplier of avg btc volume per minute over 24 hrs that we can buy & sell
# btc_usd_price = 9000
# buy_trigger_drop_percent_factor = 0.9 # * 1.003 # 2
# sell_trigger_gain_percent_factor = 0.8 # * 0.997 # 3

# print_trades = False

# #################################################################################### RUN STRATEGY

# symbols = ut.pickle_read('./botfarming/Development/binance_btc_symbols.pklz')
# symbols_filtered, symbol_list = ut2.get_trimmed_symbols(symbols, min_volume_btc)

# for d, day in enumerate(days):
#     print('------------------------------', day, '-----------------------------')
#     day_1 = day
#     try:
#         day_2 = days[d+1]
#     except IndexError:
#         break

#     symbols_not_found_day_1 = []
#     symbols_not_found_day_2 = []
#     trades_by_symbol = []
#     for s in symbols_filtered:
#         symbol = symbols_filtered[s]

#         if print_trades:
#             print('------------------------------', s, '-----------------------------')

#         data_1 = ut.pickle_read('./botfarming/Development/binance_training_data/'+ day_1 + '/'+ s +'_data_1m.pklz')
#         if data_1 == False or len(data_1) < 30:
#             if print_trades:
#                 print('no data found day 1')
#             symbols_not_found_day_1.append(s)
#         else:
#             outlier_drops = ut2.get_outlier_drops(data_1, symbol)

#             # print('OUTLIER DROPS')
#             # print('drop_percent  best_minute  best_gain_percent  avg_gain_percent')
#             # for d in outlier_drops:
#             #     print(round(d['drop_percent'], 4), d['best_minute'], round(d['best_gain_percent'], 4), round(d['avg_gain_percent'], 4))
#             # print('----------------------')

#             buy_trigger_drop_percent = outlier_drops[-1]['drop_percent'] * buy_trigger_drop_percent_factor
#             sell_trigger_gain_percent = outlier_drops[-1]['best_gain_percent'] * sell_trigger_gain_percent_factor

#             # gain_percent, gain_usd, trades = trade_on_drops(symbol, data_1, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor)
#             # print('GAIN ON CURRENT DAY DATA', s, round(gain_percent, 4), len(trades), round(gain_usd, 2))

#             data_2 = ut.pickle_read('./botfarming/Development/binance_training_data/'+ day_2 + '/'+ s +'_data_1m.pklz')
#             if data_2 == False or len(data_2) < 30:
#                 if print_trades:
#                     print('no data found day 2')
#                 symbols_not_found_day_2.append(s)
#             else:
#                 gain_percent, gain_usd, trades = trade_on_drops(symbol, data_2, future_candles_length, buy_trigger_drop_percent, sell_trigger_gain_percent, btc_tradeable_volume_factor)
#                 if print_trades:
#                     print('GAIN ON NEXT DAY DATA', s, round(gain_percent, 4), len(trades), round(gain_usd, 2))

#                 if gain_percent != 0:
#                     symbol_trades = {
#                         'gain_percent': gain_percent,
#                         'gain_usd': gain_usd,
#                         'volume_traded_btc': sum(trade['volume_traded_btc'] for trade in trades),
#                         'trade_count': len(trades),
#                         'trades': trades
#                     }
#                     trades_by_symbol.append(symbol_trades)

#     #################################################################################### GET RESULTS

#     gain_percent = round(sum(trades['gain_percent'] for trades in trades_by_symbol), 4)
#     gain_usd = round(sum(trades['gain_usd'] for trades in trades_by_symbol), 2)
#     total_trades = sum(trades['trade_count'] for trades in trades_by_symbol)
#     trades_per_symbol = round(total_trades / len(trades_by_symbol), 3)
#     volume_traded_btc = round(sum(trades['volume_traded_btc'] for trades in trades_by_symbol), 4)
#     avg_volume_btc = round(volume_traded_btc / total_trades, 6)
#     avg_gain_percent = round(gain_percent / total_trades, 4)
#     print('--------------------------------------------------------', day_2, 'Results')
#     print('TOTAL_GAIN_PERCENT', gain_percent, len(trades_by_symbol), '$', gain_usd)
#     print('symbols_traded', len(trades_by_symbol))
#     print('total_trades', total_trades)
#     print('trades_per_symbol', trades_per_symbol)
#     print('avg_volume_btc', avg_volume_btc)
#     print('avg_gain_percent', avg_gain_percent)
#     print('*buy_trigger_drop_percent', round(buy_trigger_drop_percent, 7))
#     print('*sell_trigger_gain_percent', round(sell_trigger_gain_percent, 7))
#     print('symbols_not_found_day_1', len(symbols_not_found_day_1), symbols_not_found_day_1)
#     print('symbols_not_found_day_2', len(symbols_not_found_day_2), symbols_not_found_day_2)

