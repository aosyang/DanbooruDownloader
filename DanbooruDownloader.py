import urllib2
import urlparse
from bs4 import BeautifulSoup, SoupStrainer
from os.path import basename
import socket
import os

baseurl = "http://danbooru.donmai.us/posts?utf8=%E2%9C%93"

# Tag for the images you want to fetch
# Note: For multiple tags, separate them with '+'
#       eg: "misaki_kurehito+kasumigaoka_utaha"
tag = "misaki_kurehito"

total_img_count = 0

def user_agent(url):
    req_header = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req_timeout = 20
    html = None
    try:
        req = urllib2.Request(url, None, req_header)
        page = urllib2.urlopen(req, None, req_timeout)
        html = page
    except urllib2.URLError as e:
        print e.message
    except socket.timeout as e:
        user_agent(url)
    return html


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def save_page_img(url):
    print 'Fetching images from: ' + url
    page = user_agent(url)
    soup = BeautifulSoup(page, "html.parser")
    img = soup.find_all(['img'])
    img_count = 0
    for myimg in img:
        link = myimg.get('src')
        print link
        if 'preview' not in link:
            if 'sample' in link:
                resize_link = soup.find(id='image-resize-link')
                link = resize_link.get('href')
            link = urlparse.urljoin(baseurl, link)

            filename = u'./' + tag + '/' + basename(link)

            print link
            img_count += 1
            if not os.path.exists(filename):
                with open(filename, 'wb') as code:
                    content = user_agent(link).read()
                    code.write(content)
    return img_count


def danbooru_page_loop(pageid):
    url = baseurl + '&page=%s' % pageid
    print url
    page = user_agent(url)

    if page is None:
        return 0

    last_page = 1
    page_keyword = 'page=' + str(pageid + 1)

    soup = BeautifulSoup(page, "html.parser")
    img_count = 0
    for link in soup.find_all('a'):
        link_to_img = link.get('href')
        if '/posts/' in link_to_img and 'random' not in link_to_img and 'popular' not in link_to_img:
            link_to_img = urlparse.urljoin(baseurl, link_to_img)
            img_count += save_page_img(link_to_img)
        elif page_keyword in link_to_img:
            last_page = 0
    print 'Finished fetching page', pageid, 'with', img_count, 'images'

    global total_img_count
    total_img_count += img_count

    if last_page == 1:
        return -1
    else:
        return img_count


ensure_dir(u'./' + tag + '/')
baseurl = baseurl + '&tags=' + tag
page_start = 1
page_stop = 1000

for i in range(page_start, page_stop):
    page_img_count = danbooru_page_loop(i)
    if page_img_count == -1:
        print 'No more pages, exit.'
        break

print 'Total fetched', total_img_count, 'images'
