


import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime


past = 0
datapoints_trailing = 8
volume_increase = 8
movement_percentage = 0
minutes_until_sale = 6
trail_vol_min = 4

end_time = int(time.time())*1000
start_time = (end_time-30*60*1000)

url = 'https://api.binance.com/api/v1/klines?symbol=OSTBTC&interval=1m&startTime='+str(start_time)+'&endTime='+str(end_time)

print('data url', url)
r = requests.get(url)
data = r.json()

trailing_volumes = []
trailing_movement = []
for index,candle in enumerate(data):
    # compare
    if len(trailing_volumes) >= datapoints_trailing:

        trail_vol_avg = numpy.mean(trailing_volumes)

        current_movement = float(candle[4])-float(candle[1])
        current_movement_percentage = current_movement/float(candle[1])

        try:
            gotdata = data[index + minutes_until_sale]
        except IndexError:
            break

        epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
        readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
        print(readable_time)
        print('current_movement_percentage',current_movement_percentage)
        print('trail_vol_avg',trail_vol_avg)
        print(candle[5])
        print()

        if float(candle[5]) > trail_vol_avg*volume_increase and current_movement_percentage < -.001*movement_percentage and trail_vol_avg > trail_vol_min*100:

            #print('')
            #print('buy',symbol['symbol'])
            pprint(trailing_volumes)
            print('current volume', data[index][5])
            print('trailing volume avg', trail_vol_avg)
            pprint(trailing_movement)
            print('current movement', current_movement)
            #print(candle[4],',',data[index + 1][4],',',data[index + 2][4],',',data[index + 3][4],',',data[index + 4][4])
            #print(candle[4],',',data[index - 1][4],',',data[index - 2][4],',',data[index - 3][4],',',data[index - 4][4])
            print(index)
            epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
            readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
            print(readable_time)
            print('buy price', candle[4])
            print('sell price', data[index + minutes_until_sale][4])


            percentage_made = (float(data[index + minutes_until_sale][4]) - float(candle[4]))/float(candle[4])

            print('percentage_made', percentage_made)

            sys.exit()

    # update
    if len(trailing_volumes) <= datapoints_trailing:
        trailing_volumes.append(float(candle[5]))
        trailing_movement.append(abs(float(candle[4])-float(candle[1])))
    if len(trailing_volumes) > datapoints_trailing:
        del trailing_volumes[0]
        del trailing_movement[0]



print('done')
