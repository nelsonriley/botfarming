import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip

# 1m & 30m
day = '20180110'

# 1m_p8 :: 6 hrs per step_back :: 80s per step_back
minutes = 1
step_backs = 8

# 30m_p1 :: 8 days per step_back :: 80s per step_back
    # minutes = 30
    # step_backs = 8

# setup
symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()

for step_back in range(0, step_backs):

    end_time_period = int(time.time())*1000-400*60*1000*minutes*step_back
    start_time_period = (end_time_period-400*60*1000*minutes)

    # start
    print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start_time = int(time.time())

    for symbol in symbol_data['symbols']:

        if symbol['quoteAsset'] == 'BTC':
            #get data from binance
            url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minutes)+'m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period)
            print('data url', url)
            r = requests.get(url)
            data = r.json()

            #write out to file
            f = gzip.open('./binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz','wb')
            pickle.dump(data,f)
            f.close()
            print('# step_back', step_back, 'symbol', symbol['symbol'])

    # end
    print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('elapsed:', int(time.time()) - start_time, 'seconds')

print('------------------done')
