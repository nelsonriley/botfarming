#!/usr/bin/python2.7
#!/usr/bin/env python
# https://github.com/BitMEX/api-connectors/blob/master/official-http/python-swaggerpy/bitmexClient.py

import sys
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from BitMEXAPIKeyAuthenticator import APIKeyAuthenticator
import json
import pprint
import schedule
import time
import datetime
import requests
import pprint

pp = pprint.PrettyPrinter(indent=2)

# See full config options at http://bravado.readthedocs.io/en/latest/configuration.html
config = {
  # Don't use models (Python classes) instead of dicts for #/definitions/{models}
  'use_models': False,
  # This library has some issues with nullable fields
  'validate_responses': False,
  # Returns response in 2-tuple of (body, response); if False, will only return body
  'also_return_response': True,
    # validate outgoing requests
  'validate_requests': True,
  # validate the swagger spec
  'validate_swagger_spec': False
}

# init clients
HOST = "https://www.bitmex.com"
SPEC_URI = HOST + "/api/explorer/swagger.json"
# this has errors: https://www.bitmex.com/api/explorer/swagger.json
# so we tried using a custom version
# SPEC_URI = 'http://nelsonriley.com/bitmex-swagger/swagger_custom_20171206.json'
bitMEX = SwaggerClient.from_url(
    SPEC_URI,
    config=config)
API_KEY = 'emjo2LdiVdhwmTqMESEcO9ut'
API_SECRET = 'DspbFr4sWjnxUPY4L5yDh13b0MZ1oDGs4kr94EcdJcSH2QkR'
request_client = RequestsClient()
request_client.authenticator = APIKeyAuthenticator(HOST, API_KEY, API_SECRET)
bitMEXAuthenticated = SwaggerClient.from_url(
    SPEC_URI,
    config=config,
    http_client=request_client)


# init clients as func
def get_clients():
    HOST = "https://www.bitmex.com"
    SPEC_URI = HOST + "/api/explorer/swagger.json"
    bitMEX = SwaggerClient.from_url(
        SPEC_URI,
        config=config)
    API_KEY = 'emjo2LdiVdhwmTqMESEcO9ut'
    API_SECRET = 'DspbFr4sWjnxUPY4L5yDh13b0MZ1oDGs4kr94EcdJcSH2QkR'
    request_client = RequestsClient()
    request_client.authenticator = APIKeyAuthenticator(HOST, API_KEY, API_SECRET)
    bitMEXAuthenticated = SwaggerClient.from_url(
        SPEC_URI,
        config=config,
        http_client=request_client)
    return bitMEX, bitMEXAuthenticated


def get_positions(do_print=False):
    print '# get_positions()'
    the_filter = json.dumps({'symbol': 'XBTUSD'})
    # print(dir(bitMEXAuthenticated.Position))
    # [u'Position_get', u'Position_isolateMargin', u'Position_transferIsolatedMargin', u'Position_updateLeverage', u'Position_updateRiskLimit']
    # ensure no request expired errortime.sleep(0.05)
    res, http_response = bitMEXAuthenticated.Position.Position_get(filter=the_filter).result()
    if do_print :
        pp.pprint(res)
    # AVAIL:
    # isOpen
    # currentQty **
    # liquidationPrice
    # marginCallPrice
    # avgEntryPrice
    # leverage
    # execBuyCost
    # execBuyQty
    # execCost
    # execQty
    # breakEvenPrice
    return res


def update_leverage(leverage, do_print=False):
    print '# update_leverage() to', leverage
    res, http_response = bitMEXAuthenticated.Position.Position_updateLeverage(symbol='XBTUSD', leverage=leverage).result()
    if do_print:
        pp.pprint(res)
    return res


