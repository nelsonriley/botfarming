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

# history periods
step_backs = 9

# params
params = {}
params['datapoints_trailing'] = datapoints_trailing = 20
params['trailing_price_range_max_percent'] = trailing_price_range_max_percent = 0.2
params['movement_multiplier'] = movement_multiplier = 5
params['movement_multiplier_ceiling'] = movement_multiplier_ceiling = 15
params['movement_percent'] = movement_percent = 0.06
params['future_window'] = future_window = 20
params['sell_skip'] = sell_skip = 10
params['sell_retract_by'] = sell_retract_by = 0.1
pprint(params)

# printing
print_every_trade = False
print_all_trades_stats = False

for step_back in range(0, step_backs + 1):
    #reporting
    wins = []
    losses = []
    capital = 1
    for symbol in symbol_data['symbols']:
        if symbol['quoteAsset'] == 'BTC':
            # python 2 pickle can not load the file dumped by python 3 pickle
            f = gzip.open('./binance_data/'+ symbol['symbol'] +'_data_30m_p'+str(step_back)+'.pklz','rb')
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

                    # current calcs  high - open
                    current_movement = float(candle[2])-float(candle[1])

                    # conditions
                    green_bar = current_movement > 0
                    range_ok = trail_price_range_percent < trailing_price_range_max_percent
                    mov_ceiling_ok = current_movement < movement_multiplier_ceiling * trail_mov_avg
                    mov_ok = current_movement > movement_multiplier * trail_mov_avg
                    mov_price = float(candle[1]) + movement_multiplier * trail_mov_avg
                    mov_percent_ok = current_movement / float(candle[1]) > movement_percent
                    mov_percent_price = float(candle[1]) + float(candle[1]) * movement_percent

                    # prevent buying when already holding (tested)
                    no_trade_overlap = False
                    if not future_index or future_index and future_index < index:
                        no_trade_overlap = True
                        future_index = False

                    if range_ok and mov_ceiling_ok and mov_ok and mov_percent_ok and no_trade_overlap and green_bar:

                        # sell rule 1: buy as soon as both conditions are met
                        if mov_price > mov_percent_price:
                            buy_price = mov_price
                        else:
                            buy_price = mov_percent_price

                        # sell rule 2: always buy at close of bar
                        # buy_price = float(candle[4])

                        epoch = int(round(int(candle[0]) / 1000)) - 7 * 60 * 60
                        readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

                        # get future candles
                        future_candles = []
                        future_index = index + future_window
                        for i in range(1, future_window + 1):
                            try:
                                future_candles.append(data[index + i])
                            except IndexError:
                                if print_every_trade:
                                    print('future candle out of range')

                        # determine sell price with rules that could be executed live
                        # skip first *3
                        # then sell whenever price retracts *50% from high
                        future_max = float(candle[2])
                        future_min = float(candle[3])
                        sell_price = False
                        if len(future_candles) > sell_skip:
                            for i, c in enumerate(future_candles):
                                open_price = float(c[1])
                                high_price = float(c[2])
                                low_price = float(c[3])
                                close_price = float(c[4])
                                if i >= sell_skip:
                                    rise = future_max - buy_price
                                    do_sell_price = future_max - rise * sell_retract_by
                                    if rise < 0 or open_price < do_sell_price:
                                        sell_price = open_price
                                        break
                                    if low_price <= do_sell_price:
                                        sell_price = do_sell_price
                                        break
                                if high_price > future_max:
                                    future_max = high_price
                                if low_price < future_min:
                                    future_min = low_price
                            if not sell_price:
                                last_candle_close = float(future_candles[-1][4])
                                sell_price = last_candle_close
                            gain = sell_price - buy_price
                            gain_percent = round(gain / buy_price, 3)
                        else:
                            sell_price = 0
                            gain = 0
                            gain_percent = 0

                        # update stats
                        if gain_percent > 0:
                            wins.append(gain_percent)
                        if gain_percent <= 0:
                            losses.append(gain_percent)
                        capital = capital * (1 + gain_percent)

                        # print trade
                        if print_every_trade:
                            print('')
                            print('buy', symbol['symbol'], readable_time)
                            print('trail_price_range_percent', round(trail_price_range_percent, 1), trailing_price_range_max_percent)
                            print('trail_mov_avg', trail_mov_avg, current_movement, round(current_movement/trail_mov_avg, 1))
                            print('buy_price', buy_price)
                            print('sell_price', sell_price)
                            print('gain_percent', gain_percent)
                            print('capital', capital)

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