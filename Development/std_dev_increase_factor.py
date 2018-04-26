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

while True:

    std_dev_increase_factor = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor')

    last_three_trades = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/variables/last_three_trades')
    
    if int(time.time()) - last_three_trades[-1] > 10*60*60:
        std_dev_increase_factor += 0.1
    else:
        std_dev_increase_factor = 0 # this is also done when trade completes, extra safe
        
    if std_dev_increase_factor > 1:
        std_dev_increase_factor = 1
        
    ut.pickle_write('/home/ec2-user/environment/botfarming/Development/variables/std_dev_increase_factor'
        , std_dev_increase_factor)
    
    print('std_dev_increase_factor', std_dev_increase_factor, ut.get_time())

    time.sleep(60)