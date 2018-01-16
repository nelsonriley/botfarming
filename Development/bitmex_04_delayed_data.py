# backtest 15 min strategy
# "big tiered drop then midd bollinger reversal"
# buy
    # 5 lower open-close-centers in a row on 15min chart
    # && price is below low_boll by (mid_boll - low_boll)*0.33
# sell (for profit)
    # price hits upper bollinger
# sell (for safety)
    # negative a big number (like 1000, worst case)

import schedule
import time
import datetime
import bitmex_lib as bm
import functions as fn
import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

# strategy params (tested variations)

# 15 min chart from 2017-12-02 18:35:00 to 2017-12-04 18:35:00
# 192 frames in 48 hours
# profit = $ 53448.0 5.345 % 2 pos 0 neg of 2 capital 50000 lev 20
hours_history = 24 * 2
consecutive_lower_open_close_centers = 4
below_boll_trigger_fraction = 0.33
stop_loss_at = -1500

# 15 min chart from 2017-12-02 18:45:00 to 2017-12-04 18:45:00
# 192 frames in 48 hours
# profit = $ 67377.0 6.738 % 1 pos 0 neg of 1 capital 50000 lev 20
hours_history = 24 * 2
consecutive_lower_open_close_centers = 4
below_boll_trigger_fraction = 0.7
stop_loss_at = -1500

# 15 min chart from 2017-11-28 18:45:00 to 2017-12-04 18:45:00
# 576 frames in 144 hours
# profit = $ 203937.0 20.394 % 3 pos 0 neg of 3 capital 50000 lev 20
hours_history = 24 * 6
consecutive_lower_open_close_centers = 4
below_boll_trigger_fraction = 0.7
stop_loss_at = -1500

# data url https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=5&from=1509906900&to=1512516900
# NEWS Cancel plans for bitcoin hard fork (nov 8)
# 2017-11-05 17:15:00 to 2017-12-05 17:15:00 ( 15 min chart)
# 2880 frames in 720 hours ( 30.0 days)
# compounded return => ROI 44.58 %
# compounded profit => ROE 619.34 %  profit $ 309671.0 with 0 orders limited by 25.0 %  rule
# return => ROI 37.87 % : 12 pos 0 neg of 12
# profit => ROE 227.22 % @ 6 x lev with $ 50000 capital, profit = $ 113612.0 with 0 orders limited by 25.0 %  rule
# period return => ROI 58.93 % $ 4360.4 ( 7399.1 to 11759.5 )
# period profit => ROE 147.33 % @ 2.5 x lev with $ 50000 capital, profit = $ 73664.0
# period draw down => 21.93 %  $ 1743.5 over 79.0 hours
# draw down => avg 2.91 %  max 8.82 %  min 0.22 %
# hours held => avg 5.92 max 11.0 min 3.0
    # 1 data url https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=5&from=1507315800&to=1509925800
    # 2017-10-06 18:15:00 to 2017-11-05 17:15:00 ( 15 min chart)
    # 2880 frames in 720 hours ( 30.0 days)
    # compounded return => ROI 10.0 %
    # compounded profit => ROE 73.52 %  profit $ 36758.0 with 0 orders limited by 25.0 %  rule
    # return => ROI 9.6 % : 8 pos 1 neg of 9
    # profit => ROE 57.61 % @ 6 x lev with $ 50000 capital, profit = $ 28804.0 with 0 orders limited by 25.0 %  rule
    # period return => ROI 69.51 % $ 3034.1 ( 4365 to 7399.1 )
    # period profit => ROE 173.77 % @ 2.5 x lev with $ 50000 capital, profit = $ 86887.0
    # period draw down => 13.82 %  $ 826.7 over 131.0 hours
    # draw down => avg 1.62 %  max 4.96 %  min 0.01 %
    # hours held => avg 8.0 max 21.0 min 5.0
        # NEWS China shuts down all exchanges (sep 15) I bought at 3100, nice
        # 2 data url https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=5&from=1504723800&to=1507333800
        # 2017-09-06 18:15:00 to 2017-10-06 18:15:00 ( 15 min chart
        # 2880 frames in 720 hours ( 30.0 days)
        # compounded return => ROI 12.26 %
        # compounded profit => ROE 89.81 %  profit $ 44907.0 with 0 orders limited by 25.0 %  rule
        # return => ROI 11.75 % : 12 pos 3 neg of 15
        # profit => ROE 70.49 % @ 6 x lev with $ 50000 capital, profit = $ 35246.0 with 0 orders limited by 25.0 %  rule
        # period return => ROI -5.31 % $ -245 ( 4610 to 4365 )
        # period profit => ROE -13.29 % @ 2.5 x lev with $ 50000 capital, profit = $ -6643.0
        # period draw down => 37.32 %  $ 1750.0 over 170.0 hours
        # draw down => avg 1.98 %  max 7.67 %  min 0.02 %
        # hours held => avg 8.33 max 17.0 min 3.0
            # 3 data url https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=5&from=1502132700&to=1504742700
            # 2017-08-07 18:15:00 to 2017-09-06 18:15:00 ( 15 min chart)
            # 2880 frames in 720 hours ( 30.0 days)
            # compounded return => ROI 12.72 %
            # compounded profit => ROE 96.55 %  profit $ 48276.0 with 1 orders limited by 25.0 %  rule
            # return => ROI 12.21 % : 9 pos 3 neg of 12
            # profit => ROE 73.24 % @ 6 x lev with $ 50000 capital, profit = $ 36618.0 with 0 orders limited by 25.0 %  rule
            # period return => ROI 36.43 % $ 1231.1 ( 3378.9 to 4610 )
            # period profit => ROE 91.09 % @ 2.5 x lev with $ 50000 capital, profit = $ 45544.0
            # period draw down => 18.99 %  $ 952.0 over 72.0 hours
            # draw down => avg 3.08 %  max 8.9 %  min 0.0 %
            # hours held => avg 8.42 max 19.0 min 3.0
