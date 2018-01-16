import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime

symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()

#params  5.9x  26
datapoints_trailing = 20
trailing_price_range_max_percent = 0.10
movement_multiplier = 5
movement_percent = 0.08
future_window = 10

# params  3445x  141
datapoints_trailing = 20
trailing_price_range_max_percent = 0.15
movement_multiplier = 5
movement_percent = 0.06
future_window = 20

# params
    # 0 32361  198
    # 1 321    171
    # 2 33239  204
    # 3 33.6   135
    # 4 25.2   121
    # 5 24.0   109
    # 6 2.8    82
    # 7 103    121
    # 8 4.4    73
    # 9 2.4    45
step_backs = 0
datapoints_trailing = 20
trailing_price_range_max_percent = 0.2
movement_multiplier = 5
movement_percent = 0.05

for periods_until_sale in range(1,40):
#periods_until_sale = 9

    #reporting
    wins = []
    losses = []

    for symbol in symbol_data['symbols']:
        if symbol['quoteAsset'] == 'BTC':
            f = gzip.open('./binance_data/'+ symbol['symbol'] +'_data_30m_p'+str(step_backs)+'.pklz','rb')
            #f = gzip.open('./binance_data/'+ symbol['symbol'] +'_data_30m.pklz','rb')
            data = pickle.load(f)
            f.close()

            trailing_volumes = []
            trailing_movement = []
            trailing_opens = []
            trailing_highs = []
            trailing_lows = []
            trailing_closes = []
            future_index = False
            for index,candle in enumerate(data):
                # compare
                if len(trailing_volumes) >= datapoints_trailing:
                    # trailing_volumes = list(map(lambda x: float(x[5]), items))
                    trail_vol_avg = numpy.mean(trailing_volumes)
                    trail_vol_std = numpy.std(trailing_volumes)
                    trail_vol_max = numpy.max(trailing_volumes)

                    trail_mov_avg = numpy.mean(trailing_movement)
                    trail_mov_max = numpy.max(trailing_movement)
                    trail_mov_min = numpy.min(trailing_movement)

                    trail_price_max = numpy.max(trailing_highs)
                    trail_price_min = numpy.min(trailing_lows)
                    trail_price_range = trail_price_max - trail_price_min
                    trail_price_range_percent = trail_price_range / trail_price_max

                    current_movement = float(candle[4])-float(candle[1])

                    # if float(candle[5]) > trail_vol_avg*volume_increase and trail_mov_max*4 < current_movement and current_movement > 0:
                    #saying its flat
                    range_ok = trail_price_range_percent < trailing_price_range_max_percent

                    price_ok = float(candle[2]) > float(candle[1]) + movement_multiplier * trail_mov_avg
                    price_price = float(candle[1]) + movement_multiplier * trail_mov_avg

                    mov_ok = (float(candle[2]) - float(candle[1])) / float(candle[1]) > movement_percent
                    mov_price = float(candle[1]) * (1 + movement_percent)

                    try:
                        gotdata = data[index + periods_until_sale]
                    except IndexError:
                        break

                    if range_ok and price_ok and mov_ok:
                        buy_price = max(price_price, mov_price)
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

                        percentage_made = (float(data[index + periods_until_sale][4]) - buy_price)/float(buy_price)


                        if percentage_made > 0:
                            #current_movement_win.append(current_movement_percentage)
                            #percentage_made_win.append(percentage_made)
                            #print('win')
                            wins.append(percentage_made)
                        else:
                            #current_movement_loss.append(current_movement_percentage)
                            #percentage_made_loss.append(percentage_made)
                            #print('loss')
                            losses.append(percentage_made)

                        break

                # update
                if len(trailing_volumes) <= datapoints_trailing:
                    trailing_volumes.append(float(candle[5]))
                    trailing_movement.append(abs(float(candle[4])-float(candle[1])))
                    trailing_opens.append(float(candle[1]))
                    trailing_highs.append(float(candle[2]))
                    trailing_lows.append(float(candle[3]))
                    trailing_closes.append(float(candle[4]))
                if len(trailing_volumes) > datapoints_trailing:
                    del trailing_volumes[0]
                    del trailing_movement[0]
                    del trailing_opens[0]
                    del trailing_highs[0]
                    del trailing_lows[0]
                    del trailing_closes[0]
            future_index = False

    print('')
    print('periods until sale:', periods_until_sale)
    print('wins', len(wins))
    win_sum = round(numpy.sum(wins), 3)
    win_avg = round(numpy.mean(wins), 3)
    print('losses', len(losses))
    losses_sum = round(numpy.sum(losses), 3)
    loss_avg = round(numpy.mean(losses), 3)
    print('total', len(wins) + len(losses))
    print('wins/losses', len(wins)/len(losses))

print('done')
