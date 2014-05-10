 # -*- coding: utf-8 -*-


import csv
import json
import logging
import os
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

    def task_generator(self):
        with open(URLS_FILE) as json_data:
            data = json.load(json_data)
            sites = data['sites']
            for site in sites:
                yield Task('initial', url=site['link'], rss_url=site['rss'])

    def task_initial(self, grab, task):
        brand = ''
        store_number = ''
        places = grab.xpath_list('//div[@id="circular-stores"]/div')
        for place in places:
            brand = place[0].text_content()
            address = place.find('div[@class="store-title"]').text_content()
            city = place.find('div/span[@class="store-city"]').text_content()
            state = place.find('div/span[@class="store-state"]').text_content()
            zip = place.find('div/span[@class="store-zipcode"]').text_content()
            phone = place.find('div[@class="store-phone"]').text_content()
            store_number = place.attrib['class'].split('-')[-1]

            link = task.rss_url.format(store_number)
            feed = feedparser.parse(link)
            file_name = link.split('//')[1].split('.')[0]     # Get the first domain name from the url as the leading path

            directory = os.path.join('data', file_name, store_number)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_name = os.path.join(directory, 'data.csv')
            print file_name
            f = csv.writer(open(file_name, 'wb'))
            # First row record, clear all old data
            # data = u'StoreBrand, Address, City, State, Zip, PhoneNumber, StoreNumber'.encode('utf-8')
            data_header = u'Product, Description, Price, Saving, Valid From, Valid To, Image Path'.encode('utf-8')
            f.writerow(data_header.split(','))

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
                    base_name = os.path.join(IMAGE_DIR, brand, sha1(image_link).hexdigest()+'.jpg')
                    # image = sys.path.join([IMAGE_DIR, brand, base_name])
                    image = base_name
                    self.add_task(Task(name='save_image', url=image_link, image_name=image))
                except Exception:
                    pass

                data = [product.encode('utf-8'), description.encode('utf-8'), price.encode('utf-8'),
                        saving.encode('utf-8'), valid_from, valid_to, image]
                f.writerow(data)

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
