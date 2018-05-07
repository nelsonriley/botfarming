#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility_3 as ut
from binance.client import Client

# INDICATOR BOT #
indicator_bot = 1
file_number = 0
total_files = 1
length = '12h'
api_key = '41EwcPBxLxrwAw4a4W2cMRpXiQwaJ9Vibxt31pOWmWq8Hm3ZX2CBnJ80sIRJtbsI'
api_secret = 'pnHoASmoe36q54DZOKsUujQqo4n5Ju25t5G0kBaioZZgGDOQPEHqgDDPA6s5dUiB'
client = Client(api_key, api_secret)

ut.run_bot_parallel(file_number, length, total_files, client, indicator_bot)