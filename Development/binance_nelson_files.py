import requests
import time
from pprint import pprint
import numpy
import sys
import pickle
import gzip
import datetime

print(isinstance({},dict))
print(isinstance(None,dict))

pickle_file_path = '/home/nelsonriley/Development/binance_profit_graph/profits.pklz'
pickle_file_path = '/home/ec2-user/environment/botfarming/Development/program_state_1m/program_state_1m_3_SALTBTC.pklz'
pickle_file_path = '/home/ec2-user/environment/botfarming/Development/program_state_1m/test.pklz'

f = gzip.open(pickle_file_path,'wb')
#pickle.dump({'epoch': 1515612763, 'profit': 0, 'readable_time': '2018-01-10 19:32:43'}, f)
pickle.dump(False, f)
f.close()

f = gzip.open(pickle_file_path,'rb')
data = pickle.load(f)
print('DATA----------------')
pprint(data)
f.close()







# symbol = 'ADABTC'

# f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_data/'+ symbol +'_data_30m.pklz','rb')
# data = pickle.load(f)
# f.close()

# f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_data/'+ symbol +'_data_30m_p0.pklz','rb')
# data1 = pickle.load(f)
# f.close()

# f = gzip.open('/home/ec2-user/environment/botfarming/Development/binance_data/'+ symbol +'_data_30m_p1.pklz','rb')
# data2 = pickle.load(f)
# f.close()

# print('len(data)', len(data))
# print('len(data1)', len(data1))
# print('len(data2)', len(data2))
