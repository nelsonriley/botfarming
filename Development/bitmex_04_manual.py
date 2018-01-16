#!/usr/bin/python2.7
import schedule
import time
import datetime
import bitmex_lib as bm
import functions as fn
import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

max_lev = 6.0
# pretty json toggle: control + command + j

# bm.get_positions()
price = bm.get_first_sell_price()
# print 'price', price
# res = bm.get_user_wallet()
res = bm.get_user_margin(do_print=False)
btc = res['availableMarginBtc']
qty = int(round(btc * (price - price * 0.01) * max_lev, 0))
print 'qty', qty, 'btc', btc, 'price', price, 'max_lev', max_lev
# bitcoin = res['amount_bitcoins']
# bm.update_leverage(6.0)
bm.place_order(qty=1, price=10000, side='Buy')
# bm.place_order(qty=1, price=13300, side='Sell')
# bm.cancel_all_orders()
# time.sleep(1)
# bm.get_positions()
