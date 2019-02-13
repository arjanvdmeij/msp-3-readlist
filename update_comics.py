#!/usr/bin/python
import config, requests, json, pymongo


MONGODB_URI = config.mongodb
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
    """ Get current comics to avoid re-adding """
    check_against = comics.find()
    check_list = [i['comic_id'] for i in check_against]
    
    """ Get new comics from Marvel """
    _raw = requests.get(config.marvel_url)

    _full_tree = _raw.json()
    short_tree = _full_tree['data']['results']
    
    """ Process results and add to database """
    x=0
    while x < len(short_tree):
        if not short_tree[x]['id'] in check_list:
            id = short_tree[x]['id']
            title = short_tree[x]['title']
            
            _raw_date = short_tree[x]['dates']['type'=='onsaleDate']['date'].split('T')
            date = _raw_date[0]

            _non_ssl_front = short_tree[x]['thumbnail']['path']
            _strip_protocol = _non_ssl_front.split('//')
            
            image = 'https://' + _strip_protocol[1]\
            + '/portrait_large.'\
            + short_tree[x]['thumbnail']['extension']
            
            image_fs = 'https://' + _strip_protocol[1]\
            + '/detail.'\
            + short_tree[x]['thumbnail']['extension']
            
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
