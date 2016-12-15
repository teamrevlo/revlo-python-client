import requests
from math import ceil
import json
from time import sleep

VERSION = 1
API_BASE = 'https://api.revlo.co'
MAX_RETRIES = 10

class RetryableHttpClient(object):

  def __init__(self, http=requests,headers=None):
    self.http = http
    self.headers = headers

  def _handle_errors(self, response):
    if response.status_code >= 500:
      raise RevloAPIServiceError("Something went wrong")
    else:
      raise RevloAPIClientError(json.loads(response.text)['error'])

  def _is400(self, code):
    return code >= 400 and code < 500

  def get(self, endpoint):
    return self.request('GET', endpoint)

  def post(self, endpoint, payload):
    return self._request('POST', endpoint, payload=payload)

  def patch(self, endpoint, payload):
    return self.request('PATCH', endpoint, payload=payload)

  def delete(self, endpoint):
    return self.request('DELETE', endpoint, payload=payload)

  def request(self, request_type, endpoint, payload=None):
    response = None
    for i in range(0, MAX_RETRIES):
      response = self.http.request(request_type, endpoint, headers=self.headers, data=payload)
      if response.ok:
        break
      elif self._is400(response.status_code):
        self._handle_errors(response)
      sleep(min(2**i,10))
    if not response.ok:
      self._handle_errors(response)
    return response.json()

class RevloClient(object):

  def __init__(self, api_key="", base_url=API_BASE):
    headers = {'content-type': 'application/json', \
               'x-api-key'   : api_key}
    self.base_url = base_url
    self.http = RetryableHttpClient(requests, headers)

  def get_rewards(self, **kwargs):
    response = self.http.get('{}/{}/rewards?{}'.format(self.base_url, VERSION, "&".join(map(lambda a: "{}={}".format(a[0],a[1]), kwargs.items()))))
    total = response['total']
    page_size = response['page_size']
    number_of_pages = int(ceil((total+0.0)/page_size))
    rewards = response['rewards']
    for reward in rewards:
      yield reward
    p = 2
    if 'page' in kwargs:
      try:
        p = max(2, int(kwargs['page']) + 1)
      except ValueError:
        pass
    while p <= number_of_pages:
      rewards = self.http.get('{}/{}/rewards?page={}'.format(self.base_url, VERSION, p))['rewards']
      for reward in rewards:
        yield reward
      p += 1

  def get_redemptions(self, **kwargs):
    kwargs['page'] = 1
    endpoint = "{}/{}/redemptions?{}".format(self.base_url, VERSION, "&".join(map(lambda a: "{}={}".format(a[0],a[1]), kwargs.items())))
    response = self.http.get(endpoint)
    total = response['total']
    page_size = response['page_size']
    number_of_pages = int(ceil((total+0.0)/page_size))
    redemptions = response['redemptions']
    for redemption in redemptions:
      yield redemption
    p = 2
    if 'page' in kwargs:
      try:
        p = max(2, int(kwargs['page']) + 1)
      except ValueError:
        pass
    while p <= number_of_pages:
      kwargs['page'] = p
      endpoint = "{}/{}/redemptions?{}".format(self.base_url, VERSION, "&".join(map(lambda a: "{}={}".format(a[0],a[1]),kwargs.items())))
      redemptions = self.http.get(endpoint)['redemptions']
      for redemption in redemptions:
        yield redemption
      p += 1

  def get_redemption(self, redemption_id):
    return self.http.get('{}/{}/redemptions/{}'.format(self.base_url, VERSION, redemption_id))

  def update_redemption(self, redemption_id, d):
    return self.http.patch('{}/{}/redemptions/{}'.format(self.base_url, VERSION, redemption_id), json.dumps(d))

class RevloAPIServiceError(IOError):
  pass

class RevloAPIClientError(IOError):
  pass
