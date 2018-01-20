#!/usr/bin/python2.7
import sys
print 'python', sys.version
from pprint import pprint
import utility as ut
import requests
import time
import os

day_folder = '20180118'
minutes = [30]
step_backs = [8]

directory = './binance_training_data/'+day_folder
if not os.path.exists(directory):
    os.makedirs(directory)

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

