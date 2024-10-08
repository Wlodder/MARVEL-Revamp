import bs4
import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

def extract_urls_from_xml_url(xml_url):

  try:
      tree = ET.parse(xml_url)
  except ET.ParseError as e:
      print(f"error {e}")
      return []
  root = tree.getroot()
  urls = []
  
  for url_tag in root.findall('url'):
    content = url_tag.find('loc').text
    urls.append(content)

  return urls


def extract_name_from_url(url):
  req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  html = urlopen(req, timeout=300).read()
  soup = bs4.BeautifulSoup(html, "lxml")
  
  name_span = soup.find_all('span', class_='information-item__title')

  #txt = 'Vessel Type<!-- -->:'
  #name_span = soup.find('span', class_='information-item__title', text=txt)
  for span in name_span:
    if 'Vessel Type' in span:
      name_span = span
      break

  for vs in name_span:
    parent = vs.parent.parent
    te = parent.find('span', class_='information-item__value')
    if te:
      return te.text
  return None

def download_file(url, filename):
  response = requests.get(url, stream=True)
  with open(filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
      if chunk:
        f.write(chunk)

def image_download(url):
    number = url.split('/')[-1]
    photo_url = f"https://shipspotting.com/photos/big"
    
    if len(number) == 2:
      photo_url = f"{photo_url}/{number[1]}/{number[0]}/{number[0]}/{number}.jpg"
    else:
      photo_url = f"{photo_url}/{number[-1]}/{number[-2]}/{number[-3]}/{number}.jpg"
    print(photo_url)
    download_file(photo_url, f'{number}.jpg')
    return f'{number}.jpg'

# Example usage:

if __name__ == '__main__':

    if os.path.isfile('all_files.csv'):
        df = pd.read_csv('all_files.csv')
    else:
        df = pd.DataFrame(columns=['source_file','file_name','class_name'])
    sitemaps = os.listdir('./sitemaps')

    for st in sitemaps:
        xml_url=f'./sitemaps/{st}'
        extracted_urls = extract_urls_from_xml_url(xml_url)

        # Example usage:
        i =0 
        for url in extracted_urls:
            i += 1
            extracted_name = extract_name_from_url(url)
            print(url, extracted_name) 
            fname = image_download(url)

            new_row = {'source_file':st,'file_name':fname,'class_name':extracted_name}
            df = df.append(new_row, ignore_index=True)

            df.to_csv('all_files.csv', index=None)
            if i > 10:
                break
