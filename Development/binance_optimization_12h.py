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

length = '12h'
minutes = 12*60
max_price_to_buy_factor = .78
buy_sell_starting_gap = .055
minutes_until_sale = 3
minutes_until_sale_3 = 5
default_change_size_1 = .017
default_change_size_2 = .0085

bou.run_optimizer(length, minutes, max_price_to_buy_factor, buy_sell_starting_gap, minutes_until_sale, minutes_until_sale_3, default_change_size_1, default_change_size_2)