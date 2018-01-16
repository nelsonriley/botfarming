import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip

# custom time period
directory = './binance_training_data/30m_20180114_0000_to_1900/'
minutes = 30
# 7:30 until 9:45 (use epochtimeconverter.com or some shit)
end_time_period = 1515956400000
start_time_period = 1515888000000

# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())

# setup
symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()

for symbol in symbol_data['symbols']:

    if symbol['quoteAsset'] == 'BTC':
        #get data from binance
        url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol['symbol'] +'&interval='+str(minutes)+'m&startTime='+str(start_time_period)+'&endTime='+str(end_time_period)
        r = requests.get(url)
        data = r.json()

        #write out to file
        f = gzip.open(directory+symbol['symbol']+'.pklz','wb')
        pickle.dump(data,f)
        f.close()
        print(symbol['symbol'])

# end
print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print('elapsed:', int(time.time()) - start_time, 'seconds')

print('------------------done')
