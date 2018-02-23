#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility_3 as ut

file_number = 0
total_files = 1
length = '12h'

ut.run_bot_parallel(file_number, length, total_files)