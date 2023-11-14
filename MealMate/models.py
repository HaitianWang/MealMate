from datetime import datetime
from MealMate import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from MealMate import login
from hashlib import md5
from time import time
import jwt
from MealMate import app
from pytz import timezone
import random


# set open hours of restaurants
business_hours = {
    "Monday": "09:00 AM - 05:00 PM",
    "Tuesday": "11:00 AM - 23:00 PM",
    "Wednesday": "09:00 AM - 05:00 PM",
    "Thursday": "09:00 AM - 05:00 PM",
    "Friday": "09:00 AM - 05:00 PM",
    "Saturday": "10:00 AM - 02:00 PM",
    "Sunday": "12:00 AM - 08:00 PM"
}


# User data table
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.String(400), default= datetime.now(timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"))
    status_index = db.Column(db.Integer, default=0)  # index of the status of NLP
    session_id = db.Column(db.Integer, default=0) # recorded chatting sessions
    is_talking = db.Column(db.Boolean, default=False) # record if user had conversation
    first_NLP = db.Column(db.String(400), default=None) # first level of conversation
    first_Random_Nearest_restaurant_id = db.Column(db.Integer, default=None)
    second_NLP_restaurant = db.Column(db.Integer, default=None) # second level of conversation for resturant id
    second_NLP_dish = db.Column(db.String(40), default=None) # second level of conversation for dish choice
    third_NLP_restaurant = db.Column(db.Integer, default=None) # third level of conversation for restaurant id
    third_NLP_dish = db.Column(db.String(40), default=None) # third level of conversation for dish choice

#    relationship between user and history 
    histories = db.relationship('History', backref='user', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    # User avatar URLs are generated with the help of the Gravatar service
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(70, 70)


    # reset password
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# history data table
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32))  # session id
    timestamp = db.Column(db.String(400), default= datetime.now(timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"))  # timestamp
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # usr id

   # relationship between history and users
    conversations = db.relationship('Conversation', backref='history', lazy='dynamic', foreign_keys='Conversation.session_id')

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), db.ForeignKey('history.session_id'))  # link chatting id with history session id
    message = db.Column(db.JSON)  # chatting content
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # link user id with multiple chatting history sessions


# restaurant data table
class Restaurant(db.Model): 
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(60), unique=True)  # name of restaurant
    location = db.Column(db.String(400))  # address of restaurant
    type = db.Column(db.String(20))  # type of restaurant
    phone = db.Column(db.String(40)) # phone number of restaurant

    dishes = db.relationship('Dish', backref='restaurant', lazy=True)  # restaurant link to dishes

    @staticmethod   
    def opening_hours():
        times = list(business_hours.values())
        random_time = random.choice(times)
        return random_time


# dish data table
class Dish(db.Model):
  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))  # name of dish
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))  # link to restaurant
    price = db.Column(db.Integer)   # price of dish
    rate = db.Column(db.Integer)    # rate of dish (score 1 to 10)


@login.user_loader
def load_user(id):
     return User.query.get(int(id))
















