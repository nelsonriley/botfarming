import sys
print('python', sys.version)
from collections import OrderedDict, Mapping, Container
from pprint import pprint
from sys import getsizeof
# 2.7 from twilio.rest import Client
from twilio.rest import TwilioRestClient

# import twilio
# print(dir(twilio.rest))

# https://www.twilio.com/docs/quickstart/python/sms/sending-via-rest#send-sms-via-library
# DO THIS sudo easy_install twilio
# $1 / month per number, $0.0075 per sent SMS
# (951) 476-2168
# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
# Find these values at https://twilio.com/user/account
account_sid = "ACcc6bd88977d0eddd1ff935ecbc2cacee"
auth_token = "c9ba89f331e84936155f1916a5bca2fb"
client = TwilioRestClient(account_sid, auth_token)


def twilio_send_sms(text):
    message = client.api.account.messages.create(
    to="+18027936146",
    from_="+19514762168",
    body=text)
    print('SENT SMS:', text)


def hello_dawg():
    print('hello_dawg')


# thanks: https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
def print_pretty_dict(d, indent=0):
    # for key, value in d.items():
    #     print('\t' * indent + str(key))
    #     if isinstance(value, dict):
    #         print_pretty_dict(value, indent+1)
    #     else:
    #         print('\t' * (indent+1) + str(value))
    # for key, value in d.items():
    for key in sorted(d.iterkeys()):
        value = d[key]
        if isinstance(value, dict):
            print('\t' * indent + str(key))
            print_pretty_dict(value, indent+1)
        else:
            print('\t' * indent + str(key) + ': ' + str(value))


def poll_for_action(order_book, is_stream=False, do_print=False):
    if is_stream == True:
        order_book['bids'].reverse()

    do_sell = False
    first_ask_price = 0
    first_bid_price = 0

    if len(order_book['asks']) == 0 or len(order_book['bids']) == 0:
        return do_sell, first_ask_price, first_bid_price

    first_ask_price = order_book['asks'][0][0]
    first_bid_price = order_book['bids'][0][0]
    ask_slope = get_max_slope_from_order_book_asks(order_book, 200, 500)
    bid_slope = get_min_slope_from_order_book_bids(order_book, 15, 50)
    immediate_ask_vol = get_cum_vol_to_price(order_book, bid_or_ask='asks', price=2)
    immediate_bid_vol = get_cum_vol_to_price(order_book, bid_or_ask='bids', price=2)

    if do_print:
        print('first_ask_price', first_ask_price)
        print('first_bid_price', first_bid_price)
        print('ask_slope', ask_slope)
        print('bid_slope', bid_slope)
        print('immediate_ask_vol', immediate_ask_vol)
        print('immediate_bid_vol', immediate_bid_vol)

    if ask_slope >= 17 and bid_slope <= 2 and immediate_ask_vol <= 1.15 * immediate_bid_vol:
        do_sell = True

    return do_sell, first_ask_price, first_bid_price


def get_first_n_percent_from_order_book(order_book_bids_or_asks, percent=0.02):
    first_price = 0
    price_change_limit = 0
    orders = []
    for order in order_book_bids_or_asks:
        price = float(order[0])
        size = float(order[1])
        if first_price == 0:
            first_price = price
            price_change_limit = first_price * percent
        price_change = abs(price - first_price)
        if price_change >= price_change_limit:
            break
        minimized_order = [float(order[0]), float(order[1])]
        orders.append(minimized_order)
    return orders


def get_max_slope_from_order_book_asks(order_book, min_volume=200, max_volume=500):
    max_slope = 0
    cum_volume = 0
    first_price = 0
    for order in order_book['asks']:
        price = float(order[0])
        size = float(order[1])
        if first_price == 0:
            first_price = price
        cum_volume += size
        if cum_volume >= min_volume and first_price < price:
            slope = cum_volume / (price - first_price)
            if slope > max_slope:
                max_slope = slope
        if cum_volume > max_volume:
            break
    return max_slope


