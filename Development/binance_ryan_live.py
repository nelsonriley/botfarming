#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut

file_number = 0
total_files = 4
overlap = 1
length = '1m'

ut.run_bot_parallel(file_number, total_files)