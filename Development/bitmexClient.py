#!/usr/bin/env python
# https://github.com/BitMEX/api-connectors/blob/master/official-http/python-swaggerpy/bitmexClient.py

import sys
# print sys.path
# '/Library/Python/2.7/site-packages/pip-9.0.1-py2.7.egg'


from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from BitMEXAPIKeyAuthenticator import APIKeyAuthenticator
import json
import pprint

HOST = "https://testnet.bitmex.com"
SPEC_URI = HOST + "/api/explorer/swagger.json"

HOST = "https://www.bitmex.com"
SPEC_URI = HOST + "/api/explorer/swagger.json"

# See full config options at http://bravado.readthedocs.io/en/latest/configuration.html
config = {
  # Don't use models (Python classes) instead of dicts for #/definitions/{models}
  'use_models': False,
  # This library has some issues with nullable fields
  'validate_responses': False,
  # Returns response in 2-tuple of (body, response); if False, will only return body
  'also_return_response': True,
}

bitMEX = SwaggerClient.from_url(
    SPEC_URI,
    config=config)

pp = pprint.PrettyPrinter(indent=2)

# You can get a feel for what is available by printing these objects.
# See also https://testnet.bitmex.com/api/explorer
# https://www.bitmex.com/api/explorer/#/
print('---The BitMEX Object:---')
print(dir(bitMEX))

print('\n---The BitMEX.OrderBook Object:---')
print(dir(bitMEX.OrderBook))
res, http_response = bitMEX.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=1).result()
pp.pprint(res)

print('\n---The BitMEX.Trade Object:---')
print(dir(bitMEX.Trade))
# Basic unauthenticated call
res, http_response = bitMEX.Trade.Trade_get(symbol='XBTUSD', count=1).result()
print('\n---A basic Trade GET:---')
pp.pprint(res)
print('\n---Response details:---')
print("Status Code: %d, headers: %s" % (http_response.status_code, http_response.headers))


#
# Authenticated calls
#
# To do authentication, you must generate an API key.
# Do so at https://testnet.bitmex.com/app/apiKeys

API_KEY = 'n_fGcrHLvBqtAt-222QTxjra'
API_SECRET = '-3yafgNu-JNJUpYq4r5A-NzBC5DC8xy8ByDXZmdNV1bDt2aB'
API_KEY = 'emjo2LdiVdhwmTqMESEcO9ut'
API_SECRET = 'DspbFr4sWjnxUPY4L5yDh13b0MZ1oDGs4kr94EcdJcSH2QkR'

request_client = RequestsClient()
request_client.authenticator = APIKeyAuthenticator(HOST, API_KEY, API_SECRET)

bitMEXAuthenticated = SwaggerClient.from_url(
    SPEC_URI,
    config=config,
    http_client=request_client)

# Basic authenticated call
print('\n---A basic Position GET:---')
print('The following call requires an API key. If one is not set, it will throw an Unauthorized error.')
res, http_response = bitMEXAuthenticated.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()
pp.pprint(res)


# Basic order placement
# print(dir(bitMEXAuthenticated.Order))
# res, http_response = bitMEXAuthenticated.Order.Order_new(symbol='XBTUSD', orderQty=3, price=1000).result()
# print(res)
