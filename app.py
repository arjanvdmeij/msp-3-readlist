import os, config, requests, json, time, datetime
from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.config["MONGO_DBNAME"] = config.mongo['db']
app.config["MONGO_URI"] = config.mongo['uri']


mongo = PyMongo(app)

        
@app.route('/')
@app.route('/home')
def index():
    if 'user' in session:
        return redirect(url_for('user_home'))
    return render_template('index.html')

    
@app.route('/user_home')
def user_home():
    if 'user' in session:
        user_unread_list = mongo.db.user_comic_list.find({ "user_name" : session['user'],
                                                          "comic_status" : { "$eq" : "unread" } })
        
        return render_template('user_home.html',
                                user_unread=user_unread_list)
    else:
        return render_template('index.html')

@app.route('/read_comics')
def read_comics():
    if 'user' in session:
        user_read_list = mongo.db.user_comic_list.find({ "user_name" : session['user'],
                                                          "comic_status" : { "$eq" : "read" } })
        return render_template('read_comics.html',
                                user_read=user_read_list)

        
@app.route('/mark_comic_read', methods=['POST'])
def mark_comic_read():
    if 'user' in session:
        posted = request.json
        comic_to_update = mongo.db.user_comic_list.find_one({ "_id" : ObjectId(posted['_id']) })
        mongo.db.user_comic_list.update(
            {"_id": ObjectId(posted['_id'])},
            {
                "comic_series_id": comic_to_update['comic_series_id'],
                "comic_id": comic_to_update['comic_id'],
                "user_list_identifier": comic_to_update['user_list_identifier'],
                "comic_status": "read",
                "on_sale_date": comic_to_update['on_sale_date'],
                "comic_title": comic_to_update['comic_title'],
                "user_name": session['user'],
                "comic_image": comic_to_update['comic_image'],
                "comic_image_fs" : comic_to_update['comic_image_fs'],
                "date_read": config.date_today })
        return jsonify({ 'result' : 'success' })
    else:
        return render_template('index.html')


@app.route('/delete_comic', methods=['POST'])
def delete_comic():
    if 'user' in session:
        posted = request.json
        mongo.db.user_comic_list.remove({'_id': ObjectId(posted['_id'])})
        return jsonify({ 'result' : 'success' })
    else:
        return render_template('index.html')
    
@app.route('/add_comics')
def add_comics():
    if 'user' in session:
        new_comics_list=mongo.db.comics.find({ "$query": { "on_sale_date" : { "$gte" : config.date_week_ago }}, "$orderby": { "comic_series_id" : 1 }})
        user_comics=mongo.db.user_comic_list.find({ "user_name" : session['user'] })
        check = [i['comic_id'] for i in user_comics]
        now = datetime.datetime.now().strftime("%b-%d")
        then = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%b-%d")
        return render_template('add_comics.html',
        new_comics=new_comics_list, check_list=check, 
        today=now, week_ago=then)
    else:
        return render_template('index.html')


@app.route('/add_comics_all')
def add_comics_all():
    if 'user' in session:
        all_comics_list=mongo.db.comics.find()
        user_comics=mongo.db.user_comic_list.find({ "user_name" : session['user'] })
        check = [i['comic_id'] for i in user_comics]
        return render_template('add_comics_all.html',
        all_comics=all_comics_list, 
        check_list=check)
    else:
        return render_template('index.html')


@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    if 'user' in session:
        posted = request.json
        comic_to_add = mongo.db.comics.find_one({ "_id" : ObjectId(posted['_id']) })
        user_db_entry = mongo.db.users.find_one({ "user_name" : session['user']})
        user_list_identifier = user_db_entry['_id']
        new_comic = { "user_list_identifier": user_list_identifier,
                      "user_name" : session['user'],
                      "comic_title" : comic_to_add['comic_title'],
                      "comic_id" : comic_to_add['comic_id'],
                      "comic_series_id" : comic_to_add['comic_series_id'],
                      "comic_image" : comic_to_add['comic_image'],
                      "comic_image_fs" : comic_to_add['comic_image_fs'],
                      "on_sale_date" : comic_to_add['on_sale_date'],
                      "comic_status" : "unread"}
        mongo.db.user_comic_list.insert_one(new_comic)
        return jsonify({ 'result' : 'success' })
    else:
        return render_template('index.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')
    

@app.route('/sign_up_submit', methods=['POST'])
def sign_up_submit():
    users = mongo.db.users
        
    if users.find_one({ "user_name" : request.form["uname"]}):
        print('\nUsername already exists\n')
        return render_template('sign_up.html', 
                                u_error = ' - This name is taken, try again')
    
    if request.form["pwd"] != request.form["pwd_check"]:
        print('\nPasswords don\'t match\n')
        return render_template('sign_up.html', 
                                u_error = '', 
                                p_error = ' -  Passwords did not match, try again', 
                                if_pw_error = request.form['uname'])
        
    pwd_hash = generate_password_hash(request.form['pwd'])
    user_name = request.form['uname']
    session['user'] = request.form['uname']
    new_user = { "user_name" : user_name, 
                 "pwd" : pwd_hash, 
                 "creation_date" : datetime.date.today().strftime("%Y%m%d") }
    users.insert(new_user)
    print('\nUser added\n')
    return redirect(url_for('index'))
    

@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')
    

@app.route('/sign_in_submit', methods=['POST'])
def sign_in_submit():
    users=mongo.db.users
    user_name = users.find_one({"user_name" : request.form['uname']})
    
    if not user_name:
        return render_template('sign_in.html', 
                                u_error = ' - User does not exist, try again')
    if user_name:
        pwd_hash_check = check_password_hash(user_name['pwd'], request.form['pwd'])
        if  pwd_hash_check:
            session['user'] = request.form['uname']
            return redirect(url_for('user_home'))
        else:
            return render_template('sign_in.html', 
                                    p_error = ' - Incorrect password, try again',
                                    if_pw_error = request.form['uname'])


@app.route('/log_out')
def log_out():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = config.secret_key
    app.run(host=os.getenv('IP'), 
            port=int(os.getenv('PORT')),
            debug=True)