def get_user_wallet(do_print=False):
    # print(dir(bitMEXAuthenticated.User))
    # [u'User_cancelWithdrawal', u'User_checkReferralCode', u'User_confirm', u'User_confirmEnableTFA', u'User_confirmWithdrawal', u'User_disableTFA', u'User_get', u'User_getAffiliateStatus', u'User_getCommission', u'User_getDepositAddress', u'User_getMargin', u'User_getWallet', u'User_getWalletHistory', u'User_getWalletSummary', u'User_logout', u'User_logoutAll', u'User_minWithdrawalFee', u'User_requestEnableTFA', u'User_requestWithdrawal', u'User_savePreferences', u'User_update']
    print '# get_user_balance()'
    res, http_response = bitMEXAuthenticated.User.User_getWallet(currency='XBt').result()
    res['amount_bitcoins'] = res['amount'] * 0.00000001
    if do_print:
        pp.pprint(res)
    return res

def get_user_margin(do_print=False):
    # print(dir(bitMEXAuthenticated.User))
    # [u'User_cancelWithdrawal', u'User_checkReferralCode', u'User_confirm', u'User_confirmEnableTFA', u'User_confirmWithdrawal', u'User_disableTFA', u'User_get', u'User_getAffiliateStatus', u'User_getCommission', u'User_getDepositAddress', u'User_getMargin', u'User_getWallet', u'User_getWalletHistory', u'User_getWalletSummary', u'User_logout', u'User_logoutAll', u'User_minWithdrawalFee', u'User_requestEnableTFA', u'User_requestWithdrawal', u'User_savePreferences', u'User_update']
    print '# get_user_balance()'
    res, http_response = bitMEXAuthenticated.User.User_getMargin(currency='XBt').result()
    # res['amount_bitcoins'] = res['amount'] *0.00000001
    res['availableMarginBtc'] = res['availableMargin'] * 0.00000001
    res['walletBalanceBtc'] = res['walletBalance'] * 0.00000001
    if do_print:
        pp.pprint(res)
    return res


def place_order(qty=0, price=9999999, side='Buy', do_print=False):
    # possible errors
        # Order price is below the liquidation price of current long position
    # Basic order placement
    # print(dir(bitMEXAuthenticated.Order))
    print '# place_order()', side, '@ qty', qty, 'price', price
    # [u'Order_amend', u'Order_amendBulk', u'Order_cancel', XX u'Order_cancelAll', u'Order_cancelAllAfter', u'Order_closePosition', u'Order_getOrders', u'Order_new', u'Order_newBulk']
    res, http_response = bitMEXAuthenticated.Order.Order_new(symbol='XBTUSD', orderQty=qty, price=price, side=side).result()
    if do_print:
        pp.pprint(res)
    return res
    # IMMEDIATE EXECUTION (long and limit price > current price)
    # { u'account': 113345L,
    # u'avgPx': 13090.5, **
    # u'clOrdID': u'',
    # u'clOrdLinkID': u'',
    # u'contingencyType': u'',
    # u'cumQty': 1L,
    # u'currency': u'USD',
    # u'displayQty': None,
    # u'exDestination': u'XBME',
    # u'execInst': u'',
    # u'leavesQty': 0L,
    # u'multiLegReportingType': u'SingleSecurity',
    # u'ordRejReason': u'',
    # u'ordStatus': u'Filled', **  or 'New'
    # u'ordType': u'Limit', **
    # u'orderID': u'ff5f95f5-9af2-52f2-7d06-2a0eb277ecf7', **
    # u'orderQty': 1L, **
    # u'pegOffsetValue': None,
    # u'pegPriceType': u'',
    # u'price': 15000.0, **
    # u'settlCurrency': u'XBt',
    # u'side': u'Buy',
    # u'simpleCumQty': 7.639e-05,
    # u'simpleLeavesQty': 0.0,
    # u'simpleOrderQty': None,
    # u'stopPx': None,
    # u'symbol': u'XBTUSD',
    # u'text': u'Submitted via API.',
    # u'timeInForce': u'GoodTillCancel',
    # u'timestamp': datetime.datetime(2017, 12, 6, 20, 42, 19, 977000, tzinfo=tzutc()),
    # u'transactTime': datetime.datetime(2017, 12, 6, 20, 42, 19, 977000, tzinfo=tzutc()),
    # u'triggered': u'',
    # u'workingIndicator': False}
    # NOT EXECUTED
    # { u'account': 113345L,
    #   u'avgPx': None,
    #   u'clOrdID': u'',
    #   u'clOrdLinkID': u'',
    #   u'contingencyType': u'',
    #   u'cumQty': 0L,
    #   u'currency': u'USD',
    #   u'displayQty': None,
    #   u'exDestination': u'XBME',
    #   u'execInst': u'',
    #   u'leavesQty': 1L,
    #   u'multiLegReportingType': u'SingleSecurity',
    #   u'ordRejReason': u'',
    #   u'ordStatus': u'New',
    #   u'ordType': u'Limit',
    #   u'orderID': u'1f00b218-ea84-938a-2885-399401b18c29',
    #   u'orderQty': 1L,
    #   u'pegOffsetValue': None,
    #   u'pegPriceType': u'',
    #   u'price': 11000.0,
    #   u'settlCurrency': u'XBt',
    #   u'side': u'Buy',
    #   u'simpleCumQty': 0.0,
    #   u'simpleLeavesQty': 0.0001,
    #   u'simpleOrderQty': None,
    #   u'stopPx': None,
    #   u'symbol': u'XBTUSD',
    #   u'text': u'Submitted via API.',
    #   u'timeInForce': u'GoodTillCancel',
    #   u'timestamp': datetime.datetime(2017, 12, 6, 20, 54, 37, 140000, tzinfo=tzutc()),
    #   u'transactTime': datetime.datetime(2017, 12, 6, 20, 54, 37, 140000, tzinfo=tzutc()),
    #   u'triggered': u'',
    #   u'workingIndicator': True}