hours_history = 24 * 7
consecutive_lower_open_close_centers = 4
below_boll_trigger_fraction = 1.0
stop_loss_at = -1500
capital = 140000
max_lev = 8
max_lev_period = 2.5
volume_allowed_per_bar = 0.25

###############################################

go_back_minutes = 0 * 30 * 24 * 60
frames = bm.get_smart_chart(hours_history, resolution_minutes=15, do_print=False, go_back_minutes=go_back_minutes)

# period stats
below_boll_count = 0
above_boll_count = 0
period_local_max = 0
period_local_min = 99999999
period_local_start = 0
period_local_end = 0
period_max_draw_down = 0
period_max_draw_down_percent = 0
period_local_hours = 0

# trade vars (liquid, long, short, go_long, go_short, go_liquid)
trades = []
start_state = 'liquid'
state = start_state
capital_compounded = capital
buy_price = 0
contracts = 0
contracts_compounded = 0
contracts_limited = 0
contracts_compounded_limited = 0
gain_percent_compounded = 1
draw_down_price = 99999999

# run strategy
if True:
    f_prev = False
    for f in frames:
        # TEST / DEBUG
        # print f['time_human'], f['open'], f['high'], f['open_close_center'], f['consecutive_lower_open_close_centers']

        # STATS LOGIC
        if f['low'] < f['boll_lower']:
            below_boll_count += 1
        if f['high'] > f['boll_upper']:
            above_boll_count += 1
        if f['high'] > period_local_max:
            period_local_max = f['high']
            period_local_start = f['time_epoch']
            # @ new high, reset min
            period_local_min = 99999999
        if f['low'] < period_local_min:
            period_local_min = f['low']
            period_local_end = f['time_epoch']
        draw_down = period_local_max - period_local_min
        draw_down_percent = draw_down / period_local_max
        if draw_down_percent > period_max_draw_down_percent:
            period_max_draw_down_percent = draw_down_percent
            period_max_draw_down = draw_down
            period_local_hours = (period_local_end - period_local_start) / 60 / 60

        # TRADE LOGIC
        # buy
            # 5 lower open-close-centers in a row on 15min chart
            # && price is below low_boll by (mid_boll - low_boll)*0.7
        # sell (for profit)
            # price hits upper bollinger
        # sell (for safety)
            # negative a big number (like 1000, worst case)
        if state == 'liquid':
            # the "trade frame" looks at previous frame to determine buy criteria
            if not f_prev is False:
                if f['consecutive_lower_open_close_centers'] >= consecutive_lower_open_close_centers:
                    low_gap = (f_prev['boll_middle'] - f_prev['boll_lower']) * below_boll_trigger_fraction
                    if f_prev['boll_lower'] - f['low'] >= low_gap:
                        state = 'go_long'
                        buy_price = f_prev['boll_lower'] - low_gap
        if state == 'long':
            # calculate max draw down per trade
            if f['low'] < draw_down_price:
                draw_down_price = f['low']
            # sell for profit
            if f['high'] >= f['boll_upper']:
                sell_price = f['boll_upper']
                state = 'go_liquid'
            # sell for safety
            elif f['low'] < buy_price + stop_loss_at:
                sell_price = buy_price + stop_loss_at
                state = 'go_liquid'
            # record the trade
            if state == 'go_liquid':
                gain_percent = (sell_price - buy_price) / buy_price
                gain_percent_compounded = gain_percent_compounded * (1 + gain_percent)
                profit_compounded = gain_percent * contracts_compounded
                capital_compounded = capital_compounded + profit_compounded
                trades.append({
                    'buy_price': buy_price,
                    'buy_time_epoch': buy_time_epoch,
                    'buy_time_human': buy_time_human,
                    'contracts': contracts,
                    'contracts_compounded': contracts_compounded,
                    'contracts_as_coins': contracts / buy_price,
                    'contracts_limited': contracts_limited,
                    'contracts_compounded_limited': contracts_compounded_limited,
                    'sell_price': sell_price,
                    'sell_time_epoch': f['time_epoch'],
                    'sell_time_human': f['time_human'],
                    'profit': contracts * gain_percent,
                    'profit_compounded': profit_compounded,
                    'gain': sell_price - buy_price,
                    'gain_percent': gain_percent,
                    'gain_percent_compounded': gain_percent_compounded,
                    'hours_held': (f['time_epoch'] - buy_time_epoch) / 60 / 60,
                    'draw_down_price': draw_down_price,
                    'draw_down': buy_price - draw_down_price,
                    'draw_down_percent': (buy_price - draw_down_price) / buy_price,
                    'capital_compounded': capital_compounded,
                    'buy_bar_volume': buy_bar_volume,
                    'sell_bar_volume': f['volume']
                    })
                state = 'liquid'
                draw_down_price = 99999999
                contracts_limited = 0
                contracts_compounded_limited = 0
        if state == 'go_long':
            # calculate max draw down per trade
            if f['low'] < draw_down_price:
                draw_down_price = f['low']
            # buy contracts
            # print '###', f['volume']
            # print '###', contracts, capital * max_lev, contracts, capital_compounded * max_lev
            contracts_avail = f['volume'] * volume_allowed_per_bar
            contracts = capital * max_lev
            contracts_compounded = capital_compounded * max_lev
            if contracts > contracts_avail:
                contracts = contracts_avail
                contracts_limited = 1
            if contracts_compounded > contracts_avail:
                contracts_compounded = contracts_avail
                contracts_compounded_limited = 1
            buy_time_epoch = f['time_epoch']
            buy_time_human = f['time_human']
            buy_bar_volume = f['volume']
            state = 'long'
        f_prev = f


