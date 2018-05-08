#!/usr/bin/python2.7
import sys
print 'python', sys.version
import time
import utility_3 as ut
from pprint import pprint
from os import listdir
from os.path import isfile, join





while True:
    
    while time.localtime().tm_sec > 2 or time.localtime().tm_sec < 1:
        time.sleep(.5)
    
    lengths = ['1m', '5m', '15m', '30m', '1h', '2h', '6h', '12h', '1d']
    
    for length in lengths:
        
        if length == '1m':
            max_trades_allowed = 35
            max_std_increase = 1
        elif length == '5m':
            max_trades_allowed = 25
            max_std_increase = 1
        elif length == '15m':
            max_trades_allowed = 10
            max_std_increase = 1
        elif length == '30m':
            max_trades_allowed = 12
            max_std_increase = 1
        elif length == '1h':
            max_trades_allowed = 11
            max_std_increase = 1
        elif length == '2h':
            max_trades_allowed = 7
            max_std_increase = 1
        elif length == '6h':
            max_trades_allowed = 6
            max_std_increase = 1
        elif length == '12h':
            max_trades_allowed = 6
            max_std_increase = 1
        elif length == '1d':
            max_trades_allowed = 6
            max_std_increase = 1

        indicator_trades = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/indicator_trades_'+length)
        
        std_dev_increase_factor = max(0,round((float(max_trades_allowed)-float(len(indicator_trades)))*max_std_increase/float(max_trades_allowed),1))
        
        #std_dev_increase_factor = 0 
            
        ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor_'+length, std_dev_increase_factor)
        
        print('std_dev_increase_factor_' + length, std_dev_increase_factor, ut.get_time())
    
    time.sleep(30)