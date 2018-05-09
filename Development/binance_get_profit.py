#!/usr/bin/python2.7
import sys
import time
import os
import datetime
from pprint import pprint
import utility_3 as ut3
from binance.client import Client

################################## BINANCE GET PROFIT

api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)

acct_info = client.get_account()
prices = client.get_all_tickers()
# pprint(acct_info)
# pprint(prices)

## earlier in time
# ryan_btc_before_bots = 6.21201378 + 3.18120133 + 0.13423430603 + 0.20798 - 0.61213 + 2.38472954 + 2.21955718 + 2.11721460 # 9.23021912
# ryans_symbols = { 'BNB': 494.00943559 }
## 20180422
# ryan_btc_before_bots = 6.21201378 + 3.18120133 + 0.13423430603 + 0.20798 - 0.61213 + 2.38472954 + 2.21955718 + 2.11721460 - 4.07636575
# ryans_symbols = { 'BNB': 210.21609545, 'XVG': 409685 }
## 20180505
ryan_btc_before_bots = 14.186409436
ryans_symbols = { 'BNB': 363.04951434 }

coins_held = 0
bot_value = 0
for balance in acct_info['balances']:
    if balance['asset'] == 'BTC':
        bot_value += float(balance['free'])
        print('BTC holding', float(balance['free']))
        coins_held += 1
    elif float(balance['free']) > 0 or float(balance['locked']) > 0:
        for price in prices:
            if price['symbol'] == balance['asset'] + 'BTC':
                qty = float(balance['free']) + float(balance['locked'])
                if balance['asset'] in ryans_symbols:
                    qty = qty - ryans_symbols[balance['asset']]
                coin_value = float(price['price']) * qty
                if coin_value > 0.05:
                    print float(balance['locked']), float(balance['free']), balance['asset'], coin_value
                bot_value += coin_value
                coins_held += 1
                break
        pass

profit = bot_value - ryan_btc_before_bots
print('coins_held', coins_held)
print('bot_value', bot_value)
print('ryan_btc_before_bots', ryan_btc_before_bots)
print('profit BTC', profit, '$', profit * 9800)