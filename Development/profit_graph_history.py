# #!/usr/bin/python2.7
# import sys
# print('python', sys.version)
import pickle
import gzip
import time
import os
from datetime import datetime
from pprint import pprint
#import utility as ut
import numpy
# from twisted.internet import task
# from twisted.internet import reactor
# import functions as fn
# import requests
# import pprint
# import hashlib
# import hmac
# import urllib
# from binance.client import Client

file_path = './binance_profit_graph/profits.pklz'
f = gzip.open(file_path,'rb')
data_points = pickle.load(f)
pprint(data_points)
f.close()
