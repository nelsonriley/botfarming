#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut

file_number = 5
total_files = 6
overlap = 2
length = '1m'

ut.run_bot(file_number, total_files, overlap, length)