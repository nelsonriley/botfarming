#!/usr/bin/python2.7
import sys
print('python', sys.version)

import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime
import utility_3 as ut
import functions_financial as fn
import binance_optimization_utility as bou

length = '1m'
minutes = 1
max_price_to_buy_factor = .97
buy_sell_starting_gap = .006
minutes_until_sale = 12
minutes_until_sale_3 = 14
default_change_size_1 = .002
default_change_size_2 = .001

bou.run_optimizer(length, minutes, max_price_to_buy_factor, buy_sell_starting_gap, minutes_until_sale, minutes_until_sale_3, default_change_size_1, default_change_size_2)