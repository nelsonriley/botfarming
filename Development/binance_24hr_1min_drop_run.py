#!/usr/bin/python2.7
import sys
import utility as ut
import utility_2 as ut2

# DON'T FORGET to start:
# https://www.pythonanywhere.com/user/nelsonriley/files/home/nelsonriley/Development/binance_update_order_book.py?edit

bot_index = 0
total_bots = 2

the_ip = ut2.get_computer_ip()
allowed_ips = ['10.0.0.8'] # '10.0.0.22', '10.0.0.212'
non_allowed_ips = ['10.0.0.98', '10.0.0.253']
if the_ip in allowed_ips:
    print(ut.get_time())
    ut2.run_24hr_1min_drop_strategy(bot_index, total_bots)
else:
    print(the_ip, 'is not allowed, start over')
