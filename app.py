import os, config, requests, json, time
from flask import Flask, render_template, redirect
from flask import request, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = config.app

app.config["MONGO_URI"] = config.app.config["MONGO_URI"]

mongo = config.mongo

@app.before_request
def force_https():
    """ push Flask into using https on all pages """
    if request.endpoint in app.view_functions and request.headers.get(
                                    'X-Forwarded-Proto', None) == 'http':
        return redirect(request.url.replace('http://', 'https://'))


@app.route('/')
@app.route('/home')
def index():
    """ Main page, offering instruction and login/registration """
    try:
        if 'user' in session:
            if session['user'] == config.admin_name:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user_home'))
        return render_template('index.html')
    except:
        return redirect(url_for('index'))

    
@app.route('/user_home')
def user_home():
    """ user's home page, defaults to
    the current list of comics to be read 
    """
    try:
        if session['user']:
            user = mongo.db.users.find_one({"user_name":session['user']})
            _nice = user['display_name']
            coll = mongo.db.user_comic_list
            _user_unread = coll.find({ "user_name" : session['user'],
                                    "comic_status" : { "$eq" : "unread" } })
            _count = _user_unread.count()
            return render_template('user_home.html',
                                    user_unread=_user_unread,
                                    comics_total=_count,
                                    display_name=_nice)
        else:
            print('layer 2 option 2')
            return render_template('index.html')
    except:
        return render_template('401.html')


@app.route('/user_settings')
def user_settings():
    """ user setting page, allowing password change
    or setting a custom display name 
    """
    try:
        if session['user']:
            coll = mongo.db.users
            _user = coll.find_one({"user_name":session['user']})
            return render_template('user_settings.html',
                                    user=_user,
                                    display_name=_user['display_name'])
    except:
        return render_template('401.html')


@app.route('/change_display_name', methods=['POST'])
def change_display_name():
    """ action behind button for changing display name, checking restrictions
    and returning an error or applying the new name
    """
    try:
        if session['user']:
            coll = mongo.db.users
            n_display_name = request.form['dname']
            _user = coll.find_one({"user_name":session['user']})
            if len(request.form['dname']) > 32:
                return render_template('user_settings.html',
                        d_error = " - Too many characters",
                        display_name = _user['display_name'])
            if len(request.form['dname']) == 0:
                return render_template('user_settings.html',
                        d_error = " - Can't be empty",
                        display_name = _user['display_name'])
            coll.update({"_id" : ObjectId(_user['_id'])},{
                "user_name" : _user['user_name'],
                "pwd" : _user['pwd'],
                "creation_date": _user['creation_date'],
                "display_name" : n_display_name})
            _user = coll.find_one({"user_name":session['user']})
            return render_template('user_settings.html',
                dn_updated = '- Display Name Changed',
                display_name = _user['display_name'])
    except:
        return redirect(url_for('user_settings'))


@app.route('/change_password', methods=['POST'])
def change_password():
    """ action behind button for changing password.
    Checks are performed for current password and whether the new
    password adheres to minimum requirements, displaying error 
    messages if something is wrong 
    """
    try:
        if session['user']:
            coll = mongo.db.users
            _user = coll.find_one({"user_name":session['user']})
            _current = request.form['cpwd']
            _new = request.form['npwd']
            _check = request.form['npwd_check']
            _hash = generate_password_hash(_new)
            _hash_check = check_password_hash(_user['pwd'], _current)
            if not _hash_check:
                return render_template('user_settings.html',
                            cp_error = ' - Password Incorrect',
                            display_name = _user['display_name'])
            if _new != _check:
                return render_template('user_settings.html',
                            np_error = ' - Passwords do not match',
                            display_name = _user['display_name'])
            if _current == _new:
                return render_template('user_settings.html',
                            cp_error = ' - Passwords Identical',
                            np_error = ' - Passwords Identical',
                            display_name = _user['display_name'])
            if len(_new) < 8:
                return render_template('user_settings.html',
                            np_error = ' - Password too short',
                            display_name = _user['display_name'])
            if len(_new) > 16:
                return render_template('user_settings.html',
                            np_error = ' - Password too long',
                            display_name = _user['display_name'])
            if _hash_check:
                _npwd = generate_password_hash(_new)
                coll.update({"_id" : ObjectId(_user['_id'])}, {
                        "user_name" : _user['user_name'],
                        "pwd" : _npwd,
                        "display_name" : _user['display_name'],
                        "creation_date" : _user['creation_date']})
                return render_template('user_settings.html',
                            pw_updated = '- Password Changed')
        
    except:
        return redirect(url_for('user_settings'))


