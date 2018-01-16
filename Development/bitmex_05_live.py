#!/usr/bin/python2.7

# Dec 15, we are running this for the next 15 days :)
import time
import datetime
import bitmex_lib as bm
import functions as fn
import pprint
pp = pprint.PrettyPrinter(indent=2)

# params (from Backtests)
consecutive_lower_open_close_centers = 3
below_boll_trigger_fraction = 1.4
min_boll_width_fraction = 0.02

funding_fee_piggy_bank_btc = 0
stop_loss_at = -2900
max_lev = 5.0

# preferences
send_early_alerts = False
server_utc = True

# use this if you need to restart
buy_price = 0

############################################################

# vars
trades = []
draw_down_price = 99999999
early_alert_triggered = False
boll_width_fraction = 99999999

# state
state = 'liquid'
res = bm.get_positions(do_print=True)
if len(res) > 0:
    qty = res[0]['currentQty']
else:
    qty = 0
if qty > 0:
    print 'holding positions, entering state: long'
    state = 'long'
else:
    print 'state is liquid'

loop = True
i = 0
while loop:
    # get frames + time
    frames = bm.get_smart_chart(hours_history=1, resolution_minutes=15, do_print=False, go_back_minutes=0)
    epoch = int(time.time())
    if server_utc:
        epoch = epoch - (7 * 60 * 60)
    readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%c')
    if False:
        fn.print_pretty_dict(frames[-1])
        print '---'

    # data + calcs
    price = bm.get_first_sell_price()
    f_prev = frames[-1]
    low_gap = (f_prev['boll_middle'] - f_prev['boll_lower']) * below_boll_trigger_fraction
    gap = f_prev['boll_lower'] - price
    do_buy = gap >= low_gap
    do_buy_price = f_prev['boll_lower'] - low_gap
    do_buy_price_early_alert = f_prev['boll_lower'] - (low_gap * 0.5)
    buy_trigger_price = f_prev['boll_lower'] - low_gap
    draw_down_price = 99999999
    boll_width_fraction = (f_prev['boll_middle'] - f_prev['boll_lower']) / f_prev['boll_middle']

    # print every few minutes
    if True and i == 0:
        print '----------------------'
        print '#', readable_time
        print '# buy at', round(do_buy_price, 0), '(', round(do_buy_price-price, 0), ') PRICE', price, 'state', state, 'low_gap', round(low_gap, 0), '(', round(boll_width_fraction * 100, 2), '%  vs', round(min_boll_width_fraction * 100, 2), '%)', 'gap', round(gap, 0), 'do_buy', do_buy
        print '# oc_centers_in_row', f_prev['consecutive_lower_open_close_centers'], '(', consecutive_lower_open_close_centers, 'needed) below_boll_trigger_fraction', below_boll_trigger_fraction, 'lev', max_lev
        print '# prev frame time', f_prev['time_human']
        print '# prev frame O H L C', f_prev['open'], f_prev['high'], f_prev['low'], f_prev['close']
        print '# prev frame boll m u l', f_prev['boll_middle'], f_prev['boll_upper'], f_prev['boll_lower']

    # "maybe you should watch your computer" alerts
    if send_early_alerts:
        if price <= do_buy_price_early_alert and not early_alert_triggered:
            fn.twilio_send_sms(readable_time+' Price is half way below lower bollinger towards buy price! Things could happen soon! price '+str(price)+' low_bollinger '+str(f_prev['boll_lower']))
            early_alert_triggered = True
        if price > do_buy_price_early_alert:
            early_alert_triggered = False

    # trade logic
    if state == 'liquid':
        # the "trade frame" looks at previous frame to determine buy criteria
        if f_prev['consecutive_lower_open_close_centers'] >= consecutive_lower_open_close_centers:
            if boll_width_fraction >= min_boll_width_fraction:
                if do_buy:
                    state = 'go_long'
                    fn.twilio_send_sms(readable_time+' DO BUY TRIGGERED')
                    # BUY
                    bm.update_leverage(max_lev)
                    res = bm.get_user_margin()
                    btc = float(res['availableMarginBtc']) - funding_fee_piggy_bank_btc
                    qty = int(round(btc * (price - price * 0.01) * max_lev, 0))
                    buy_price = price + 5
                    print 'BUY! qty', qty, 'btc', btc, 'price', price, 'lev', max_lev
                    fn.twilio_send_sms(readable_time+' BUY! qty '+str(qty)+' btc '+str(btc)+' at price '+str(price)+' with leverage '+str(max_lev))
                    order = bm.place_order(qty=qty, price=buy_price, side='Buy', do_print=True)
                    state = 'long'
    if state == 'long':
        # calculate max draw down per trade
        if price < draw_down_price:
            draw_down_price = price
        # SELL for profit
        if price >= f_prev['boll_upper']:
            state = 'go_liquid'
        # SELL for safety
        elif price < buy_price + stop_loss_at:
            state = 'go_liquid'
        if state == 'go_liquid':
            res = bm.get_positions()
            qty = res[0]['currentQty']
            sell_price = price - 5
            print 'SELL! qty', qty, 'price', price, 'lev', max_lev
            fn.twilio_send_sms(readable_time+' SELL! qty '+str(qty)+' at price '+str(price)+' with leverage '+str(max_lev))
            order = bm.place_order(qty=qty, price=sell_price, side='Sell', do_print=True)
            state = 'liquid'

    # loop
    if False:
        loop = False
    else:
        i += 1
        if i == 10:
            i = 0
        time.sleep(10)
