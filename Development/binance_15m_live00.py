#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut

file_number = 0
total_files = 3
overlap = 2
length = '15m'

ut.run_bot(file_number, total_files, overlap, length)