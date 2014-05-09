# -*- coding: utf-8 -*-


import csv
import logging
import feedparser
from datetime import datetime

from grab.spider import Spider, Task
from grab.tools import html

from grab.tools.logs import default_logging
from hashlib import sha1
import sys

default_logging(level=logging.DEBUG)

URLS_FILE = 'urls.txt'
RSS_LINK = 'http://pathmark.inserts2online.com/rss.jsp?drpStoreID={0}'

IMAGE_DIR = 'images/'
DATA_FILE = 'data.csv'

THREADS = 2


class RSSspider(Spider):
    def __init__(self):
        super(RSSspider, self).__init__(thread_number=THREADS, network_try_limit=20)

        c = csv.writer(open(DATA_FILE, 'wb'))  # First row record, clear all old data
        # data = u'StoreBrand, Address, City, State, Zip, PhoneNumber, StoreNumber'.encode('utf-8')
        data_header = u'Product, Description, Price, Saving, Valid From, Valid To, Image Path'.encode('utf-8')
        c.writerow(data_header.split(','))

    def task_generator(self):
        with open(URLS_FILE) as f:
            for url in f:
                if url.strip():
                    yield Task('initial', url=url.strip() + '/weekly-circular', base_url=url.strip())

    def task_initial(self, grab, task):

        brand = ''
        store_number = ''
        places = grab.xpath_list('//div[@id="circular-stores"]/div')
        for place in places:
            brand = place.find('div[@class="store-brand-pm"]').text_content()
            address = place.find('div[@class="store-title"]').text_content()
            city = place.find('div/span[@class="store-city"]').text_content()
            state = place.find('div/span[@class="store-state"]').text_content()
            zip = place.find('div/span[@class="store-zipcode"]').text_content()
            phone = place.find('div[@class="store-phone"]').text_content()
            store_number = place.attrib['class'].split('-')[-1]

        # Just move to grab all places
        link = RSS_LINK.format(store_number)
        print link

        feed = feedparser.parse(link)
        for item in feed['items']:
            product = ''
            description = ''
            price = ''
            saving = ''
            valid_from = ''
            valid_to = ''

            try:
                product = item['title']
            except Exception:
                pass
            try:
                description = html.strip_tags(item['description'])
            except Exception:
                pass
            try:
                price = item['vertis_price']
            except Exception:
                pass
            try:
                saving = item['vertis_moreprice']
            except Exception:
                pass
            try:
                valid_from = item['vertis_psdate']
                valid_from = datetime.strptime(' '.join(valid_from.split(' ')[:-1]), '%a, %d %B %Y %H:%M:%S')
                valid_from = valid_from.strftime('%d/%m/%Y')
            except Exception:
                pass
            try:
                valid_to = item['vertis_edate']
                valid_to = datetime.strptime(' '.join(valid_to.split(' ')[:-1]), '%a, %d %B %Y %H:%M:%S')
                valid_to = valid_to.strftime('%d/%m/%Y')
            except Exception:
                pass

            image = ''
            try:
                image_link = item['vertis_itemlargeimage']
                base_name = IMAGE_DIR + sha1(image_link).hexdigest() + '.jpg'
                # image = sys.path.join([IMAGE_DIR, brand, base_name])
                image = base_name
                self.add_task(Task(name='save_image', url=image_link, image_name=image))
            except Exception:
                pass

            data = ''
            try:
                data = [product.encode('utf-8'), description.encode('utf-8'), price.encode('utf-8'),
                        saving.encode('utf-8'), valid_from, valid_to, image]
            except Exception, ex:
                print ex
                import pdb
                pdb.set_trace()
            c = csv.writer(open('data.csv', 'ab'))
            c.writerow(data)

    def task_save_image(self, grab, task):
        name = task.image_name
        grab.response.save(name, create_dirs=True)


def main():
    bot = RSSspider()

    # bot.setup_proxylist(proxy_file='proxy.lst')
    bot.setup_grab(hammer_mode=True)

    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print bot.render_stats()
    print 'All done'


if __name__ == '__main__':
    print 'Start working'
    default_logging(level=logging.DEBUG)
    main()
