#!/usr/bin/python
import config, requests, json, pymongo
from datetime import datetime


MONGODB_URI = config.mongo['uri']
DBS_NAME = config.mongo['db']
COLLECTION_NAME = config.mongo['comics']


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Failed connecting MongoDB: %s") % e


conn = mongo_connect(MONGODB_URI)
comics = conn[DBS_NAME][COLLECTION_NAME]


def main():
    check_against = comics.find()
    check_list = [i['comic_id'] for i in check_against]
    
    new_comics_list_raw = requests.get(config.marvel_url)

    new_comics_list_full_tree = new_comics_list_raw.json()
    new_comics_short_tree = new_comics_list_full_tree['data']['results']

    x=0
    while x < len(new_comics_short_tree):
        if not new_comics_short_tree[x]['id'] in check_list:
            comic_id = new_comics_short_tree[x]['id']
            comic_title = new_comics_short_tree[x]['title']
            
            on_sale_date_raw = new_comics_short_tree[x]['dates']['type'=='onsaleDate']['date'].split('T')
            on_sale_date = on_sale_date_raw[0]

            comic_image_non_ssl_front = new_comics_short_tree[x]['thumbnail']['path']
            comic_image_strip_protocol = comic_image_non_ssl_front.split('//')
            
            comic_image = 'https://' + comic_image_strip_protocol[1]\
            + '/portrait_large.'\
            + new_comics_short_tree[x]['thumbnail']['extension']
            
            comic_image_fs = 'https://' + comic_image_strip_protocol[1]\
            + '/detail.'\
            + new_comics_short_tree[x]['thumbnail']['extension']
            
            comic_series_uri = new_comics_short_tree[x]['series']['resourceURI']
            comic_series_uri_split = comic_series_uri.split('/')
            comic_series_id = comic_series_uri_split[6]
    
            new_entry = { "comic_id" : comic_id, 
                          "comic_series_id" : comic_series_id,
                          "comic_title" : comic_title,
                          "on_sale_date" : on_sale_date,
                          "comic_image" : comic_image,
                          "comic_image_fs" : comic_image_fs}
                        
            comics.insert_one(new_entry)
        x+=1

    
main()
