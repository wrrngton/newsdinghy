import datetime
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def is_url_rss(url: str) -> bool:
    res = requests.get(url)
    status_code = res.status_code

    if status_code != 200:
        return False, "URL could not be fetched" 

    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    rss_tag = soup.find('rss')

    if not rss_tag:
        return False, "URL is not an rss feed"

    return True
