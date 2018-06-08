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

ut.increase_std_dev_increase_factor(0)