#!/usr/bin/python2.7
import sys
print 'python', sys.version
import utility as ut
from pprint import pprint
import requests

# save symbol list daily since API sometimes fail when getting live
symbol_data = requests.get("https://api.binance.com/api/v1/exchangeInfo").json()
ticker_data = requests.get("https://api.binance.com/api/v1/ticker/24hr").json()

symbols_for_save = {}
for symbol in symbol_data['symbols']:
    if symbol['quoteAsset'] == 'BTC':
        symbols_for_save[symbol['symbol']] = symbol
for symbol in ticker_data:
    if 'BTC' in symbol['symbol'] and not 'BTC' in symbol['symbol'][:3]:
        symbols_for_save[symbol['symbol']]['24hourVolume'] = symbol['quoteVolume']
        symbols_for_save[symbol['symbol']]['24priceChangePercent'] = symbol['priceChangePercent']

print('---------------ETHBTC')
pprint(symbols_for_save['ETHBTC'])
print('---------------ETHBTC')

print('btc symbols found:', len(symbols_for_save))
ut.pickle_write('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz', symbols_for_save)

symbols_saved = ut.pickle_read('/home/ec2-user/environment/botfarming/Development/binance_btc_symbols.pklz')
print('btc symbols saved:', len(symbols_saved))
