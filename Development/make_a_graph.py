from pprint import pprint
import pylab
import pickle
import gzip
import time
import os
import datetime
from pprint import pprint
#import utility as ut
import numpy

file_path = '/home/ec2-user/environment/botfarming/Development/binance_profit_graph/profits.pklz'
f = gzip.open(file_path,'rb')
data_points = pickle.load(f)
pprint(data_points)
f.close()

hours_ago_to_plot = [24, 48, 96, 192]

for hours in hours_ago_to_plot:

    one_day_ago = datetime.datetime.fromtimestamp(int(time.time())-7*60*60-hours*60*60).strftime('%Y-%m-%d %H:%M:%S')

    data_for_plot = []
    for data in data_points:
        if data['readable_time'] > one_day_ago:
            data_for_plot.append(data['profit'])

    pprint(data_for_plot)

    pylab.plot(data_for_plot)

    pylab.savefig('/home/ec2-user/environment/botfarming/Development/graphs/' + str(hours) + 'hour_cumlative.png')

    pylab.clf()


one_day_ago = datetime.datetime.fromtimestamp(int(time.time())-7*60*60-24*60*60).strftime('%Y-%m-%d %H:%M:%S')

one_day_ago_epoch = int(time.time())-7*60*60-24*60*60



###### This don't work
data_for_plot = []
data_points_2 = data_points
for x in range(0,int(24*60/15)):
    changed = False
    start_time = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*x*60).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*(x+1)*60).strftime('%Y-%m-%d %H:%M:%S')

    for data in data_points:
        if data['readable_time'] >= start_time:
            if data['readable_time'] < end_time:
                data_for_plot.append(data['profit'])
            else:
                take_next = False
                first_data = 0
                second_data = 0
                for data_2 in data_points_2:
                    if take_next == True:
                        second_data = data_2['profit']
                        break
                    if data['readable_time'] >= start_time:
                        first_data = data_2['profit']
                        take_next = True
                if first_data != 0 and second_data != 0:
                    data_for_plot.append((second_data+first_data)/2)




    pylab.plot(data_for_plot)

    pylab.savefig('/home/ec2-user/environment/botfarming/Development/graphs/24_hour_cumlative_V1.png')

    pylab.clf()



data_points_for_graph = []
data_points_for_graph_2 = []


previous_profit = 0
current_profit = 0
for x in range(0,int(24*60/15)):
    changed = False
    start_time = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*x*60).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*(x+1)*60).strftime('%Y-%m-%d %H:%M:%S')
    start_time_2 = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*(x+1)*60).strftime('%Y-%m-%d %H:%M:%S')
    end_time_2 = datetime.datetime.fromtimestamp(one_day_ago_epoch+15*(x+2)*60).strftime('%Y-%m-%d %H:%M:%S')


    for data in data_points:
        if data['readable_time'] >= start_time and data['readable_time'] < end_time:
            previous_profit = current_profit
            current_profit = data['profit']
            changed = True

    if changed == False or current_profit - previous_profit > .2:
        data_points_for_graph.append(0)
    else:
        data_points_for_graph.append(current_profit - previous_profit)


    data_points_for_graph_2.append(start_time_2)


pprint(data_points_for_graph)

x = numpy.arange(len(data_points_for_graph))
pylab.bar(x, height=data_points_for_graph)
#pylab.xticks(x+.5, data_points_for_graph_2)

pylab.savefig('/home/ec2-user/environment/botfarming/Development/graphs/24hour_bar.png')

pylab.clf()


















