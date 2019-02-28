#!/usr/bin/python
""" This file performs the updates to the comics list.
It is run daily, despite comics running weekly, to ensure that
any intermediate releases for specials are caught as soon as added.
It relies on the config.py file used also by the app. Always check
both when performing changes to config.py.
"""
import config, requests, json, pymongo, os


MONGODB_URI = config.mongodb

""" decide on which mongodb to use based on environment """
if os.getenv('C9_HOSTNAME'):
    DBS_NAME = 'marvel-dev-read-list'
else:
    DBS_NAME = 'marvel_read_list'
    
COLLECTION_NAME = 'comics'


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Failed connecting MongoDB: %s") % e


conn = mongo_connect(MONGODB_URI)
comics = conn[DBS_NAME][COLLECTION_NAME]


def main():
    """ Get current comics to avoid dual adding """
    check_against = comics.find()
    check_list = [i['comic_id'] for i in check_against]
    
    """ Get new comics from Marvel and trim results to
    have a shorter path to work from
    """
    _raw = requests.get(config.marvel_url)
    _full_tree = _raw.json()
    short_tree = _full_tree['data']['results']
    
    """ Process results and add to database """
    x=0
    while x < len(short_tree):
        if not short_tree[x]['id'] in check_list:
            id = short_tree[x]['id']
            title = short_tree[x]['title']
            
            # strip onsaleDate to just the date
            _raw_date = short_tree[x]['dates']['type'=='onsaleDate']['date'].split('T')
            date = _raw_date[0]
            
            # rebuild image paths to https paths to avoid error messages
            _non_ssl_front = short_tree[x]['thumbnail']['path']
            _strip_protocol = _non_ssl_front.split('//')
            
            image = 'https://' + _strip_protocol[1]\
            + '/portrait_large.'\
            + short_tree[x]['thumbnail']['extension']
            
            image_fs = 'https://' + _strip_protocol[1]\
            + '/detail.'\
            + short_tree[x]['thumbnail']['extension']
            
            # strip the series ID from the series URI
            _series_uri = short_tree[x]['series']['resourceURI']
            _uri_split = _series_uri.split('/')
            series_id = _uri_split[6]
    
            new_entry = { "comic_id" : id, 
                          "comic_series_id" : series_id,
                          "comic_title" : title,
                          "on_sale_date" : date,
                          "comic_image" : image,
                          "comic_image_fs" : image_fs}
                        
            comics.insert_one(new_entry)
        x+=1

main()
