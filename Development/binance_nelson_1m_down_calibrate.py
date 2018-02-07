import requests
import time
from pprint import pprint
import numpy
import pickle
import gzip
import datetime

# params
minutes = 1
step_backs = 8
day = '20180110'

# test params
params = {}
dt_tests = [4,5,7,8,9,10,11,13,15]
# 1
mm_tests = [2,3,4,5,7,9,11,13,15,17]
#mm_tests = [0.99,0.98,0.97,0.96,0.94,0.90]

# printing
print_every_trade = 0
print_all_trades_stats = 0

# list of coins
symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()

for dt in dt_tests:
    params['datapoints_trailing'] = datapoints_trailing = dt

    # start
    print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start_time = int(time.time())

    for mm in mm_tests:
        params['movement_multiplier'] = movement_multiplier = mm

        all_periods_wins = []
        all_periods_losses = []

        for step_back in range(0, step_backs):

            #reporting
            wins = []
            losses = []
            capital = 1

            for symbol in symbol_data['symbols']:

                if symbol['quoteAsset'] == 'BTC':

                    f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_training_data/'+ day + '/'+ symbol['symbol'] +'_data_'+str(minutes)+'m_p'+str(step_back)+'.pklz','rb')
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

                            # trailing calcs
                            d = {}
                            d['trail_mov_avg'] = trail_mov_avg = numpy.mean(trailing_movement)
                            d['trail_mov_avg_percent'] = trail_mov_avg_percent = round(trail_mov_avg / float(candle[1]), 4)

                            # current calcs  open - low
                            d['current_movement'] = current_movement = float(candle[1]) - float(candle[3])

                            # time stamp
                            epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
                            readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

                            # if range_ok and trail_mov_avg_percent_max_ok and mov_ok:
                            # 2
                            movement_multiplier_trigger_price = float(candle[1]) - movement_multiplier * trail_mov_avg
                            if float(candle[3]) < movement_multiplier_trigger_price:
                                # if float(candle[3]) < float(candle[1]) * movement_multiplier:

                                # buy rule
                                # 3
                                buy_price = movement_multiplier_trigger_price * 1
                                # buy_price = float(candle[1]) * movement_multiplier

                                # sell rule
                                try:
                                    next_candle_open = float(data[index + 1][1])
                                    sell_price = next_candle_open * 1
                                    gain = sell_price - buy_price
                                    gain_percent = round(gain / buy_price, 4)
                                except IndexError:
                                    # no trade if no next candle
                                    buy_price = 0
                                    sell_price = 0
                                    gain = 0
                                    gain_percent = 0

                                # update stats
                                if gain_percent > 0:
                                    wins.append(gain_percent)
                                    all_periods_wins.append(gain_percent)
                                if gain_percent < 0:
                                    losses.append(gain_percent)
                                    all_periods_losses.append(gain_percent)
                                capital = capital * (1 + gain_percent)

                                # print trade
                                if print_every_trade:
                                    print('')
                                    print('buy', symbol['symbol'], readable_time)
                                    print('trail_mov_avg_percent', d['trail_mov_avg_percent'])
                                    print('trail_price_range_percent', d['trail_price_range_percent'])
                                    print('current_movement_multiplier', d['current_movement_multiplier'])
                                    print('current_percent', d['current_percent'])
                                    print('gain_percent', gain_percent)
                                    print('----')
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

            # final reporting
            total_trades = len(wins) + len(losses)
            win_avg = win_max = win_sum = 0
            if len(wins):
                win_avg = round(numpy.mean(wins), 3)
                win_max = round(numpy.max(wins), 3)
                win_sum = round(numpy.sum(wins), 3)
            loss_avg = loss_min = loss_sum = 0
            if len(losses):
                loss_avg = round(numpy.mean(losses), 3)
                loss_min = round(numpy.min(losses), 3)
                loss_sum = round(numpy.sum(losses), 3)
            capital_sum = round(1 + loss_sum + win_sum, 2)
            if (print_all_trades_stats):
                print('')
                print('wins', len(wins))
                print('losses', len(losses))
                print('total_trades', total_trades)
                print('win_avg', win_avg)
                print('win_max', win_max)
                print('win_sum', win_sum)
                print('loss_avg', loss_avg)
                print('loss_min', loss_min)
                print('loss_sum', loss_sum)
                print('capital x', round(capital, 1))
                print('capital_sum x', capital_sum)

            # print 1 line to track results
            print('#', step_back, total_trades, '(', len(wins), '/', len(losses), ')', 'capital_sum x', capital_sum, 'loss_min', loss_min, 'win_avg', win_avg, 'win_max', win_max, '*', round(capital, 1))

        # print all period results
        all_periods_trades = len(all_periods_wins) + len(all_periods_losses)
        all_periods_win_avg = all_periods_win_max = all_periods_win_min = all_periods_win_sum = 0
        if len(all_periods_wins):
            all_periods_win_avg = round(numpy.mean(all_periods_wins), 3)
            all_periods_win_max = round(numpy.max(all_periods_wins), 3)
            all_periods_win_sum = round(numpy.sum(all_periods_wins), 3)
        all_periods_loss_avg = all_periods_loss_min = all_periods_loss_max = all_periods_loss_sum = 0
        if len(all_periods_losses):
            all_periods_loss_avg = round(numpy.mean(all_periods_losses), 3)
            all_periods_loss_min = round(numpy.min(all_periods_losses), 3)
            all_periods_loss_sum = round(numpy.sum(all_periods_losses), 3)
        all_periods_capital_sum = round(1 + all_periods_loss_sum + all_periods_win_sum, 2)
        print('-------------------------------')
        print('#> trailing', datapoints_trailing)
        print('#> movement', movement_multiplier)
        print('#', all_periods_trades, '(', len(all_periods_wins), '/', len(all_periods_losses), ')', 'capital_sum_x', all_periods_capital_sum, 'loss_min', all_periods_loss_min, 'win_avg', all_periods_win_avg, 'win_max', all_periods_win_max)
        print('')

    print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('elapsed:', int(time.time()) - start_time, 'seconds')
