#!/usr/bin/python2.7
import sys
from pprint import pprint
import binance_optimization_utility as bou

# optimize using average of 12 periods for all time periods

lengths = ['30m', '1h', '2h']
bou.run_optimizer_multi(lengths,0)