@app.route('/read_comics')
def read_comics():
    """ page with user's comics marked 'read' """
    try:
        if session['user']:
            user = mongo.db.users.find_one({"user_name":session['user']})
            _nice = user['display_name']
            coll = mongo.db.user_comic_list
            _user_read = coll.find({ "user_name" : session['user'],
                                    "comic_status" : { "$eq" : "read" } })
            _count = _user_read.count()
            return render_template('read_comics.html',
                                    user_read=_user_read,
                                    comics_total=_count,
                                    display_name=_nice)
    except:
        return render_template('401.html')

        
@app.route('/mark_comic_read', methods=['POST'])
def mark_comic_read():
    """ action behind checkmark on unread comics """
    try:
        if 'user' in session:
            posted = request.json
            coll = mongo.db.user_comic_list
            _mark = coll.find_one({"_id":ObjectId(posted['_id'])})
            coll.update({"_id": ObjectId(posted['_id'])}, {
                "comic_series_id": _mark['comic_series_id'],
                "comic_id": _mark['comic_id'],
                "comic_status": "read",
                "on_sale_date": _mark['on_sale_date'],
                "comic_title": _mark['comic_title'],
                "user_name": session['user'],
                "comic_image": _mark['comic_image'],
                "comic_image_fs" : _mark['comic_image_fs'],
                "date_read": config.date_today })
            return jsonify({ 'result' : 'success' })
        else:
            return render_template('index.html')
    except:
        return render_template('index.html')


@app.route('/delete_comic', methods=['POST'])
def delete_comic():
    """ remove the comic entirely from the user's list """
    try:
        if 'user' in session:
            posted = request.json
            coll = mongo.db.user_comic_list
            coll.remove({'_id': ObjectId(posted['_id'])})
            return jsonify({ 'result' : 'success' })
        else:
            return render_template('index.html')
    except:
        return render_template('index.html')

    
@app.route('/add_comics')
def add_comics():
    """ default landing page for adding comics,
    defaults to the list of new comics 
    """
    try:
        if session['user']:
            user = mongo.db.users.find_one({"user_name":session['user']})
            _nice = user['display_name']
            coll_1 = mongo.db.comics
            coll_2 = mongo.db.user_comic_list
            _new_comics=coll_1.find({ "$query": { "on_sale_date" : 
                        { "$gte" : config.date_week_ago }}, 
                            "$orderby": { "comic_title" : 1 }})
            _user_list=coll_2.find({ "user_name" : session['user'] })
            _check = [i['comic_id'] for i in _user_list]
            _now = datetime.now().strftime("%b-%d")
            _then = (datetime.now() \
                - timedelta(days=7)).strftime("%b-%d")
            return render_template('add_comics.html',
                        new_comics=_new_comics, check_list=_check, 
                        today=_now, week_ago=_then, display_name=_nice)
        else:
            return render_template('index.html')
    except:
        return render_template('401.html')


@app.route('/add_comics_all')
def add_comics_all():
    """ similar to add_comics, but now
    showing the entire list of comics available 
    """
    try:
        if session['user']:
            user = mongo.db.users.find_one({"user_name":session['user']})
            _nice = user['display_name']
            coll_1 = mongo.db.comics
            coll_2 = mongo.db.user_comic_list
            _all_comics=coll_1.find({ "$query": {}, 
                                      "$orderby": { "comic_title" : 1 }})
            _user_list=coll_2.find({ "user_name" : session['user'] })
            _check = [i['comic_id'] for i in _user_list]
            return render_template('add_comics_all.html',
                        all_comics=_all_comics, 
                        check_list=_check, display_name=_nice)
        else:
            return render_template('index.html')
    except:
        return render_template('401.html')


