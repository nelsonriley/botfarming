import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip


def buy_coin(symbol):

    datapoints_trailing = 8
    volume_increase = 7.3
    movement_percentage = 9.5
    minutes_until_sale = 6
    minutes = 1

    end_time = int(time.time())*1000
    start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))

    url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol +'&interval='+str(minutes)+'m&startTime='+str(start_time)+'&endTime='+str(end_time)

    print('data url', url)
    r = requests.get(url)
    data = r.json()


    trailing_volumes = []
    trailing_movement = []
    for index,candle in enumerate(data):
        # compare
        if len(trailing_volumes) >= datapoints_trailing:

            print(symbol)

            trail_vol_avg = numpy.mean(trailing_volumes)

            current_movement = float(candle[4])-float(candle[1])
            current_movement_percentage = current_movement/float(candle[1])

            # print('current_movement_percentage', current_movement_percentage)
            # print('currrent volume', candle[5])
            # print('trail_vol_avg', trail_vol_avg)
            # print()

            if float(candle[5]) > trail_vol_avg*volume_increase and current_movement_percentage < -.001*movement_percentage:

                print('')
                print('buy',symbol)
                pprint(trailing_volumes)
                print('current volume', candle[5])
                print('trailing volume avg', trail_vol_avg)
                #print(candle[4],',',data[index + 1][4],',',data[index + 2][4],',',data[index + 3][4],',',data[index + 4][4])
                #print(candle[4],',',data[index - 1][4],',',data[index - 2][4],',',data[index - 3][4],',',data[index - 4][4])
                print(index)

                sys.exit()

            if int(time.time())%60 > 30 and float(candle[5]) < trail_vol_avg:
                return False
            else:
                return True

        # update
        if len(trailing_volumes) <= datapoints_trailing:
            trailing_volumes.append(float(candle[5]))
        if len(trailing_volumes) > datapoints_trailing:
            break
            #del trailing_volumes[0]
            #del trailing_movement[0]


def buy_coin_test(symbol):

    datapoints_trailing = 8
    volume_increase = 7.3
    movement_percentage = 9.5
    minutes_until_sale = 6
    minutes = 1

    end_time = int(time.time())*1000
    start_time = (end_time-60*1000*minutes*(datapoints_trailing+1))

    url = 'https://api.binance.com/api/v1/klines?symbol='+ symbol +'&interval='+str(minutes)+'m&startTime='+str(start_time)+'&endTime='+str(end_time)

    print('data url', url)
    r = requests.get(url)
    data = r.json()


    trailing_volumes = []
    trailing_movement = []
    for index,candle in enumerate(data):
        # compare
        if len(trailing_volumes) >= datapoints_trailing:

            print(symbol)

            trail_vol_avg = numpy.mean(trailing_volumes)

            current_movement = float(candle[4])-float(candle[1])
            current_movement_percentage = current_movement/float(candle[1])

            print(candle[5])
            # print('current_movement_percentage', current_movement_percentage)
            # print('currrent volume', candle[5])
            # print('trail_vol_avg', trail_vol_avg)
            # print()

            if float(candle[5]) > trail_vol_avg*volume_increase and current_movement_percentage < -.001*movement_percentage:

                print('')
                print('buy',symbol)
                pprint(candle)
                epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
                readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
                print(readable_time)
                pprint(trailing_volumes)
                print('current volume', candle[5])
                print('trailing volume avg', trail_vol_avg)
                #print(candle[4],',',data[index + 1][4],',',data[index + 2][4],',',data[index + 3][4],',',data[index + 4][4])
                #print(candle[4],',',data[index - 1][4],',',data[index - 2][4],',',data[index - 3][4],',',data[index - 4][4])
                print(index)

                sys.exit()

            if int(time.time())%60 > 30 and float(candle[5]) < trail_vol_avg:
                return False
            else:
                return True

        # update
        if len(trailing_volumes) <= datapoints_trailing:
            trailing_volumes.append(float(candle[5]))
        if len(trailing_volumes) > datapoints_trailing:
            break
            #del trailing_volumes[0]
            #del trailing_movement[0]
