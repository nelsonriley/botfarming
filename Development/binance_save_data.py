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

########### General
day_folder = '20180124'

########### Start End Single File Style
start_end_style = True
datapoints_trailing = 230
minute = 1
start_time = arrow.get('2018-01-23 23:00').replace(tzinfo='America/Denver')
end_time = arrow.get('2018-01-24 11:00').replace(tzinfo='America/Denver')
# file names ==> './binance_training_data/'+ day_folder + '/'+ symbol +'_data_'+str(minute)+'m.pklz'

########### Step Back Style
minutes = [1]
step_backs = [2]

#############################################################################

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
    symbols = ut.pickle_read('./binance_btc_symbols.pklz')
    coins = {}
    last_loop = False
    loops = 1
    while True:
        print('loop', loops)
        loops += 1
        # Test: symbols = { 'BQXBTC': { 'symbol': 'BQXBTC' } }
        for s in symbols:
            symbol = symbols[s]
            if not symbol['symbol'] in coins:
                coins[symbol['symbol']] = []
            # get data from binance
            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minute)+'m&startTime='+str(start)+'&endTime='+str(stop)
            r = requests.get(url)
            data = r.json()
            if symbol['symbol'] == 'BQXBTC':
                print(url)
                print(len(data))
                print(start, arrow.get(int(start/1000)).to('America/Denver'))
                print(stop, arrow.get(int(stop/1000)).to('America/Denver'))
                duration_in_minutes = int(stop - start)/(1000*60)
                print('duration_in_minutes', duration_in_minutes)
            # watch for too many API requests
            if isinstance(data, dict):
                print('ERROR... API Failed')
                print(url)
                pprint(data)
                break
            # add to coins[symbol] array
            for candle in data:
                coins[symbol['symbol']].append(candle)
        if last_loop:
            break
        # update times for next API request
        start = stop
        stop = start + 400 * minute * 60 * 1000
        if stop > end:
            stop = end
            last_loop = True

    # save continuous data for each coin to disk
    for symbol in coins:
        data = coins[symbol]
        if symbol == 'BQXBTC':
            print('candles =', len(data), '...should be', 12 * 60 + 230)
            print('first candle')
            pprint(data[0])
            print('last candle')
            pprint(data[-1])
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
    print('elapsed:', int(time.time()) - start_time_all, 'seconds')

print('------------------done')

