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
future_window = 20

#reporting
wins = []
losses = []
capital = 1

for symbol in symbol_data['symbols']:
    if symbol['quoteAsset'] == 'BTC':
        f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_data/'+ symbol['symbol'] +'_data_30m_p'+str(step_backs)+'.pklz','rb')
        #f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_data/'+ symbol['symbol'] +'_data_30m.pklz','rb')
        data = pickle.load(f)
        f.close()

        trailing_volumes = []
        trailing_movement = []
        trailing_opens = []
        trailing_highs = []
        trailing_lows = []
        trailing_closes = []
        future_index = False

        for index, candle in enumerate(data):
            # compare
            if len(trailing_volumes) >= datapoints_trailing:
                # if we ever want to store candles
                # trailing_volumes = list(map(lambda c: float(c[5]), candles))

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

                # current calcs
                current_movement = float(candle[4])-float(candle[1])

                # conditions
                range_ok = trail_price_range_percent < trailing_price_range_max_percent
                mov_ok = current_movement > movement_multiplier * trail_mov_avg
                mov_price = float(candle[1]) + movement_multiplier * trail_mov_avg
                mov_percent_ok = current_movement / float(candle[1]) > movement_percent
                mov_percent_price = float(candle[1]) + float(candle[1]) * movement_percent

                # tested, working : prevent buying when already holding
                no_trade_overlap = False
                if not future_index or future_index and future_index < index:
                    no_trade_overlap = True
                    future_index = False

                if range_ok and mov_ok and mov_percent_ok and no_trade_overlap:
                    epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
                    readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

                    # buy as soon as both conditions are met
                    if mov_price > mov_percent_price:
                        buy_price = mov_price
                    else:
                        buy_price = mov_percent_price

                    print('')
                    print('buy', symbol['symbol'], readable_time)
                    print('trail_price_range_percent', round(trail_price_range_percent, 1), trailing_price_range_max_percent)
                    print('trail_mov_avg', trail_mov_avg, current_movement, round(current_movement/trail_mov_avg, 1))
                    print('buy_price', buy_price)
                    future_candles = []
                    future_index = index + future_window
                    for i in range(1, future_window + 1):
                        try:
                            future_candles.append(data[index + i])
                        except IndexError:
                            print('future candle out of range')
                    future_min = 99999999
                    future_max = 0
                    if len(future_candles) > 0:
                        for c in future_candles:
                            if float(c[2]) > future_max:
                                future_max = float(c[2])
                            if float(c[3]) < future_min:
                                future_min = float(c[3])
                        sell_price = (future_max + future_min) / 2
                        gain = sell_price - buy_price
                        gain_percent = round(gain / buy_price, 3)
                    else:
                        sell_price = 0
                        gain = 0
                        gain_percent = 0
                    print('sell_price', sell_price)
                    print('gain_percent', gain_percent)
                    if gain_percent > 0:
                        wins.append(gain_percent)
                    if gain_percent <= 0:
                        losses.append(gain_percent)
                    capital = capital * (1 + gain_percent)
                    print('capital', capital)

                    #pprint(trailing_volumes)
                    #print('current volume', data[index][5])
                    #print('trailing volume avg', trail_vol_avg)
                    #pprint(trailing_movement)
                    # print('current_movement', current_movement)
                    # print(candle[4],',',data[index + 1][4],',',data[index + 2][4],',',data[index + 3][4],',',data[index + 4][4])
                    # print(candle[4],',',data[index - 1][4],',',data[index - 2][4],',',data[index - 3][4],',',data[index - 4][4])
                    # print('index', index)

                    # if float(data[index + 1][4]) - float(candle[4]) > 0:
                    #     print('win')
                    #     wins += 1
                    # else:
                    #     print('loss')
                    #     losses += 1

                    # break

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


print('')
print('wins', len(wins))
print('losses', len(losses))
print('total', len(wins) + len(losses))
win_avg = round(numpy.mean(wins), 3)
win_max = round(numpy.max(wins), 3)
win_sum = round(numpy.sum(wins), 3)
loss_avg = round(numpy.mean(losses), 3)
loss_min = round(numpy.min(losses), 3)
loss_sum = round(numpy.sum(losses), 3)
print('win_avg', win_avg)
print('win_max', win_max)
print('win_sum', win_sum)
print('loss_avg', loss_avg)
print('loss_min', loss_min)
print('loss_sum', loss_sum)
print('capital x', round(capital, 1))
capital_sum = 1 + loss_sum + win_sum
print('capital_sum x', capital_sum)
#print("datapoints trailing:", datapoints_trailing)
#print("volume increase:", volume_increase)
#print(numpy.mean(percent_increase_prev_win))
#pprint(percent_increase_prev_win)
#print(numpy.mean(percent_increase_prev_loss))
#pprint(percent_increase_prev_loss)
print('done')
