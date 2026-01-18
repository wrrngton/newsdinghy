import datetime
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime


def is_url_rss(soup: str) -> bool:
    rss_tag = soup.find('rss')

    if not rss_tag:
        return False, "URL is not an rss feed"

    return True, "successful"


def generate_soup(url: str) -> str:
    res = requests.get(url)
    status_code = res.status_code

    if status_code != 200:
        return False, 'Could not fetch feed url when processing articles'

    html = res.text
    soup = BeautifulSoup(html, 'xml')

    return soup, 'Success'


def process_feed_articles(feed_url: str) -> dict:
    soup, message = generate_soup(feed_url)

    if not soup:
        return False, message

    articles = soup.find_all('item')

    articles_json = [
        {
            "title": a.find('title').string,
            "description": a.find('description').string,
            "timestamp": convert_timestamp_to_utc(a.find('pubDate').string),
            "url": a.find('guid').string,
        }
        for a in articles
    ]

    return articles_json, message


def get_feed_info(soup: classmethod) -> dict:
    website_url = soup.find('link').string
    website_url_split = urlparse(website_url)
    domain_name = website_url_split.netloc
    url = soup.find('atom:link').get('href')
    author = domain_name
    description = soup.find('description').string
    website = soup.find('link').string

    feed_json = {
        'url': url,
        'author': author,
        'description': description,
        'website': website
    }

    return feed_json

def convert_timestamp_to_utc(tstamp: str) -> str:
    return parsedate_to_datetime(tstamp)

