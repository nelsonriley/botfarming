#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut

file_number = 2
total_files = 3
overlap = 2
length = '30m'

ut.run_bot(file_number, total_files, overlap, length)