# place_order()


# modified: File "/Library/Python/2.7/site-packages/bravado_core/response.py", line 124 to avoid errors
def cancel_all_orders(do_print=False):
    # bad swagger spec for Order_cancelAll /order/all   response object instead of array
    # res, http_response = bitMEXAuthenticated.Order.Order_cancelAll().result(timeout=20)
    res, http_response = bitMEXAuthenticated.Order.Order_cancelAllAfter(timeout=500).result()
    print '# cancel_all_orders()'
    if do_print:
        pp.pprint(res)
    # { u'cancelTime': u'2017-12-06T23:10:15.311Z',
    # u'now': u'2017-12-06T23:10:14.811Z'}
    return res


def get_first_sell_price():
    res, http_response = bitMEX.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=1).result()
    return float(res[0]['price'])


#########################################################################################################


def get_smart_chart_og(hours_history=24, resolution_minutes=1, do_print=False, to_time='now'):
    if to_time == 'now':
        time_to = int(time.time())
        # ensure entire history has bollinger bands & simple moving average
        time_from = time_to - (hours_history * 60 * 60) - (20 * 60 * resolution_minutes)
        time_from_actual = time_to - (hours_history * 60 * 60)

    readable_time_to = datetime.datetime.fromtimestamp(time_to).strftime('%Y-%m-%d %H:%M:%S')
    readable_time_from = datetime.datetime.fromtimestamp(time_from_actual).strftime('%Y-%m-%d %H:%M:%S')
    print 'get_smart_chart()', 'from', readable_time_from, 'to', readable_time_to

    # https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=1&from=1512071851&to=1512158311
    # API only allows resolutions: 1, 5, 60, D (for 1 day)
    url = 'https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution='+str(resolution_minutes)+'&from='+str(time_from)+'&to='+str(time_to)
    print 'data url', url
    r = requests.get(url)
    data = r.json()
    # pp.pprint(data)

    sma_interval = 20
    sma_array = []
    frame_array = []
    for i in range(0, len(data['t'])):
        t = data['t'][i]
        v = data['v'][i]
        o = data['o'][i]
        h = data['h'][i]
        l = data['l'][i]
        c = data['c'][i]

        t_readable = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

        sma_array.append(c)
        if len(sma_array) > sma_interval:
            sma_array.pop(0)
            sma = sum(sma_array) / sma_interval
            # Standard Deviation Calc
            # 1. Work out the Mean (the simple average of the numbers)
            # 2. Then for each number: subtract the Mean and square the result
            # 3. Then work out the mean of those squared differences.
            # 4. Take the square root of that and we are done!
            stan_dev_array = [(n-sma)**2 for n in sma_array]
            stan_dev_mean = sum(stan_dev_array) / sma_interval
            stan_dev = stan_dev_mean**(0.5)
            # bollinger bands
            middle_band = sma
            upper_band = sma + stan_dev * 2
            lower_band = sma - stan_dev * 2
            frame_array.append({
                'time_epoch': t,
                'time_human': t_readable,
                'volume': v,
                'open': o,
                'close': c,
                'high': h,
                'low': l,
                'boll_upper': upper_band,
                'boll_middle': middle_band,
                'boll_lower': lower_band
                })

        if do_print:
            # confirm print out with chart data
            if i > len(data['t']) - 10:
                print t_readable, sma_interval
                print 'o', o, 'h', h, 'l', l, 'c', c
                print 'bb', middle_band, upper_band, lower_band
                print '----------------------'

    if do_print:
        print len(frame_array), 'frames in', hours_history, 'hours'
    return frame_array


