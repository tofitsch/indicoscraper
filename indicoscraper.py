# https://docs.getindico.io/en/stable/http-api/

import requests
import hashlib
import hmac
import time
import json
import re
from urllib.parse import urlencode
from pprint import pprint

class BearerAuth(requests.auth.AuthBase):

  def __init__(self, token):
    self.token = token

  def __call__(self, r):
    r.headers["authorization"] = "Bearer " + self.token
    return r


def str_parse(*args):
 
  return '_'.join([re.sub('[^0-9a-zA-Z]+', '-', x.replace('.pdf', '')) if x != None else 'NaN' for x in args])


def build_indico_request(path, params, api_key=None, secret_key=None):

  items = list(params.items())

  items.append(('apikey', api_key))
  items.append(('timestamp', str(int(time.time()))))

  items = sorted(items, key=lambda x: x[0].lower())

  url = '%s?%s' % (path, urlencode(items))

  signature = hmac.new(secret_key.encode('utf-8'), url.encode('utf-8'), hashlib.sha1).hexdigest()
  items.append(('signature', signature))

  return '%s?%s' % (path, urlencode(items))


def get_events_from_category(category_id, date_from, date_to, api_token):
  
  events = {}
  
  url = 'https://indico.cern.ch/export/categ/' + category_id +'.json?from=' + date_from + '&to=' + date_to

  response = requests.get(url, auth=BearerAuth(api_token))

  if response.status_code != 200:
    print('WARNING: [get_events_from_category] status_code', response.status_code, ' != 200 for category_id', category_id)
    return {}

  data = json.loads(response.content.decode('utf-8'))

  if len(data['results']) == 0:
    print('WARNING: [get_events_from_category] number of results == 0 for category_id', category_id)
    return {}
 
  for evt in data['results']:
    events[evt['id']] = {'title': evt['title'], 'date': evt['startDate']['date']}
  
  return events


def get_material_from_event(event_id, api_token):
  
  material = {}

  url = 'https://indico.cern.ch/export/event/' + event_id + '.json?detail=subcontributions'

  response = requests.get(url, auth=BearerAuth(api_token))

  if response.status_code != 200:
    print('WARNING:', response.status_code, ' [get_material_from_event] status_code != 200 for event_id', event_id)
    return {}

  data = json.loads(response.content.decode('utf-8'))

  if len(data['results']) != 1:
    print('WARNING: [get_material_from_event] number of results != 1 for event_id', event_id)
    return {}

  for con in data['results'][0]['contributions']:

    for fol in con['folders']:
      for att in fol['attachments']:
        if att['download_url'].endswith('.pdf'):
          material[str_parse(con['title'], att['title'])] = {'evt': event_id, 'con': con['id'], 'mat': att['id']}
      
    for subcon in con['subContributions']:

      for mat in subcon['material']:
        if mat['download_url'].endswith('.pdf'):
          material[str_parse(con['title'], subcon['title'], mat['title'])] = {'evt': event_id, 'con': con['id'], 'mat': mat['id']}

      for subfol in subcon['folders']:
        for subatt in subfol['attachments']:
          if subatt['download_url'].endswith('.pdf'):
            material[str_parse(con['title'], subcon['title'], subatt['title'])] = {'evt': event_id, 'con': con['id'], 'mat': subatt['id']}
  
  return material


def download_material(material, api_key, api_secret):
  
  domain = 'https://indico.cern.ch'

  for name in material:
    
    path = '/export/event/{}/session/0/contrib/{}/material/slides/{}.bin'.format(material[name]['evt'], material[name]['con'], material[name]['mat'])

    url = domain + build_indico_request(path, {}, api_key, api_secret)

    print(url)

    response = requests.get(url)

    if response.status_code != 200:
      print('WARNING: [download_material] status_code', response.status_code, '!= 200 for url', url)
      return None
    
    open(name + '.pdf', 'wb').write(response.content)


api_token, api_key, api_secret = [x.replace('\n', '') for x in open('indico_api.secret', 'r').readlines()]

#events = get_events_from_category('3285', '2024-02-01', '2024-02-01', api_token)
#
#pprint(events, width=128)
#
#for event_id in events:
#
#  material = get_material_from_event(event_id, api_token)
#
#  pprint(material, width=128)
#
#  exit()

material = get_material_from_event('1355094', api_token)
pprint(material, width=128)

download_material(material, api_key, api_secret)