# trade stats
profit = 0
gain_percent = 0
trades_pos = 0
trades_neg = 0
hours_held_max = 0
hours_held_min = 99999999
hours_held_total = 0
draw_down_percent_max = 0
draw_down_max = 0
draw_down_percent_min = 99999999
draw_down_min = 99999999
draw_down_percent_total = 0
contracts_limited = 0
contracts_compounded_limited = 0
for t in trades:
    if t['gain'] >= 0:
        trades_pos += 1
    if t['gain'] < 0:
        trades_neg += 1
    if t['draw_down_percent'] > draw_down_percent_max:
        draw_down_percent_max = t['draw_down_percent']
        draw_down_max = t['draw_down']
    if t['draw_down_percent'] < draw_down_percent_min:
        draw_down_percent_min = t['draw_down_percent']
        draw_down_min = t['draw_down']
    if t['hours_held'] > hours_held_max:
        hours_held_max = t['hours_held']
    if t['hours_held'] < hours_held_min:
        hours_held_min = t['hours_held']
    profit += t['profit']
    gain_percent += t['gain_percent']
    contracts_limited += t['contracts_limited']
    contracts_compounded_limited += t['contracts_compounded_limited']
    hours_held_total += t['hours_held']
    draw_down_percent_total += t['draw_down_percent']
