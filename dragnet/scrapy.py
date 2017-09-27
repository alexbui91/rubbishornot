import urllib2
import requests
import os 

from BeautifulSoup import BeautifulStoneSoup as Soup
import json
from urlparse import urlparse
import argparse

import numpy as np

import utils
import properties as p

from dragnet import content_extractor


# scrape list of sitemaps as parsing
loaded = dict()

def scrape_list(sites):
    for x in sites:
        url = x.replace('\n', '')   
        print('==> scraping site: %s' % url)
        #create folder if not exists
        folder = get_domain_name(url)
        utils.create_folder('crawling/' + folder)
        j_hash = hash(url)
        json_file = '%s_sitemap.json' % j_hash
        if os.path.isfile(json_file):
            with open(json_file) as f:
                data = json.load(f)
                urls = data['data']
        else:
            urls = parse_sitemap(url)
            json_data = json.dumps({'data': urls})
            utils.save_file(json_file, json_data, use_pickle=False)
        print('total available urls: %i' % len(urls))
        get_articles(folder, urls)


def get_domain_name(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


def parse_sitemap(url_string, url_links=None):
    try:
        if not url_links:
            url_links = []
        if not 'tag' in url_string:
            r = requests.get(url_string, timeout=10)
            # html = urllib2.urlopen(url_string)
            # if 200 != resp.status_code:
            #     return []
            soup = Soup(r.text)
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
                    fir_url = urls[0].find('loc').string
                    if is_article_url(fir_url):
                        for u in urls:
                            link = u.find('loc').string
                            img_src = [
                                img.find('image:loc').string for img in u.findAll('image:image')]
                            url_links.append({'link': link, 'images': img_src})
    except Exception as e: 
        print("Error occurred during parse sitemap", e)
    return url_links


def is_article_url(url):
    parsed_uri = urlparse(url)
    parsed_uri = parsed_uri.path.split('.')
    return len(parsed_uri) > 1


# scrape one list of articles 
def get_articles(folder, sitemap):
    last_index = get_last_index('crawling/%s' % folder)
    total = len(sitemap)
    for index, a in enumerate(sitemap):
        key = hash(a['link'])
        if not key in loaded:
            loaded[key] = 1
            article = get_article_name(index + last_index)
            base = 'crawling/%s/%s' % (folder, article)
            try: 
                r = requests.get(a['link'], timeout=5)
                # r = urllib2.urlopen(a['link'])
                html = Soup(r.text)
                title = html.find('h1')
                if title:
                    title = getText(title)
                else:
                    title = ''
                content = content_extractor.analyze(r.content)
                if len(content.split(' ')) >= p.min_length:
                    # print([])
                    content = title.encode('utf=8') + '\n' + a['link'].encode('utf-8') + '\n' + content
                    utils.save_file(base + '.txt', content, False)
                    #get images
                get_images(base, a['images'])
            except requests.exceptions.Timeout:
                print("Timeout url: %s" % a['link'])
            except Exception as e:
                print("Error occured", e)
            utils.save_file('cached.pkl', loaded)
        utils.update_progress(index * 1.0 / total)


def getText(parent):
    return ''.join(parent.find(text=True)).strip()


def get_last_index(folder):
    files = os.listdir(folder)
    if not files:
        return 0
    else:
        files.sort()
        last = files[-1].split('.')[0]
        return int(last)


# download image inside article
def get_images(base, img_src):
    if img_src:
        utils.create_folder(base)
        try:
            for index, img in enumerate(img_src):
                f = open("%s/%i.%s" % (base, index, img.split('.')[-1]),'wb')
                f.write(requests.get(img, timeout=2).content)
                f.close()
        except Exception e:
            print("Error when load images", e)
        if not len(os.listdir(base)):
            os.rmdir(base)


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


def main(urls, file=False):
    a_load = utils.load_file('cached.pkl')
    if a_load: 
        loaded = a_load
    if file:
        urls = utils.load_file(urls)
        # bad = utils.load_file('sitemap_bad.txt')
    elif urls:
        urls = urls.split(',')
    scrape_list(urls)
    # bad = utils.load_file('sitemap_bad.txt')


# print(get_article_name(1234567))
# get_articles('tokhoe.com', [{"images": ["https://tokhoe.com/wp-content/uploads/2016/09/thumb.jpg"], "link": "https://tokhoe.com/song-khoe/giu-duoc-thoi-quen-uong-du-nuoc-moi-ngay-ban-se-dat-duoc-vo-loi-ich-khong-tuong-6.html"}])
# scrape_list(['https://tokhoe.com/post-sitemap1.xml'])
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=int, default=0)
    parser.add_argument("-u", "--urls")
    args = parser.parse_args()
    if args.file:
        main(args.urls, file=True)
    elif args.urls:
        main(args.urls, file=False)
# parse_sitemap('http://dantri.com.vn/sitemaps/sitemap-index.xml')