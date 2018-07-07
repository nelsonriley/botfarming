#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility_3 as ut
from binance.client import Client

file_number = 0
total_files = 1
length = '1m'
api_key = 'OTOejkqQJK2QXMM4Bax0MGLETj8sdDZOpU5iUNLyrUxUtE9DiZFAPSr0jBclImph'
api_secret = '1gyl8xogyuCsMhbMwzGY6QMjOTxDdcwk5ugCqem9vFEeVJEL3KNppAxJniVUmQBV'
client = Client(api_key, api_secret)

ut.run_bot_parallel(file_number, length, total_files, client)