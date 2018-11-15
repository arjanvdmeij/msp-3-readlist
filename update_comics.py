import os, config, requests, json, datetime, pymongo

MONGODB_URI = config.mongo['uri']
DBS_NAME = config.mongo['db']
COLLECTION_NAME = 'new_comics'

def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Failed connecting MongoDB: %s") % e

conn = mongo_connect(MONGODB_URI)
coll = conn[DBS_NAME][COLLECTION_NAME]

def refresh_comics():
    new_comics = coll
    new_comics_list_raw = requests.get(config.marvel_url)
    new_comics_list_full_tree = new_comics_list_raw.json()
    new_comics_short_tree = new_comics_list_full_tree['data']['results']

    # new_comics.delete_many({})  --------- Commented, no need to remove
    x=0
    while x < len(new_comics_short_tree):
        comic_id = new_comics_short_tree[x]['id']
        comic_title = new_comics_short_tree[x]['title']
        comic_image_non_ssl = new_comics_short_tree[x]['thumbnail']['path']\
        + '/portrait_large.'\
        + new_comics_short_tree[x]['thumbnail']['extension']
        comic_image_strip_protocol = comic_image_non_ssl.split('//')
        comic_image = 'https://' + comic_image_strip_protocol[1]
        cw_add_db = datetime.date.today().strftime("%V")
        cy_add_db = datetime.date.today().strftime("%Y")
        new_entry = { "comic_id" : comic_id, "comic_title" : comic_title,
                    "cw_add_db" : cw_add_db,
                    "cy_add_db" : cy_add_db,
                    "comic_image" : comic_image }
        new_comics.insert_one(new_entry)
        x+=1
    print('\nComics refreshed\n')
        
refresh_comics()