def get_smart_chart(hours_history=24, resolution_minutes=1, do_print=False, go_back_minutes=0):
    time_to = int(time.time()) - go_back_minutes * 60
    # ensure even 15 minute intervals
    if resolution_minutes == 15:
        while True:
            if time_to % (15 * 60) == 0:
                break
            time_to = time_to - 1
        time_to += 5 * 60
    # ensure entire history has bollinger bands & simple moving average
    time_from = time_to - (hours_history * 60 * 60) - (20 * 60 * resolution_minutes)
    # time_from = time_to - (hours_history * 60 * 60)
    time_from_actual = time_to - (hours_history * 60 * 60)

    readable_time_to = datetime.datetime.fromtimestamp(time_to - 5 * 60).strftime('%Y-%m-%d %H:%M:%S')
    readable_time_from = datetime.datetime.fromtimestamp(time_from_actual - 5 * 60).strftime('%Y-%m-%d %H:%M:%S')

    req_resolution = resolution_minutes
    if resolution_minutes == 15:
        req_resolution = 5

    # TODO Too many bars requested. Max bars: 10080
    bars = (time_to - time_from) / 60 / req_resolution
    # print 'bars requested', bars
    if bars > 10080:
        'ERROR too many bars'
        return []

    # https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=1&from=1512071851&to=1512158311
    # API only allows resolutions: 1, 5, 60, D (for 1 day)
    url = 'https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution='+str(req_resolution)+'&from='+str(time_from)+'&to='+str(time_to)
    if do_print:
        print '# data url', url
        print '#', readable_time_from, 'to', readable_time_to, '(', resolution_minutes, 'min chart)'
    r = requests.get(url)
    data = r.json()
    # pp.pprint(data)

    # combine frames in same API format if unsupported API time resolution
    if resolution_minutes == 15:
        combine_n_frames = resolution_minutes / req_resolution
        combine_index = 1
        t_comb = 0
        v_comb = 0
        o_comb = 0
        h_comb = 0
        l_comb = 999999999
        c_comb = 0
        data_comb = {
          't': [],
          'v': [],
          'o': [],
          'h': [],
          'l': [],
          'c': [],
        }
        for i in range(0, len(data['t'])):
            t = data['t'][i]
            v = data['v'][i]
            o = data['o'][i]
            h = data['h'][i]
            l = data['l'][i]
            c = data['c'][i]
            v_comb += v
            if h > h_comb:
                h_comb = h
            if l < l_comb:
                l_comb = l
            if combine_index == 1:
                o_comb = o
                t_comb = t
            if combine_index == combine_n_frames:
                c_comb = c
                data_comb['t'].append(t_comb)
                data_comb['v'].append(v_comb)
                data_comb['o'].append(o_comb)
                data_comb['h'].append(h_comb)
                data_comb['l'].append(l_comb)
                data_comb['c'].append(c_comb)
                # reset
                combine_index = 0
                t_comb = 0
                v_comb = 0
                o_comb = 0
                h_comb = 0
                l_comb = 999999999
                c_comb = 0
            combine_index += 1
        data = data_comb

    # create frames with bollinger bands
    sma_interval = 20
    sma_array = []
    frame_array = []
    # vars
    last_open_close_center = 0
    consecutive_lower_open_close_centers = 0
    consecutive_higher_open_close_centers = 0
    last_boll_middle = 0
    for i in range(0, len(data['t'])):
        t = data['t'][i]
        v = data['v'][i]
        o = data['o'][i]
        h = data['h'][i]
        l = data['l'][i]
        c = data['c'][i]

        t_readable = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

        sma_array.append(c)
        if len(sma_array) > sma_interval:
            sma_array.pop(0)
            sma = sum(sma_array) / sma_interval
            # Standard Deviation Calc
            # 1. Work out the Mean (the simple average of the numbers)
            # 2. Then for each number: subtract the Mean and square the result
            # 3. Then work out the mean of those squared differences.
            # 4. Take the square root of that and we are done!
            stan_dev_array = [(n-sma)**2 for n in sma_array]
            stan_dev_mean = sum(stan_dev_array) / sma_interval
            stan_dev = stan_dev_mean**(0.5)
            # bollinger bands
            middle_band = sma
            upper_band = sma + stan_dev * 2
            lower_band = sma - stan_dev * 2
            # meta
            color = 'red'
            if c > o:
                color = 'green'
            open_close_center = (o + c) / 2
            if last_open_close_center == 0:
                last_open_close_center = open_close_center
            if open_close_center < last_open_close_center:
                consecutive_lower_open_close_centers += 1
                consecutive_higher_open_close_centers = 0
            if open_close_center >= last_open_close_center:
                consecutive_higher_open_close_centers += 1
                consecutive_lower_open_close_centers = 0
            frame_array.append({
                'time_epoch': t,
                'time_human': t_readable,
                'volume': v,
                'open': o,
                'close': c,
                'high': h,
                'low': l,
                'boll_upper': upper_band,
                'boll_middle': middle_band,
                'boll_middle_change': middle_band - last_boll_middle,
                'boll_lower': lower_band,
                'color': color,
                'open_close_center': open_close_center,
                'high_low_center': (h + l) / 2,
                'consecutive_lower_open_close_centers': consecutive_lower_open_close_centers,
                'consecutive_higher_open_close_centers': consecutive_higher_open_close_centers
                })
            last_open_close_center = open_close_center
            last_boll_middle = middle_band

        if do_print:
            # confirm print out with chart data
            if i > len(data['t']) - 10:
                print t_readable, sma_interval
                print 'o', o, 'h', h, 'l', l, 'c', c
                print 'bb', middle_band, upper_band, lower_band
                print '----------------------'

    if do_print:
        print '#', len(frame_array), 'frames in', hours_history, 'hours (', round(hours_history / 24, 3), 'days)'
    return frame_array