def get_min_slope_from_order_book_bids(order_book, min_volume=15, max_volume=50):
    min_slope = 9900000
    cum_volume = 0
    first_price = 0
    for order in order_book['bids']:
        price = float(order[0])
        size = float(order[1])
        if first_price == 0:
            first_price = price
        cum_volume += size
        if cum_volume >= min_volume and first_price > price:
            slope = cum_volume / (first_price - price)
            if slope < min_slope:
                min_slope = slope
        if cum_volume > max_volume:
            break
    return min_slope


def get_avg_price_of_first_n_volume(order_book, bid_or_ask='asks', volume=5):
    cum_volume = 0
    cum_dollars = 0
    avg_price = 0
    first_price = 0
    for order in order_book[bid_or_ask]:
        price = float(order[0])
        size = float(order[1])
        if first_price == 0:
            first_price = price
        cum_volume += size
        cum_dollars += size * price
        if cum_volume > volume:
            avg_price = cum_dollars / cum_volume - first_price
            if bid_or_ask == 'bids':
                avg_price = first_price - (cum_dollars / cum_volume)
            break
    return avg_price


def get_cum_vol_to_price(order_book, bid_or_ask='asks', price=2):
    price_change = price
    cum_volume = 0
    first_price = 0
    for order in order_book[bid_or_ask]:
        price = float(order[0])
        size = float(order[1])
        if first_price == 0:
            first_price = price
        cum_volume += size
        change = price - first_price
        if bid_or_ask == 'bids':
            change = first_price - price
        if change >= price_change:
            break
    return cum_volume


# thanks: https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
# and: https://github.com/the-gigi/deep/blob/master/deeper.py
def deep_compare(a, b, pointer='/'):
    if a == b:
        return

    if type(a) != type(b):
        reason = 'Different data types'
        extra = str((type(a), type(b)))
        x(pointer, reason, extra)

    elif type(a) in (set, frozenset):
        pointer += 'set()'
        if len(a) != len(b):
            pointer += 'set()'
            reason = 'Different number of items'
            extra = str((len(a), len(b)))
            x(pointer, reason, extra)

        reason = 'Different items'
        extra = (a, b)
        x(pointer, reason, extra)

        for i in range(len(a)):
            deep_compare(a[i], b[i], pointer + 'set()'.format(i))

    elif type(a) in (list, tuple):
        if len(a) != len(b):
            pointer += '[]'
            reason = 'Different number of items'
            extra = str((len(a), len(b)))
            x(pointer, reason, extra)

        if sorted(a) == sorted(b):
            pointer += '[]'
            reason = 'Different sort order'
            extra = 'N/A'
            x(pointer, reason, extra)

        for i in range(len(a)):
            deep_compare(a[i], b[i], pointer + '[{}]'.format(i))

    elif type(a) in (dict, OrderedDict):
        if len(a) != len(b):
            pointer += '{}'
            reason = 'Different number of items'
            extra = str((len(a), len(b)))
            x(pointer, reason, extra)

        if set(a.keys()) != set(b.keys()):
            pointer += '{}'
            reason = 'Different keys'
            extra = (a.keys(), b.keys())
            x(pointer, reason, extra)

        for k in a:
            deep_compare(a[k], b[k], pointer + '[{}]'.format(k))
    else:
        reason = 'Different objects'
        extra = (a, b)
        x(pointer, reason, extra)


def x(pointer, reason, extra):
    message = 'Objects are not the same. Pointer: {}. Reason: {}. Extra: {}'
    raise RuntimeError(message.format(pointer, reason, extra))


def compare(a, b):
    try:
        deep_compare(a, b, '/')
    except RuntimeError as e:
        pprint(e.message)


def deep_getsizeof(o, ids):
    """Find the memory footprint of a Python object
    This is a recursive function that drills down a Python object graph
    like a dictionary holding nested ditionaries with lists of lists
    and tuples and sets.
    The sys.getsizeof function does a shallow size of only. It counts each
    object inside a container as pointer only regardless of how big it
    really is.
    :param o: the object
    :param ids:
    :return:
    """
    d = deep_getsizeof
    if id(o) in ids:
        return 0

    r = getsizeof(o)
    ids.add(id(o))

    if isinstance(o, str) or isinstance(0, unicode):
        return r

    if isinstance(o, Mapping):
        return r + sum(d(k, ids) + d(v, ids) for k, v in o.iteritems())

    if isinstance(o, Container):
        return r + sum(d(x, ids) for x in o)

    return r
