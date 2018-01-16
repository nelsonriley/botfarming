#!/usr/bin/python2.7
import csv
import sys
from pprint import pprint

# schema
    # date = row[0]
    # pair = row[1]
    # buy_or_sell = row[2]
    # order_price = float(row[3])
    # order_amount = float(row[4])
    # trade_price = float(row[5])
    # filled = float(row[6])
    # total = float(row[7])
    # status = row[8]

# setup dictionary for every symbol traded
f = open('./OrderHistory.csv', 'rb')
reader = csv.reader(f)
symbols = {}
symbols_traded = {}
for row in reader:
    status = row[8]
    #print('status1', status)
    if status == 'Filled' or status == 'Partial Fill':
        pair = row[1]
        symbols[pair] = True
        symbols_traded[pair+'_buys_filled'] = 0
        symbols_traded[pair+'_buys_total'] = 0
        symbols_traded[pair+'_sells_filled'] = 0
        symbols_traded[pair+'_sells_total'] = 0
        # print row
f.close()

# track buys + sells total / filled
f = open('./OrderHistory.csv', 'rb')
reader = csv.reader(f)
for row in reader:
    status = row[8]
    if status == 'Filled':
        pair = row[1]
        buy_or_sell = row[2]
        filled = float(row[6])
        total = float(row[7])
        if buy_or_sell == 'BUY':
            symbols_traded[pair+'_buys_filled'] += filled
            symbols_traded[pair+'_buys_total'] += total
        if buy_or_sell == 'SELL':
            symbols_traded[pair+'_sells_filled'] += filled
            symbols_traded[pair+'_sells_total'] += total
f.close()

# calc profit per symbol (ensure matching sell / buy filled amount)
for symbol in symbols:
    if symbols_traded[symbol+'_buys_filled'] == symbols_traded[symbol+'_sells_filled']:
        symbols[symbol] = symbols_traded[symbol+'_sells_total'] - symbols_traded[symbol+'_buys_total']
    else:
        symbols[symbol] = 0

pprint(symbols_traded)
# pprint(symbols)

# stats
profit = 0
profit_gains = 0
profit_losses = 0
skipped_count = 0
symbol_count = 0
for symbol in symbols:
    if symbols[symbol] > 0:
        profit_gains += symbols[symbol]
    if symbols[symbol] < 0:
        profit_losses += symbols[symbol]
    if symbols[symbol] == 0:
        skipped_count += 1
        print('skipped', symbol)
    profit += symbols[symbol]
    symbol_count += 1

print('profit', profit)
print('profit_gains', profit_gains)
print('profit_losses', profit_losses)
print('skipped_count', skipped_count)
print('symbol_count', symbol_count)

f.close()
