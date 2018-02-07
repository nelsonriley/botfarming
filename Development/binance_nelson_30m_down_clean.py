import requests
import time
from pprint import pprint
import numpy
import pickle
import gzip
import datetime

# start
print('start @',  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
start_time = int(time.time())

# list of coins
symbol_url = "https://api.binance.com/api/v1/exchangeInfo"
symbol_r = requests.get(symbol_url)
symbol_data = symbol_r.json()

# configuration
minutes = 30
step_backs = 2
day = '20180110'

# params
params = {}
params['datapoints_trailing'] = datapoints_trailing = 20
params['movement_multiplier'] = movement_multiplier = 7
pprint(params)

# printing
print_every_trade = 1
print_all_trades_stats = 1

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

                    # trigger
                    movement_multiplier_trigger_price = float(candle[1]) - movement_multiplier * trail_mov_avg
                    if float(candle[3]) < movement_multiplier_trigger_price:

                        # buy rule
                        buy_price = movement_multiplier_trigger_price * 1

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
                        if gain_percent < 0:
                            losses.append(gain_percent)
                        capital = capital * (1 + gain_percent)

                        # print trade
                        if print_every_trade:
                            # print('')
                            print('buy', symbol['symbol'], readable_time)
                            # print('trail_mov_avg_percent', d['trail_mov_avg_percent'])
                            # print('trail_price_range_percent', d['trail_price_range_percent'])
                            # print('current_movement_multiplier', d['current_movement_multiplier'])
                            # print('current_percent', d['current_percent'])
                            # print('gain_percent', gain_percent)
                            # print('----')
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

print('end @', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print('elapsed:', int(time.time()) - start_time, 'seconds')