hours_held_avg = hours_held_total / float(len(trades))
draw_down_percent_avg = draw_down_percent_total / float(len(trades))
capital_compounded = trades[-1]['capital_compounded']
profit_compounded = capital_compounded - capital
profit_compounded_roe = profit_compounded / capital
gain_percent_compounded = trades[-1]['gain_percent_compounded'] - 1


if True:
    ROE = profit / capital
    price_gain = frames[-1]['close'] - frames[0]['open']
    price_gain_percent = float(price_gain) / frames[0]['open']
    period_roe = price_gain_percent * max_lev_period
    period_profit = capital * price_gain_percent * max_lev_period
    max_lev_period_b = 8
    period_roe_b = price_gain_percent * max_lev_period_b
    period_profit_b = capital * price_gain_percent * max_lev_period_b
    print '# compounded return => ROI', round(gain_percent_compounded * 100, 2), '%'
    print '# compounded profit => ROE', round(profit_compounded_roe * 100, 2), '%  profit $', round(profit_compounded, 0), 'with', contracts_compounded_limited, 'orders limited by', round(volume_allowed_per_bar * 100, 2), '%  rule'
    print '# return => ROI', round(gain_percent * 100, 2), '% :', trades_pos, 'pos', trades_neg, 'neg of', len(trades)
    print '# profit => ROE', round(ROE * 100, 2), '% @', max_lev, 'x lev with $', capital, 'capital, profit = $', round(profit, 0), 'with', contracts_limited, 'orders limited by', round(volume_allowed_per_bar * 100, 2), '%  rule'
    print '# period return => ROI', round(price_gain_percent * 100, 2), '% $', price_gain, '(', frames[0]['open'], 'to', frames[-1]['close'], ')'
    print '# period profit => ROE', round(period_roe * 100, 2), '% @', max_lev_period, 'x lev with $', capital, 'capital, profit = $', round(period_profit, 0)
    print '# period profit => ROE B', round(period_roe_b * 100, 2), '% @', max_lev_period_b, 'x lev with $', capital, 'capital, profit = $', round(period_profit_b, 0)
    print '# period draw down =>', round(period_max_draw_down_percent * 100, 2), '%  $', period_max_draw_down, 'over', round(period_local_hours, 3), 'hours'
    print '# draw down => avg', round(draw_down_percent_avg * 100, 2), '%  max', round(draw_down_percent_max * 100, 2), '%  min', round(draw_down_percent_min * 100, 2), '%'
    print '# hours held => avg', round(hours_held_avg, 2), 'max', round(hours_held_max, 2), 'min', round(hours_held_min, 2)
    if True:
        print '# ----------------------------'
        i = 1
        for t in trades:
            print '#', i, t['buy_time_human'], 'to', t['sell_time_human'], ':', round(t['buy_price'], 0), 'to', round(t['sell_price'], 0), round(t['gain_percent'] * 100, 2), '%', t['hours_held'], 'hrs', round(t['draw_down_percent']*100, 2), '%  down'
            i += 1
    if False:
        for t in trades:
            print '---------------------'
            fn.print_pretty_dict(t)
    # print 'below_boll_count', below_boll_count, 'of', len(frames), round(float(below_boll_count) / len(frames) * 100, 2), '%'
    # print 'above_boll_count', above_boll_count, 'of', len(frames), round(float(above_boll_count) / len(frames) * 100, 2), '%'
