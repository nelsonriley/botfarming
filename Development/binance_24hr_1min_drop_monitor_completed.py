#!/usr/bin/python2.7
import sys
print('python', sys.version)
import pickle
import gzip
import time
import os
import datetime
from pprint import pprint
import utility as ut
import utility_2 as ut2

# buy_triggered_live_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/buys_triggered_live.pklz'
# buys_triggered_live = ut.pickle_read(buy_triggered_live_path)
# buy_triggered_sim_path = '/home/ec2-user/environment/botfarming/Development/binance_24hr_1min_drop/buys_triggered_sim.pklz'
# buys_triggered_sim = ut.pickle_read(buy_triggered_sim_path)

# look_back_minutes = 10