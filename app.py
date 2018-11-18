import os, config, requests, json, time, datetime
from flask import Flask, render_template, redirect, request, url_for, session
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
        user_read_list = mongo.db.user_comic_list.find({ "user_name" : session['user'],
                                                          "comic_status" : { "$eq" : "read" } })

        return render_template('user_home.html',
                                user_unread=user_unread_list,
                                user_read=user_read_list)
    else:
        return render_template('index.html')

        
@app.route('/mark_comic_read/<mark_comic_id>')
def mark_comic_read(mark_comic_id):
    if 'user' in session:
        comic_to_update = mongo.db.user_comic_list.find_one({ "_id" : ObjectId(mark_comic_id)})
        print(comic_to_update)
        mongo.db.user_comic_list.update(
            {"_id": ObjectId(mark_comic_id)},
            {
                "comic_series_id": comic_to_update['comic_series_id'],
                "comic_id": comic_to_update['comic_id'],
                "user_list_identifier": comic_to_update['user_list_identifier'],
                "comic_status": "read",
                "cw_add_db": comic_to_update['cw_add_db'],
                "comic_title": comic_to_update['comic_title'],
                "user_name": session['user'],
                "comic_image": comic_to_update['comic_image'],
                "date_read": datetime.date.today().strftime("%d%m%Y")
            })
        return redirect('user_home')
    else:
        return render_template('index.html')


@app.route('/comic_delete/<delete_id>')
def comic_delete(delete_id):
    mongo.db.user_comic_list.remove({'_id': ObjectId(delete_id)})
    return redirect('user_home')

    
@app.route('/add_comics')
def add_comics():
    if 'user' in session:
        new_comics_list=mongo.db.comics.find({ "cw_add_db" : datetime.date.today().strftime("%V%Y") })
        old_comics_list=mongo.db.comics.find({ "cw_add_db" : { "$ne" : datetime.date.today().strftime("%V%Y") } })
        user_comics=mongo.db.user_comic_list.find({ "user_name" : session['user'] })
        check = [i['comic_id'] for i in user_comics]
        return render_template('add_comics.html',
        new_comics=new_comics_list, old_comics=old_comics_list, check_list=check)
    else:
        return render_template('index.html')

    
@app.route('/add_comic_to_list/<comic_add>')
def add_comic_to_list(comic_add):
    if 'user' in session:
        comic_to_add = mongo.db.comics.find_one({ "comic_id" : int(comic_add) })
        user_db_entry = mongo.db.users.find_one({ "user_name" : session['user']})
        user_list_identifier = user_db_entry['_id']
        new_comic = { "user_list_identifier": user_list_identifier,
                      "user_name" : session['user'],
                      "comic_title" : comic_to_add['comic_title'],
                      "comic_id" : comic_to_add['comic_id'],
                      "comic_series_id" : comic_to_add['comic_series_id'],
                      "comic_image" : comic_to_add['comic_image'],
                      "cw_add_db" : comic_to_add['cw_add_db'],
                      "comic_status" : "unread"}
        mongo.db.user_comic_list.insert_one(new_comic)
        return redirect('add_comics',code=204)
    else:
        return render_template('index.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')
    

@app.route('/sign_up_submit', methods=["POST"])
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
    

@app.route('/sign_in_submit', methods=["POST"])
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