@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    """ action taken when checkbox is clicked,
    adding the comic to the list of unread comics
    """
    try:
        if 'user' in session:
            print(request)
            print(request.json)
            posted = request.json
            coll_1 = mongo.db.comics
            coll_2 = mongo.db.user_comic_list
            _add = coll_1.find_one({ "_id" : ObjectId(posted['_id']) })
            _new = { "user_name" : session['user'],
                     "comic_title" : _add['comic_title'],
                     "comic_id" : _add['comic_id'],
                     "comic_series_id" : _add['comic_series_id'],
                     "comic_image" : _add['comic_image'],
                     "comic_image_fs" : _add['comic_image_fs'],
                     "on_sale_date" : _add['on_sale_date'],
                     "comic_status" : "unread"}
            coll_2.insert_one(_new)
            return jsonify({ 'result' : 'success' })
        else:
            return render_template('index.html')
    except:
        return render_template('index.html')


@app.route('/sign_up')
def sign_up():
    """ the registration page """
    try:
        if 'user' in session:
            return redirect(url_for('index'))
        else:
            return render_template('sign_up.html')
    except:
        return redirect(url_for('index'))
    

@app.route('/sign_up_submit', methods=['POST'])
def sign_up_submit():
    """ action taken when user subits registration form """
    try:
        users = mongo.db.users
        display_name = request.form['uname']
        uname = request.form['uname'].lower()
        pwd = request.form['pwd']
        pwd_check = request.form["pwd_check"]
        
        if uname == '':
            return render_template('sign_up.html',
                    u_error = ' - Only Drax is invisible, if he stands still')
        
        x=0
        y=0
        while x < len(uname):
            # create counter for letter in the name
            if uname[x] in config.letters:
                y += 1
            # check if character is outside of allowed characters
            if uname[x] not in config.valids:
                return render_template('sign_up.html',
                    u_error = ' - Use allowed characters only')
            x += 1
        
        # Less than three letters in the chosen username
        if y < 3:
            return render_template('sign_up.html',
                    u_error = ' - Not enough letters')
        
        # username total length is less than 5 characters
        if  len(uname) < 5:
            return render_template('sign_up.html',
                    u_error = ' - Minimum 5 characters')
        
        # username is more than 32 characters                            
        if  len(uname) > 32:
            return render_template('sign_up.html',
                    u_error = ' - Who needs more than 32 characters? O_o')
        
        # username already exists
        if users.find_one({ "user_name" : uname}):
            return render_template('sign_up.html', 
                    u_error = ' - This name is taken, try again')
        
        # empty password fields                            
        if len(pwd) == 0:
            return render_template('sign_up.html',
                    p_error = ' - Empty is at least 8 characters short',
                    u_error = '')
        
        # password length too short
        if len(pwd) < 8:
            return render_template('sign_up.html',
                    p_error = ' - That\'s not enough characters',
                    u_error = '',
                    if_pw_error = request.form['uname'])
                                    
        # pssword length too long
        if len(pwd) > 16:
            return render_template('sign_up.html',
                    p_error = ' - That\'s too long, try again',
                    u_error = '',
                    if_pw_error = request.form['uname'])
        
        # mismatching passwords in form
        if pwd != pwd_check:
            return render_template('sign_up.html', 
                    p_error = ' -  Passwords did not match, try again', 
                    u_error = '',
                    if_pw_error = uname)
                    
        # All checks passed, add user to database and hash the password
        pwd_hash = generate_password_hash(pwd)
        session['user'] = uname
        creation_date = datetime.now().strftime("%Y%m%d")
        new_user = { "user_name" : uname, 
                     "display_name" : display_name,
                     "pwd" : pwd_hash, 
                     "creation_date" : creation_date }
        users.insert_one(new_user)
        # Add user to admin table as well with less information
        config.admin_coll.insert_one({ "user_name" : uname, 
                                   "display_name" : display_name })
        return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))
    

