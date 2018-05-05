#!/usr/bin/python2.7
import sys
print 'python', sys.version
import time
import utility_3 as ut
from pprint import pprint
from os import listdir
from os.path import isfile, join

# if not trade in last 10 min
# increase std_dev_increase_factor by 0.1 with a max of 2

ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor', 0)

while time.localtime().tm_sec > 2 or time.localtime().tm_sec < 1:
    time.sleep(.5)


while True:

    std_dev_increase_factor = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor')

    last_trade_start_overall = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/last_trade_start_overall')
    
    print('last_trade_start_overall', ut.get_readable_time(last_trade_start_overall))
    
    if int(time.time()) - last_trade_start_overall > 3*60:
        if int(time.time()) - last_trade_start_overall < 7*60:
            std_dev_increase_factor += 0.05
        elif int(time.time()) - last_trade_start_overall < 11*60:
            std_dev_increase_factor += 0.1
        else:
            std_dev_increase_factor += 0.2
    else:
        std_dev_increase_factor = 0 # this is also done when trade completes, extra safe
        
    if std_dev_increase_factor > 4:
        std_dev_increase_factor = 4
        
    ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor', std_dev_increase_factor)
    
    print('std_dev_increase_factor', std_dev_increase_factor, ut.get_time())

    time.sleep(60)