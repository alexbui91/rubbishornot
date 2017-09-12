import requests
import urllib

from BeautifulSoup import BeautifulStoneSoup as Soup
import json
from urlparse import urlparse

import numpy as np

import utils
from dragnet import content_extractor


def scrape_list(sites):
    for x in sites:
        #create folder if not exists
        folder = get_domain_name(x)
        utils.create_folder(folder)
        urls = parse_sitemap(x)
        get_articles(folder, urls)
        json_data = json.dumps({'data': urls})
        utils.save_file('%s/sitemap.json' % folder, json_data, use_pickle=False)


def get_domain_name(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc

def parse_sitemap(url_string, url_links=None):
    if not url_links:
        url_links = []
    resp = requests.get(url_string)
    if 200 != resp.status_code:
        return False
    soup = Soup(resp.content)
    sitemap = soup.findAll('sitemapindex')
    url_set = soup.findAll('urlset')
    locs = []
    if sitemap:
        locs = [s.string for s in soup.findAll('loc')]
        for l in locs:
            url_links = parse_sitemap(l, url_links)
    elif url_set:
        urls = soup.findAll('url')
        if urls:
            if '.html' in urls[0].find('loc').string:
                for u in urls:
                    link = u.find('loc').string
                    img_src = [
                        img.find('image:loc').string for img in u.findAll('image:image')]
                    url_links.append({'link': link, 'images': img_src})
    return url_links


# scrape one list of articles 
def get_articles(folder, sitemap):
    for index, a in enumerate(sitemap):
        article = get_article_name(index)

        base = 'crawling/%s/%s' % (folder, article)
        r = requests.get(a['link'])
        
        content = content_extractor.analyze(r.content)
        utils.save_file(base + '.txt', content, False)
        #get images
        get_images(base, a['images'])


# download image inside article
def get_images(base, img_src):
    utils.create_folder(base)
    for index, img in enumerate(img_src):
        f = open("%s/%i.jpg" % (base, index),'wb')
        f.write(requests.get(img).content)
        f.close()


# fill index article with '000000' -> '000123'
def get_article_name(index, max_length=6):
    try:
        str_index = str(index)
        end = -len(str_index)
        arr = np.zeros(max_length, dtype='int32')
        for index, i in enumerate(str_index):
            arr[index + end] = int(i)
        return ''.join([str(x) for x in arr])
    except Exception:
        print('Max length of title is %' & max_length)
        return '000000'

# print(get_article_name(1234567))
get_articles('tokhoe.com', [{"images": ["https://tokhoe.com/wp-content/uploads/2016/09/thumb.jpg"], "link": "https://tokhoe.com/song-khoe/giu-duoc-thoi-quen-uong-du-nuoc-moi-ngay-ban-se-dat-duoc-vo-loi-ich-khong-tuong-6.html"}])
# scrape_list(['https://tokhoe.com/post-sitemap1.xml'])