@app.route('/sign_in')
def sign_in():
    """ user sign in page """
    try:
        if 'user' in session:
            return redirect(url_for('index'))
        else:
            return render_template('sign_in.html')
    except:
        return redirect(url_for('index'))
    

@app.route('/sign_in_submit', methods=['POST'])
def sign_in_submit():
    """ action taken when user submits login form """
    try:
        users=mongo.db.users
        uname = request.form['uname'].lower()
        user = users.find_one({"user_name" : uname})
        # user doesn't exist, return generic 'try again' message
        if not user:
            return render_template('sign_in.html', 
                    u_error = ' - Incorrect username or password, try again',
                    p_error = ' - Incorrect username or password, try again')
        # user exists, return generic 'try again' on password failure
        if user:
            pwd = request.form['pwd']
            pwd_hash_check = check_password_hash(user['pwd'], pwd)
            if  pwd_hash_check:
                session['user'] = uname
                if session['user'] == config.admin_name:
                    return redirect(url_for('admin'))
                return redirect(url_for('index'))
            else:
                return render_template('sign_in.html', 
                    u_error = ' - Incorrect username or password, try again',
                    p_error = ' - Incorrect username or password, try again')
    except:
        return redirect(url_for('index'))


@app.route('/log_out')
def log_out():
    """ Speaks for itself, action taken when user 
    clicks the logout (red cross) button 
    """
    session.clear()
    return redirect(url_for('index'))
    

@app.errorhandler(404)
def page_not_found(e):
    """ custom 404 page """
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized_401(e):
    """ custom page to show whenever link manipulation
    is performed to pages that require a logged in user
    """
    return render_template('401.html'), 401


@app.errorhandler(405)
def methord_not_allowed(e):
    """ custom page to catch link manipulation
    towards pages that are POST only 
    """
    return render_template('405.html'), 405


@app.route('/admin')
def admin():
    """ admin page allowing removal of users
    to avoid the need to go to mLabs and remove there.
    Provides an overview of the number of comics in 
    user's lists as well, which is generated and updated to 
    the database on page load
    """
    try:
        if session['user'] == config.admin_name:
            user_all = mongo.db.users.find()
            usernames = [i["user_name"] for i in user_all]
            comicslist = mongo.db.user_comic_list
            for x in usernames:
                if x != config.admin_name:
                    adm_user = config.admin_coll.find_one({"user_name":x})
                    user = mongo.db.users.find_one({"user_name":x})
                    comic_u = comicslist.count({"user_name":x,
                                            "comic_status":"unread"})
                    comic_r = comicslist.count({"user_name":x,
                                            "comic_status":"read"})
                    config.admin_coll.update({"_id":ObjectId(adm_user['_id'])}, {
                        "user_name":x,
                        "display_name":user['display_name'],
                        "comics_unread":comic_u,
                        "comics_read":comic_r})
            user_list_all = config.admin_coll.find({"$query":{}, 
                                            "$orderby" : { "user_name": 1}})
            return render_template('admin/admin_home.html',
                                    user_list=user_list_all,
                                    display_name = config.admin_display_name)
        else:
            return redirect(url_for('index'))
    except:
        return render_template('401.html')


@app.route('/adm_del_user', methods=["POST"])
def adm_del_user():
    """ actions taken upon deletion of a user.
    User is deleted from all relevant tables
    """
    try:
        if session['user'] == config.admin_name:
            posted = request.json
            coll_1 = mongo.db.users
            coll_2 = mongo.db.user_comic_list
            coll_1.delete_one({'user_name': posted['user_name']})
            coll_2.delete_many({'user_name': posted['user_name']})
            config.admin_coll.delete_one({'user_name': posted['user_name']})
            user_list = config.admin_coll.find({"$query":{}, 
                                            "$orderby" : { "user_name": 1}})
            return render_template('admin/admin_home.html',
                                    user_list=user_list,
                                    display_name = config.admin_display_name)
        else:    
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = config.secret_key
    app.run(host=os.getenv('IP'), 
            port=int(os.getenv('PORT')),
            )