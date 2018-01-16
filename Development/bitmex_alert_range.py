#!/usr/bin/python2.7

import functions as fn
import bitmex_lib as bm
import time
import datetime

high_alert = 16000
low_alert = 15500

upper_bollinger = False
lower_bollinger = True

server_utc = True

##############################################

# params
do_print = True
loop_duration = 10
loop_interval = 1

##############################################

# loop
loop = True
i = 0
while loop:
    # get data
    price = bm.get_first_sell_price()
    frames = bm.get_smart_chart(hours_history=1, resolution_minutes=15, do_print=False, go_back_minutes=0)
    f_prev = frames[-1]
    epoch = int(time.time())
    if server_utc:
        epoch = epoch - (7 * 60 * 60)
    readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%c')

    # bollinger alerts
    if upper_bollinger and price >= f_prev['boll_upper']:
        fn.twilio_send_sms('Price ABOVE BOLLINGER'+str(f_prev['boll_upper'])+' '+readable_time)
        loop = False
    if lower_bollinger and price <= f_prev['boll_lower']:
        fn.twilio_send_sms('Price BELOW BOLLINGER'+str(f_prev['boll_lower'])+' '+readable_time)
        loop = False

    # price alerts
    if price >= high_alert:
        fn.twilio_send_sms('Price ABOVE '+str(high_alert)+' '+readable_time)
        loop = False
    if price <= low_alert:
        fn.twilio_send_sms('Price BELOW '+str(low_alert)+' '+readable_time)
        loop = False

    # i'm still working
    if do_print and i == 0:
        print '# price', price, 'alerts (', low_alert, '-', high_alert, ') bollingers (', f_prev['boll_lower'], '-', f_prev['boll_upper'], ')', readable_time

    # loop
    if False:
        loop = False
    else:
        i += 1
        if i == loop_interval:
            i = 0
        time.sleep(10)
