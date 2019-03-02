import config
import app as mrl
from flask import session
import unittest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = config.app

app.secret_key="whatever"

app.config["MONGO_URI"] = config.app.config["MONGO_URI"]

mongo = config.mongo

users = mongo.db.users

class TestReadingList(unittest.TestCase):
    def setUp(self):
        """ Ensure testing mode is on """
        mrl.app.testing = True
        self.app = mrl.app.test_client()
    
    """ helpers for POST tests """
    def logout(self):
        return self.app.get(
            '/log_out',
            follow_redirects=True
        )
        
    def signin(self, uname, pwd):
        form=dict(uname=uname, pwd=pwd)
        return self.app.post(
            '/sign_in_submit',
            data=form,
            follow_redirects=True
        )
    
    def signup(self, uname, pwd, pwd_check):
        return self.app.post(
            '/sign_up_submit',
            data=dict(uname=uname, pwd=pwd, pwd_check=pwd_check),
            follow_redirects=True
        )
    
    def addtolist(self,_id):
        return self.app.post(
            '/add_to_list',
            data=dict(_id=_id),
            follow_redirects=True
        )
    
    """ database tests outside app functions """
    def test_new_user(self):
        """ Users can be created in the database """
        display_name = "Dora the Explorer"
        uname = "dora123"
        pwd = "IloveDiego"
        pwd_hash = generate_password_hash(pwd)
        creation_date = datetime.now().strftime("%Y%m%d")
        new_user = { "user_name" : uname, 
                     "display_name" : display_name,
                     "pwd" : pwd_hash, 
                     "creation_date" : creation_date }
        users.insert_one(new_user)
        config.admin_coll.insert_one({ "user_name" : uname, 
                                   "display_name" : display_name })

        self.assertTrue(users.find_one(
            {"user_name":"dora123"}))
        self.assertTrue(config.admin_coll.find_one(
            {"display_name":"Dora the Explorer"}))
        users.delete_many({"user_name":"dora123"})
        config.admin_coll.delete_many({"user_name":"dora123"})
    
    def test_add_comic_to_user_unread_list(self):
        """ Add a comic to the user_comics table 
        """
        coll_1 = mongo.db.comics
        coll_2 = mongo.db.user_comic_list
        
        # Add the comic in the collection
        _add = coll_1.find_one(
            { "_id" : ObjectId("5c77de72cac98e202c6562b5")})
        _new = { "user_name" : "tester1",
                 "comic_title" : _add['comic_title'],
                 "comic_id" : _add['comic_id'],
                 "comic_series_id" : _add['comic_series_id'],
                 "comic_image" : _add['comic_image'],
                 "comic_image_fs" : _add['comic_image_fs'],
                 "on_sale_date" : _add['on_sale_date'],
                 "comic_status" : "unread"}
        coll_2.insert_one(_new)
        self.assertTrue(coll_2.find(
            {"user_name":"tester1"}))
        entry = coll_2.find_one(
            {"comic_id":72949})
        self.assertEqual(entry['comic_id'],72949)
        self.assertEqual(entry['comic_status'],'unread')
        self.assertEqual(entry['comic_title'],
                    'Age of X-Man: X-Tremists (2019) #1')
        
        """ Remove the comic from the list
        """
        coll_2.delete_many(
            {"comic_id": 72949})
        self.assertFalse(coll_2.find_one(
            {"comic_title":"Age of X-Man: X-Tremists (2019) #1"}))
    
     
    def test_all_pages_rendered_normally(self):
        """ Tests to check app page routes 
        """   
        root = self.app.get('/')
        self.assertEqual(root.status_code, 200)
        home = self.app.get('/home')
        self.assertEqual(home.status_code, 200)
        user_home = self.app.get('/user_home')
        self.assertEqual(user_home.status_code, 200)
        user_settings = self.app.get('/user_settings')
        self.assertEqual(user_settings.status_code, 200)
        read_comics = self.app.get('/read_comics')
        self.assertEqual(read_comics.status_code, 200)
        add_comics = self.app.get('add_comics')
        self.assertEqual(add_comics.status_code, 200)
        add_comics_all = self.app.get('add_comics_all')
        self.assertEqual(add_comics_all.status_code, 200)
        sign_up = self.app.get('sign_up')
        self.assertEqual(sign_up.status_code, 200)
        sign_in = self.app.get('sign_in')
        self.assertEqual(sign_in.status_code, 200)
        admin = self.app.get('admin')
        self.assertEqual(admin.status_code, 200)
        
    def test_invalid_link_entered(self):
        """ Non-existent link entered 
        """
        error = self.app.get('i_dont_exist')
        self.assertEqual(error.status_code, 404)
    
    def test_direct_address_post_link(self):
        """ Attempt POST through address link failure
        """
        not_allowed = self.app.get('sign_in_submit')
        self.assertEqual(not_allowed.status_code, 405)
        
    def test_valid_user_signup(self):
        """ Signup: Username is free, passwords match
        """
        response = self.signup('pennywise', 'weallfloat', 'weallfloat')
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_user_signup_username(self):
        """ Signup: Username is taken
        """
        response = self.signup('walterwhite', 'heisenberg','heisenberg')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This name is taken, try again', response.data)
        
    def test_invalid_user_signup_passwords(self):
        """ Signup: Passwords do not match
        """
        response = self.signup('peterparker','ilovemaryjane','MJrocks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords did not match, try again', response.data)
        
    def test_empty_username_signup(self):
        """ Signup: Try to register without a username
        """
        response = self.signup('','metaphor','metaphor')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Only Drax is invisible', response.data)
        
    def test_invalid_character_in_username(self):
        """ Signup: Username contains invalid character(s)
        """
        response = self.signup('God of Thunder','pointbreak','pointbreak')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Use allowed characters only', response.data)
        
    def test_too_few_letters_in_username(self):
        """ Signup: Username has less than three letters
        """
        response = self.signup('IM1234','pepperftw','pepperftw')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Not enough letters', response.data)
        
    def test_username_too_short(self):
        """ Signup: Username has less than five characters
        """
        response = self.signup('Thor','mjolnir12','mjolnir12')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Minimum 5 characters', response.data)
        
    def test_username_too_long(self):
        """ Signup: Username has more than 32 characters
        """
        response = self.signup('abcd1234abcd1234abcd1234abcd12345'
                                        ,'thisisnuts','thisisnuts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'32 characters? O_o', response.data)
        
    def test_no_password_entered(self):
        """ Signup: Password field empty
        """
        response = self.signup('Banner','','')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Empty is at least 8 characters short', response.data)
        
    def test_password_too_short(self):
        """ Signup: Password less than eight characters
        """
        response = self.signup('Banner','smash!','smash!')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'not enough characters', response.data)
        
    def test_password_too_long(self):
        """ Signup: Password more than sixteen characters
        """
        response = self.signup('Thanos',
                                'Allthingsbalanced','Allthingsbalanced')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'too long, try again', response.data)
        
    def test_signin_incorrect1(self):
        """ Signin: Incorrect signin - user does not exist
        """
        response = self.signin('Thanos','Allthingsbalanced')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect username or password', response.data)
        
    def test_signin_incorrect2(self):
        """ Signin: Incorrect signin - password wrong
        """
        response = self.signin('cyclops','wolverinebad')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect username or password', response.data)
        
    def test_signin_correct(self):
        """ Signin: Correct signin
        """
        response = self.signin('cyclops','1234qwer')
        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):
        """ Logout: Successful
        """
        response = self.logout()
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_list(self):
        """ Add to list: Success
        """
        response = self.addtolist('5c77de72cac98e202c6562b5')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()