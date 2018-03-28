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

length = '2h'
minutes = 120
minutes_until_sale = 8

bou.run_optimizer(length, minutes, minutes_until_sale)