#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut

file_number = 4
total_files = 8
overlap = 5
length = '30m'

ut.run_bot(file_number, total_files, overlap, length)