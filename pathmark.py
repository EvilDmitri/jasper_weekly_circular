# -*- coding: utf-8 -*-


import csv
import logging
import feedparser

from grab.spider import Spider, Task
from grab.tools import html

from grab.tools.logs import default_logging
from hashlib import sha1

default_logging(level=logging.DEBUG)

URLS_FILE = 'urls.txt'
RSS_LINK = '/rss.jsp?drpStoreID={0}'

IMAGE_DIR = 'images'
DATA_FILE = 'data.csv'

THREADS = 2


class RSSspider(Spider):
    def __init__(self):
        super(RSSspider, self).__init__(thread_number=THREADS, network_try_limit=20)

        c = csv.writer(open(DATA_FILE, 'wb'))  # First row record, clear all old data
        # data = u'StoreBrand, Address, City, State, Zip, PhoneNumber, StoreNumber'.encode('utf-8')
        data_header = u'Product, Description, Price, Saving, Valid From, Valid To'.encode('utf-8')
        c.writerow(data_header.split(','))

    def task_generator(self):
        with open(URLS_FILE) as f:
            for url in f:
                if url.strip():
                    yield Task('initial', url=url.strip() + '/weekly-circular', base_url=url.strip())

    def task_initial(self, grab, task):

        places = grab.xpath_list('//div[@id="circular-stores"]/div')
        for place in places:
            brand = place.find('div[@class="store-brand-pm"]')
            address = place.find('div[@class="store-title"]')
            city = place.find('div/span[@class="store-city"]')
            state = place.find('div/span[@class="store-state"]')
            zip = place.find('div/span[@class="store-zipcode"]')
            phone = place.find('div[@class="store-phone"]')
            store_number = place.attrib['class'].split('-')[-1]

        link = task.base_url + RSS_LINK.format(store_number)

        feed = feedparser.parse(link)
        for item in feed['items']:
            product = item['title']
            description = html.strip_tags(item['description'])
            price = item['vertis_price']
            saving = item['vertis_moreprice']
            valid_from = item['vertis_psdate']
            valid_to = item['vertis_edate']

            image_link = item['vertis_itemlargeimage']
            base_name = sha1(image_link).hexdigest()
            image = '/'.join([IMAGE_DIR, brand, base_name]) + '.jpg'
            self.add_task(Task(name='save_image', url=image, image_name=image))

            try:
                data = [product, description, price, saving,
                        valid_from, valid_to, image]
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
    main()
