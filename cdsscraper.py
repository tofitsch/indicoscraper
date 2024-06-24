import requests
import fitz
import sys
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def main():

  _, url, rex, out_dir = sys.argv

  url = url.replace('https://', '').replace('http://', '')

  url = url.split('&')[0]

  domain, suffix = url.split('/')

  domain = 'http://' + domain
  suffix = '/' + suffix

  print('domain:', domain)
  print('suffix:', suffix)
  print('regex:', rex)
  print('out_dir:', out_dir)

  Path(out_dir).mkdir(parents=True, exist_ok=True)

  read_rss(domain, suffix, out_dir, rex)


def read_rss(domain, suffix, out_dir, rex):
  
  material = {}

  while suffix:
  
    url = domain + suffix
    print(url)
  
    response = requests.get(url)
  
    if response.status_code != 200:
      print('WARNING: [read_rss] status_code', response.status_code, ' != 200 for url', url)
      break
  
    tree = ET.fromstring(response.content)

    for item in tree.findall('.//item'):
        
        link = item.find('link').text
        print(link)
  
        media_list = item.findall('.//media:content', {'media': 'http://search.yahoo.com/mrss/'})

        for media_content in media_list:
          
          media_url = media_content.attrib.get('url')

          if media_url.endswith('.pdf'):

            download_material(media_url, out_dir, rex)
  
    next_link = tree.find(".//{http://www.w3.org/2005/Atom}link[@rel='next']")
  
    if next_link == None:
      break
  
    suffix = next_link.attrib.get('href')


def download_material(media_url, out_dir, rex):
  
  out_path = out_dir + '/cds' + media_url.split('/')[-3] + '_' + media_url.split('/')[-1]

  if os.path.exists(out_path):

    print('file exists. skipping download')

    return


  if not re.match(rex, out_path):
    return 
  
  print('  downloading:', media_url)

  response = requests.get(media_url)

  if response.status_code != 200:
    print('WARNING: [download_material] status_code', response.status_code, ' != 200 for url', media_url)
    return

  content_type = response.headers.get('content-type')

  if not 'application/pdf' in content_type:
    print('WARNING: [download_material] content-type', content_type, '!= applicaton/pdf for url ', media_url)
    return
  
  tmp_path = 'cds_tmp.pdf'

  open(tmp_path, 'wb').write(response.content)

  doc = fitz.open(tmp_path)

  for page in doc:
    page.insert_link({'kind': 2, 'xref': 0, 'from': fitz.Rect(0, 0, 10, 10), 'uri': media_url})

  doc.save(out_path)

  os.remove(tmp_path)

if __name__ == '__main__':
  main()
