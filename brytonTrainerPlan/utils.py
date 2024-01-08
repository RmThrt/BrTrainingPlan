import os
import re
import unicodedata

import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


def prepare_output_folder(output_folder, training_plan,zwift_url):
    os.makedirs(output_folder) if not os.path.exists(output_folder) else None

    req = Request(zwift_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')
    cnt = str(urlopen(req).read())
    f = open(output_folder + "/" + training_plan + ".html", 'w', encoding='utf-8')
    f.write(cnt)
    f.close

def zwo_to_csv(directory, filename, csvName):
    os.system("python ./brytonTrainerPlan/zwoparse.py " + directory + filename + " -f 266 -k 71 -t csv -o " + csvName)




def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def search_in_google(search_term):      
    url = f"https://google.com/search?q={search_term}"

    headers = {
	'Accept' : '*/*',
	'Accept-Language': 'fr-FR,fr;q=0.5',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    # headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
    parameters = {'q': search_term}
    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, "html.parser")
    try:
        search = soup.find(id = 'search')
        first_link = search.find('a')
        return first_link['href']
    except : 
        return url

    
    