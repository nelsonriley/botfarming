import json
from django.http import StreamingHttpResponse
import pickle
import gzip
from django.views.decorators.csrf import csrf_exempt
import time
import datetime
import os

@csrf_exempt
def updateprofit(request):
    if request.method=='GET':
        # you can't write to folders in the web app unless they already exist
        # you can write to folders outside of the web app
        pickle_file_path = '/home/nelsonriley/Development/binance_profit_graph/profits.pklz'
        is_file = os.path.isfile(pickle_file_path)
        if not is_file:
            #save the file first time
            f = gzip.open(pickle_file_path,'wb')
            pickle.dump([], f)
            f.close()
        profit = float(request.GET.get('profit', '0'))
        epoch = int(time.time()) - 7 * 60 * 60
        readable_time = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
        #read
        f = gzip.open(pickle_file_path,'rb')
        data_points = pickle.load(f)
        f.close()
        #update
        data = {
            'epoch': epoch,
            'readable_time': readable_time,
            'profit': profit
        }
        data_points.append(data)
        #write
        f = gzip.open(pickle_file_path,'wb')
        pickle.dump(data_points, f)
        f.close()
        #respond
        return StreamingHttpResponse('profit logged: '+ str(profit));
    if request.method=='POST':
        received_json_data=json.loads(request.body)
        #write out to file
        f = gzip.open('test.pklz','wb')
        pickle.dump(received_json_data,f)
        f.close()
        return StreamingHttpResponse('it was post request: '+str(received_json_data))
    return StreamingHttpResponse('please use POST request')