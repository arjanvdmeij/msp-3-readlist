import os, config, requests, json, time, datetime
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = config.secret_key

app.config["MONGO_DBNAME"] = config.mongo['db']
app.config["MONGO_URI"] = config.mongo['uri']

mongo = PyMongo(app)

def refresh_comics():
    new_comics = mongo.db.new_comics
    new_comics_list_raw = requests.get(config.marvel_url)
    new_comics_list_full_tree = new_comics_list_raw.json()
    new_comics_short_tree = new_comics_list_full_tree['data']['results']

    new_comics.delete_many({})
    x=0
    while x < len(new_comics_short_tree):
        comic_id = new_comics_short_tree[x]['id']
        comic_title = new_comics_short_tree[x]['title']
        comic_image_non_ssl = new_comics_short_tree[x]['thumbnail']['path']\
        + '/portrait_large.'\
        + new_comics_short_tree[x]['thumbnail']['extension']
        comic_image_strip_protocol = comic_image_non_ssl.split('//')
        comic_image = 'https://' + comic_image_strip_protocol[1]
        new_entry = { "comic_id" : comic_id, "comic_title" : comic_title,
                    "comic_image" : comic_image }
        new_comics.insert_one(new_entry)
        x+=1
        
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/add_comics')
def add_comics():
    return render_template('add_comics.html',
    new_comics_list=mongo.db.new_comics.find())
    
@app.route('/sign_up', methods=["GET","POST"])
def sign_up():
    return render_template('sign_up.html')
    
@app.route('/sign_up_submit', methods=["GET","POST"])
def sign_up_submit():
    users = mongo.db.users
    if users.find({ "user_name" : request.form["uname"]}):
        print('\nUsername already exists\n') # fix hier iets mee om form terug te zetten met melding
        return redirect(url_for('index'))
    if request.form["pwd"] == request.form["pwd_check"]:
        pwd_hash = generate_password_hash(request.form['pwd'])
        print('pwd_hash: ',pwd_hash)
        user_name = request.form['uname']
        print('user_name: ',user_name)
        new_user = { "user_name" : user_name, "pwd" : pwd_hash, "creation_date" : datetime.date.today().strftime("%Y%m%d") }
        print('new_user: ',new_user)
        users.insert(new_user)
        return redirect(url_for('index'))
    else:
        print('\n\nIt\'s safe to say that shit went sideways, in a colossal manner..\n\n')
        return redirect(url_for('sign_up'))
    
@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')
    
@app.route('/sign_in_submit', methods=["POST"])
def sign_in_submit():
    users=mongo.db.users
    user_name = users.find_one({"user_name" : request.form['uname']})
    print('\nDatabase pwd string: ',user_name['pwd'])
    pwd_hash_check = check_password_hash(user_name['pwd'], request.form['pwd'])
    print('\nForm pwd hash check: ', pwd_hash_check)
    if user_name:
        if  pwd_hash_check:
            print('\n\nPerfectly balanced, as all things should be..\n\n')
            return redirect(url_for('add_comics')) # aanpassen naar user specific page, eerst duidelijk 'inloggen'..
        else:
            print('\n\nMr. Stark, I don\'t feel so good..\n\n')
            return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host=os.getenv('IP'), 
            port=int(os.getenv('PORT')), 
            debug=True)