# You can get a feel for what is available by printing these objects.
# See also https://testnet.bitmex.com/api/explorer
# https://www.bitmex.com/api/explorer/#/
# print('---The BitMEX Object:---')
# print(dir(bitMEX))

# print('\n---The BitMEX.OrderBook Object:---')
# print(dir(bitMEX.OrderBook))
# res, http_response = bitMEX.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=1).result()
# pp.pprint(res)

# print 'get_first_sell_price', get_first_sell_price()


# Basic unauthenticated call
# print('\n---The BitMEX.Trade Object:---')
# print(dir(bitMEX.Trade))
# res, http_response = bitMEX.Trade.Trade_get(symbol='XBTUSD', count=1).result()
# print('\n---A basic Trade GET:---')
# pp.pprint(res)
# print('\n---Response details:---')
# print("Status Code: %d, headers: %s" % (http_response.status_code, http_response.headers))

#
# Authenticated calls
#
# To do authentication, you must generate an API key.
# Do so at https://testnet.bitmex.com/app/apiKeys

# Basic authenticated call
# print('\n---A basic Position GET:---')
# print('The following call requires an API key. If one is not set, it will throw an Unauthorized error.')
# res, http_response = bitMEXAuthenticated.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()
# pp.pprint(res)


# Basic order placement
# print(dir(bitMEXAuthenticated.Order))
# res, http_response = bitMEXAuthenticated.Order.Order_new(symbol='XBTUSD', orderQty=3, price=1000).result()
# print(res)
