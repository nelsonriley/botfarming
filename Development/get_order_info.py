#!/usr/bin/python2.7
import sys
print 'python', sys.version


import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime
from binance.client import Client


api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)

amount_to_buy = '26'
price_to_buy = '0.00030218'

print('amount to buy', amount_to_buy)

print()
print('buy')

order = client.order_limit_buy(symbol='RDNBTC', quantity=amount_to_buy, price=price_to_buy)

pprint(order)
print()

order = client.get_order(symbol=order['symbol'],orderId=order['orderId'])

pprint(order)

order = client.cancel_order(symbol='RDNBTC', orderId=order['orderId'])

pprint

pprint(order)
