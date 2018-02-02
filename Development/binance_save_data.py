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

## Save data here, backtest in:
    # binance_ryan.py

# Don't forget!
datapoints_trailing = 0
min_volume = 0

# 6 mins +/- for all symbols 24hrs
save_params = [
    ['20180124_c', '2018-01-23 12:30', '2018-01-24 12:30'],
    ['20180125_c', '2018-01-24 12:30', '2018-01-25 12:30'],
    ['20180126_c', '2018-01-25 12:30', '2018-01-26 12:30'],
    ['20180127_c', '2018-01-26 12:30', '2018-01-27 12:30'],
    ['20180128_c', '2018-01-27 12:30', '2018-01-28 12:30'],
    # ['20180126', '2018-01-25 15:10', '2018-01-26 11:55'],
    # ['20180126_a', '2018-01-26 19:00', '2018-01-26 20:14'],
    # ['20180126_b', '2018-01-26 20:15', '2018-01-26 21:49'],
    # ['20180127', '2018-01-26 20:40', '2018-01-27 11:36'],
    #['20180129_c', '2018-01-28 12:30', '2018-01-29 12:30'],
    # ['20180130', '2018-01-29 11:00', '2018-01-30 11:00'],
    # ['20180130_a', '2018-01-30 16:00', '2018-01-30 19:41'],
    # ['20180130_b', '2018-01-30 20:00', '2018-01-30 20:29'],
    #['20180130_c', '2018-01-29 12:30', '2018-01-30 12:30'],
    # ['20180131', '2018-01-30 20:00', '2018-01-31 16:00'],
    # ['20180131_a', '2018-01-31 18:00', '2018-01-31 20:03'],
    # ['20180131_b', '2018-01-30 13:55', '2018-01-31 18:03'],
    # ['20180131_c', '2018-01-30 12:30', '2018-01-31 12:30'],
    # ['20180201', '2018-01-31 12:30', '2018-02-01 12:30'],
    # ['20180201_a', '2018-01-31 16:30', '2018-02-01 16:30'],
    # ['20180201_b', '2018-02-01 15:30', '2018-02-01 17:46'],
    # ['20180201_c', '2018-01-31 20:25', '2018-02-01 20:25'],
    # ['20180202', '2018-02-01 12:21', '2018-02-02 12:21']
]

########### Start End Single File Style
start_end_style = True
minute = 1

########### Step Back Style
# day_folder = '20180126'
minutes = [1]
step_backs = [2]

for settings in save_params:

    day_folder = settings[0]
    start_time = arrow.get(settings[1]).replace(tzinfo='America/Denver')
    end_time = arrow.get(settings[2]).replace(tzinfo='America/Denver')
        # file names ==> './binance_training_data/'+ day_folder + '/'+ symbol +'_data_'+str(minute)+'m.pklz'

    directory = './binance_training_data/'+day_folder
    if not os.path.exists(directory):
        os.makedirs(directory)


    if start_end_style:
        # start all
        print('start all @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        start_time_all = int(time.time())

        start = start_time.timestamp * 1000
        print('start', start, arrow.get(int(start/1000)).to('America/Denver'))
        start = start - datapoints_trailing * minute * 60 * 1000
        print('start with datapoints_trailing', start, arrow.get(int(start/1000)).to('America/Denver'))
        end = end_time.timestamp * 1000
        stop = start + 400 * minute * 60 * 1000
        last_loop = False
        if stop > end:
            stop = end
            last_loop = True
        symbols = ut.pickle_read('./binance_btc_symbols.pklz')
        coins = {}
        loops = 1
        while True:
            print('loop', loops)
            loops += 1
            for s in symbols:
                symbol = symbols[s]
                if float(symbol['24hourVolume']) > min_volume:
                    if not symbol['symbol'] in coins:
                        coins[symbol['symbol']] = []
                    # get data from binance
                    url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minute)+'m&startTime='+str(start)+'&endTime='+str(stop)
                    r = requests.get(url)
                    data = r.json()
                    if symbol['symbol'] == 'ETHBTC':
                        print('--------------------ETHBTC')
                        print(url)
                        print(len(data))
                        print(start, arrow.get(int(start/1000)).to('America/Denver'))
                        print(stop, arrow.get(int(stop/1000)).to('America/Denver'))
                        duration_in_minutes = int(stop - start)/(1000*60)
                        print('duration_in_minutes', duration_in_minutes)
                        print('--------------------ETHBTC')
                    # watch for too many API requests
                    if isinstance(data, dict):
                        print('ERROR... API Failed')
                        print(url)
                        pprint(data)
                        break
                    # add to coins[symbol] array
                    for candle in data:
                        coins[symbol['symbol']].append(candle)
            print('symbol_count =', len(coins))
            if last_loop:
                break
            # update times for next round of API requests
            start = stop
            stop = start + 400 * minute * 60 * 1000
            if stop > end:
                stop = end
                last_loop = True

        # save continuous data for each coin to disk
        for symbol in coins:
            data = coins[symbol]
            if symbol == 'ETHBTC':
                print('--------------------ETHBTC')
                print('candles =', len(data), '...should be', 12 * 60 + 230)
                print('first candle')
                pprint(data[0])
                print('last candle')
                pprint(data[-1])
                print('--------------------ETHBTC')
            ut.pickle_write('./binance_training_data/'+ day_folder + '/'+ symbol +'_data_'+str(minute)+'m.pklz', data)

        # end all
        print('end all @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        print('elapsed:', int(time.time()) - start_time_all, 'seconds')

    ################################################################################

    if not start_end_style:
        run_time = 0
        data_sets = 0
        for i in range(0, len(minutes)):
            step_back = step_backs[i]
            run_time += step_back * 80
            data_sets += step_back
        run_time = round(run_time / 60, 2)
        print('estimated run time:', run_time, 'minutes for', data_sets, 'datasets')

        # Notes
            # 80s to save each step_back
            # 1m = 6 hrs per step_back
            # 30m = 8 days per step_back

        # start all
        print('start all @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        start_time_all = int(time.time())

        symbols = ut.pickle_read('./binance_btc_symbols.pklz')
        for i in range(0, len(minutes)):
            minute = minutes[i]
            for step_back in range(0, step_backs[i]):

                end_time_period = int(time.time())*1000-400*60*1000*minute*step_back
                start_time_period = (end_time_period-400*60*1000*minute)

                print('save: {symbol}_data_'+str(minute)+'m_p'+str(step_back)+'.pklz')
                # start
                print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                start_time = int(time.time())

                for s in symbols:
                    symbol = symbols[s]

                    #get data from binance
                    url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minute)+'m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period)
                    r = requests.get(url)
                    data = r.json()

                    # watch for too many API requests
                    if isinstance(data, dict):
                        print('ERROR... API Failed')
                        print(url)
                        pprint(data)
                        break

                    #write out to file
                    ut.pickle_write('./binance_training_data/'+ day_folder + '/'+ symbol['symbol'] +'_data_'+str(minute)+'m_p'+str(step_back)+'.pklz',data)
                    # print('# step_back', step_back, 'symbol', symbol['symbol'])

                # end
                print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                print('elapsed:', int(time.time()) - start_time, 'seconds')

        # end all
        print('end all @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        secs = int(time.time()) - start_time_all
        print('elapsed:', secs, 'seconds', round(secs/60, 2), 'minutes')

print('------------------done')

