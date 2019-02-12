import os
from hashlib import md5
from time import time
from datetime import datetime, timedelta
from flask import Flask
from flask_pymongo import PyMongo


secret_key = os.getenv('secret_key')

""" Time calculations for new comics """
timestamp=int(time())
date_week_ago = (datetime.now()
                - timedelta(days=6)).strftime("%Y-%m-%d")
date_today = datetime.now().strftime("%Y-%m-%d")

""" Build Marvel URL for getting new comics """
marvel = {"pub" : os.getenv('marvel_pub'),
          "priv" : os.getenv('marvel_priv'),
}

input_string = str(timestamp) + marvel['priv'] + marvel['pub']

key_hash = str(md5(input_string.encode("utf-8")).hexdigest())

marvel_url = "https://gateway.marvel.com:443/v1/public/comics?"\
    + "format=comic&formatType=comic&dateRange="\
    + date_week_ago\
    + "%2C"\
    + date_today\
    + "&orderBy=title&limit=100"\
    + "&ts=" + str(timestamp)\
    + "&apikey=" + marvel['pub']\
    + "&hash=" + str(key_hash)


mongodb = os.getenv('mongodb')

""" Username and Password validator characters """
letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
           'q','r','s','t','u','v','w','x','y','z']

valids = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
          'q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5',
          '6','7','8','9']

""" Flask base information """
app = Flask(__name__)
app.config["MONGO_URI"] = mongodb
mongo = PyMongo(app)
admin_name = os.getenv('admin_name')
admin_display_name = os.getenv('admin_display_name')
admin_coll = mongo.db.jlkagjhflakjs7845oluhgfq






