'''
This file is used to store settings for both the main app.py,
as well as the update_comics.py file.
In it, those values that you want 'private' can be kept away
from the main files, where they are only called when needed.from
This specific file has been stripped of information, but can be 
used by saving it as config.py and filling out the < > blocks 
with relevant data
'''
from hashlib import md5
from time import time
from datetime import datetime, timedelta
from flask import Flask
from flask_pymongo import PyMongo

''' variables needed when getting new data from API '''
timestamp=int(time())
date_week_ago = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
date_today = datetime.now().strftime("%Y-%m-%d")

marvel = {"pub" : "<Marvel_API_public_key>",
          "priv" : "<Marvel_API_private_key>",
}

''' server requests require timestamp and hash value''' 
input_string = str(timestamp) + marvel['priv'] + marvel['pub']
key_hash = str(md5(input_string.encode("utf-8")).hexdigest())

''' rebuild API call on execution of update_comics.py '''
marvel_url = "https://gateway.marvel.com:443/v1/public/comics?"\
    + "format=comic&formatType=comic&dateRange="\
    + date_week_ago\
    + "%2C"\
    + date_today\
    + "&orderBy=title&limit=100"\
    + "&ts=" + str(timestamp)\
    + "&apikey=" + marvel['pub']\
    + "&hash=" + str(key_hash)

secret_key = '<secret_key_goes_here>' # used with Flask's session

mongodb = "mongodb://<dbuser>:<dbpassword>@ds261253.mlab.com:61253/<name_of_Mongo_database >"

''' Flask app settings for app.py, do not change '''
app = Flask(__name__)
app.config["MONGO_URI"] = mongodb
mongo = PyMongo(app)


admin_name = '<admin_username >'
admin_display_name = '<custom_displayname>'
''' mongo.db prefix required, rename admin_collection as needed '''
admin_coll = mongo.db.admin_collection

''' used in checking if three letters exist in chosen username '''
letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
           'q','r','s','t','u','v','w','x','y','z']

''' user to verify valid characters in usernames '''
valids = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
          'q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5',
          '6','7','8','9']


