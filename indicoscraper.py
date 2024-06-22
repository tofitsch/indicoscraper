from pathlib import Path
import requests
import hashlib
import hmac
import time
import json
import fitz
import sys
import re
import os
from datetime import datetime,timedelta

def main():

  _, category, rex, out_dir = sys.argv

  category = category.replace('https://', '')

  domain, _, category_id, _ = category.split('/')

  domain = 'https://' + domain

  print('domain:', domain)
  print('category_id:', category_id)
  print('regex:', rex)
  print('out_dir:', out_dir)

  Path(out_dir).mkdir(parents=True, exist_ok=True)
  
  api_key, api_secret = [x.replace('\n', '') for x in open('api.secret', 'r').readlines()]

  week = 0

  while True:
    
    print('scraping week of: today -', week, 'weeks')

    from_time = datetime.now() - timedelta(days=7 * (week + 1))
    to_time = datetime.now() - timedelta(days=7 * week)
  
    events = get_events_from_category(category_id, rex, from_time.strftime('%Y-%m-%d'), to_time.strftime('%Y-%m-%d'), domain, api_key, api_secret)

    for event in events:
    
      material = get_material_from_event(event, domain, api_key, api_secret)

      for mat in material:
      
        download_material(mat, out_dir, domain, api_key, api_secret)
    
    week += 1

def flatten(xss):
  return [x for xs in xss for x in xs]

def build_indico_request(path, params, api_key=None, secret_key=None):

  items = list(params.items())

  items.append(('apikey', api_key))
  items.append(('timestamp', str(int(time.time()))))

  items = sorted(items, key=lambda x: x[0].lower())

  url = path + '?' + '&'.join(['='.join(x) for x in items])

  signature = hmac.new(secret_key.encode('utf-8'), url.encode('utf-8'), hashlib.sha1).hexdigest()
  items.append(('signature', signature))

  url = path + '?' + '&'.join(['='.join(x) for x in items])

  return url


def compose_name(*args):
 
  return '_'.join([re.sub('[^0-9a-zA-Z]+', '-', x.replace('.pdf', '')) if x != None else 'NaN' for x in args]) + '.pdf'


def get_events_from_category(category_id, rex, date_from, date_to, domain, api_key, api_secret):
  
  events = []
  
  path = '/export/categ/{}.json'.format(category_id)

  url = domain + build_indico_request(path, {'from': date_from, 'to': date_to}, api_key, api_secret)

  response = requests.get(url)

  if response.status_code != 200:
    print('WARNING: [get_events_from_category] status_code', response.status_code, ' != 200 for category_id', category_id)
    return []

  data = json.loads(response.content.decode('utf-8'))

  if len(data['results']) == 0:
    print('WARNING: [get_events_from_category] number of results == 0 for category_id', category_id)
    return []
 
  for evt in data['results']:
    if re.match(rex, evt['title']):
      events.append({'id': evt['id'], 'title': evt['title'], 'date': evt['startDate']['date']})
  
  return events


def get_material_from_event(event, domain, api_key, api_secret):
  
  material = []

  path = '/export/event/{}.json'.format(event['id'])

  url = domain + build_indico_request(path, {'detail': 'subcontributions'}, api_key, api_secret)

  response = requests.get(url)

  if response.status_code != 200:
    print('WARNING:', response.status_code, ' [get_material_from_event] status_code != 200 for event', event['id'])
    return []

  data = json.loads(response.content.decode('utf-8'))

  if len(data['results']) != 1:
    print('WARNING: [get_material_from_event] number of results != 1 for event', event['id'])
    return []

  for con in data['results'][0]['contributions']:
    
    speakers = []
    
    for n in ['first_name', 'last_name']:
      speakers += [s[n].split(' ') for s in con['speakers']]

    speakers = flatten(speakers)
    
    for fol in con['folders']:
      for att in fol['attachments']:
        if 'download_url' in att and att['download_url'].endswith('.pdf'):
          material.append({'name': compose_name(event['date'], con['title'], att['title']), 'evt': event['id'], 'con': con['id'], 'mat': att['id'], 'url': con['url'], 'speakers': speakers})
      
    for subcon in con['subContributions']:
      
      for mat in subcon['material']:
        if 'download_url' in mat and mat['download_url'].endswith('.pdf'):
          material.append({'name': compose_name(event['date'], con['title'], subcon['title'], mat['title']), 'evt': event['id'], 'con': con['id'], 'mat': mat['id'], 'url': con['url'], 'speakers': speakers})

      for subfol in subcon['folders']:
        for subatt in subfol['attachments']:
          if 'download_url' in subatt and subatt['download_url'].endswith('.pdf'):
            material.append({'name': compose_name(event['date'], con['title'], subcon['title'], subatt['title']), 'evt': event['id'], 'con': con['id'], 'mat': subatt['id'], 'url': con['url'], 'speakers': speakers})
  
  return material


def download_material(mat, out_dir, domain, api_key, api_secret):
    
  path = '/export/event/{}/session/0/contrib/{}/material/slides/{}.bin'.format(mat['evt'], mat['con'], mat['mat'])

  url = domain + build_indico_request(path, {}, api_key, api_secret)

  response = requests.get(url)

  if response.status_code != 200:
    print('WARNING: [download_material] status_code', response.status_code, '!= 200 for url', url)
    return None

  open('tmp.pdf', 'wb').write(response.content)

  doc = fitz.open('tmp.pdf')

  text = doc[0].get_text()

  names = '_'.join([word for word in text.split() if word in mat['speakers']])
  
  out_path = out_dir + '/' + mat['name'].replace('_', '_' + names + '_', 1)
  
  print('  downloading:', out_path)

  for page in doc:
    page.insert_link({'kind': 2, 'xref': 0, 'from': fitz.Rect(0, 0, 10, 10), 'uri': mat['url']})

  doc.save(out_path)

  os.remove('tmp.pdf')

if __name__ == '__main__':
  main()
