 # -*- coding: utf-8 -*-

from models import Data, session, table_name

import json
import logging
import os
import feedparser
from datetime import datetime

from grab.spider import Spider, Task
from grab.tools import html

from grab.tools.logs import default_logging
from hashlib import sha1

default_logging(level=logging.DEBUG)

path = os.path.dirname(os.path.abspath(__file__))
URLS_FILE = os.path.join(path, 'urls.txt')


RSS_LINK = 'http://pathmark.inserts2online.com/rss.jsp?drpStoreID={0}'

IMAGE_DIR = os.path.join(path, 'images/')

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
                    base_name = os.path.join(IMAGE_DIR, table_name, brand, sha1(image_link).hexdigest()+'.jpg')
                    # image = sys.path.join([IMAGE_DIR, brand, base_name])
                    image = base_name
                    self.add_task(Task(name='save_image', url=image_link, image_name=image))
                except Exception:
                    pass

                data = Data(store_number.encode('utf-8'), product.encode('utf-8'), description.encode('utf-8'), price.encode('utf-8'),
                            saving.encode('utf-8'), valid_from, valid_to, image)

                session.add(data)
                session.commit()


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
