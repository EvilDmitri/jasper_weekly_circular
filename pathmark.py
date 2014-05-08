# -*- coding: utf-8 -*-


import csv

from grab.spider import Spider, Task
from grab import DataNotFound
from grab.tools import russian
import logging
from grab.tools.logs import default_logging


default_logging(level=logging.DEBUG)



URLS_FILE = 'urls.txt'
BASE_URL = 'http://pathmark.inserts2online.com/'
RSS_LINK = 'http://pathmark.inserts2online.com/rss.jsp?drpStoreID={0}&categories=all'

IMAGE_DIR = 'images'
DATA_FILE = 'data.csv'

THREADS = 2


class RSSspider(Spider):

    def __init__(self):
        super(RSSspider, self).__init__(thread_number=THREADS, network_try_limit=20)

        c = csv.writer(open(DATA_FILE, 'wb'))  # First row record, clear all old data
        data = u'StoreBrand, Address, City, State, Zip, PhoneNumber, StoreNumber'.encode('utf-8')
        c.writerow(data.split(','))

        # Ugly photo name counter
        self.counter = 0

    def task_generator(self):
        with open(URLS_FILE) as f:
            for url in f:
                if url.strip():
                    yield Task('initial', url=url.strip())


    def task_initial(self, grab, task):

        global store_number
        places = grab.xpath_list('//div[@id="circular-stores"]/div')
        for place in places:
            brand = place.find('div[@class="store-brand-pm"]')
            address = place.find('div[@class="store-title"]')
            city = place.find('div/span[@class="store-city"]')
            state = place.find('div/span[@class="store-state"]')
            zip = place.find('div/span[@class="store-zipcode"]')
            phone = place.find('div[@class="store-phone"]')
            store_number = place.attrib['class'].split('-')[-1]

        link = RSS_LINK.format(store_number)
        self.add_task(Task('get_rss', url=link))

    def task_get_rss(self, grab, task):


        link = BASE_URL + image_link
        self.add_task(Task(name='save_image', url=link, image_name=name))
        pass

    def task_save_image(self, grab, task):
        name = task.image_name
        grab.response.save(name, create_dirs=True)


def main():

    bot = RSSspider()

    # bot.setup_proxylist(proxy_file='proxy.lst')
    #bot.load_proxylist('proxy.lst', file)
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
