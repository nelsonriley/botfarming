


import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip


symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()


for past in range(1,9):

    best_datapoints = 0
    best_volume = 0
    best_movement = 0
    best_minutes = 0

    best_gain = 0

    for datapoints_trailing in range(6, 11):
    #datapoints_trailing = 8

        for volume_increase in range(8, 13):
        #volume_increase = 10

            for movement_percentage in range(9,14):
            #movement_percentage = 11

                for minutes_until_sale in range(3,8):
                #minutes_until_sale = 5

                    wins = 0
                    losses = 0

                    current_movement_win = []
                    current_movement_loss = []

                    percentage_made_win = []
                    percentage_made_loss = []

                    for symbol in symbol_data['symbols']:
                        if symbol['quoteAsset'] == 'BTC':


                            ##create function below combine with bincance_ryan

                            f = gzip.open('./binance_data/'+ symbol['symbol'] +'_data_1m_p'+ str(past) +'.pklz','rb')
                            data = pickle.load(f)
                            f.close()

                            trailing_volumes = []
                            trailing_movement = []
                            for index,candle in enumerate(data):
                                # compare
                                if len(trailing_volumes) >= datapoints_trailing:
                                    trail_vol_avg = numpy.mean(trailing_volumes)
                                    trail_vol_std = numpy.std(trailing_volumes)
                                    trail_vol_max = numpy.max(trailing_volumes)

                                    trail_mov_max = numpy.max(trailing_movement)

                                    current_movement = float(candle[4])-float(candle[1])
                                    current_movement_percentage = current_movement/float(candle[1])

                                    try:
                                        gotdata = data[index + minutes_until_sale]
                                    except IndexError:
                                        break

                                    if float(candle[5]) > trail_vol_avg*volume_increase and current_movement_percentage < -.001*movement_percentage:

                                        ##print('')
                                        ##print('buy',symbol['symbol'])
                                        # pprint(trailing_volumes)
                                        # print('current volume', data[index][5])
                                        # print('trailing volume avg', trail_vol_avg)
                                        # pprint(trailing_movement)
                                        # print('current movement', current_movement)
                                        # print('trail movement max',trail_mov_max)
                                        ##print(candle[4],',',data[index + 1][4],',',data[index + 2][4],',',data[index + 3][4],',',data[index + 4][4])
                                        ##print(candle[4],',',data[index - 1][4],',',data[index - 2][4],',',data[index - 3][4],',',data[index - 4][4])
                                        # print(index)

                                        percentage_made = (float(data[index + minutes_until_sale][4]) - float(candle[4]))/float(candle[4])


                                        if percentage_made > 0:
                                            #current_movement_win.append(current_movement_percentage)
                                            percentage_made_win.append(percentage_made)
                                            #print('win')
                                            wins += 1
                                        else:
                                            #current_movement_loss.append(current_movement_percentage)
                                            percentage_made_loss.append(percentage_made)
                                            #print('loss')
                                            losses += 1

                                        break

                                # update
                                if len(trailing_volumes) <= datapoints_trailing:
                                    trailing_volumes.append(float(candle[5]))
                                    trailing_movement.append(abs(float(candle[4])-float(candle[1])))
                                if len(trailing_volumes) > datapoints_trailing:
                                    del trailing_volumes[0]
                                    del trailing_movement[0]




                    current_gain = wins*numpy.mean(percentage_made_win)-losses*numpy.mean(percentage_made_loss)

                    if current_gain > best_gain:
                        best_gain = current_gain
                        best_datapoints = datapoints_trailing
                        best_volume = volume_increase
                        best_movement = movement_percentage
                        best_minutes = minutes_until_sale

                    # print("gain:", gain)
                    # print("minutes_until_sale:", minutes_until_sale)
                    # print("movement_percentage:", movement_percentage*-.001)
                    # print("datapoints trailing:", datapoints_trailing)
                    # print("volume increase:", volume_increase)
                    # print('wins:',wins)
                    # #print(numpy.mean(current_movement_win))
                    # #pprint(current_movement_win)
                    # print(numpy.mean(percentage_made_win))
                    # #pprint(percentage_made_win)
                    # print('losses:',losses)
                    # #print(numpy.mean(current_movement_loss))
                    # #pprint(current_movement_loss)
                    # print(numpy.mean(percentage_made_loss))
                    # #pprint(percentage_made_loss)
                    # print('wins/losses', wins/losses)
                    # print()

    print("past:", past)
    print("gain:", best_gain)
    print("minutes_until_sale:", best_minutes)
    print("movement_percentage:", best_movement)
    print("datapoints trailing:", best_datapoints)
    print("volume increase:", best_volume)
    print()


print('done')
