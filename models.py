from time import gmtime, strftime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, orm

engine = create_engine('mysql://scraper@localhost/scraper_data')

meta = MetaData()

table_name = strftime('%d_%m_%Y_%H_%M_%S', gmtime())

# Store Number, Product, Description, Price, Saving, Valid From, Valid To, Image Path
data_table = Table(table_name, meta,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('store_number', String(254)),
                   Column('product', String(254)),
                   Column('description', String(10000)),
                   Column('price', String(1024)),
                   Column('saving', String(1024)),
                   Column('valid_from', String(254)),
                   Column('valid_to', String(254)),
                   Column('image_path', String(254))
                   )

meta.create_all(engine)


class Data(object):
    def __init__(self, store_number, product, description, price, saving, valid_from, valid_to, image_path):
        self.store_number = store_number
        self.product = product
        self.description = description
        self.price = price
        self.saving = saving
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.image_path = image_path


from sqlalchemy.orm import mapper
mapper(Data, data_table)


from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


session = Session()

