import os
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest

from flask import url_for
from MealMate import app, db
from MealMate.models import User, Restaurant, History, Conversation
from faker import Faker
from random import random, randint


class MealMateTestCase(unittest.TestCase):

    # set up test environment
    def setUp(self):

        # set up test environment for flask
        self.app_context = app.app_context()
        app.config.update(
            TESTING = True,
            SERVER_NAME = 'localhost:5000',
            PREFERRED_URL_SCHEME = 'http',
            APPLICATION_ROOT = '/',
        )

        # push the test script into current running thread
        self.app_context.push()

        # create test database
        db.create_all()

        # input test data into User table
        user = User(username='wanghaitian1', email='simon__qiu@126.com')
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

        # input test data into Restaurant table
        address = [
            '33 Kanimbla Rd, Nedlands WA 6009',
            '35 Stirling Hwy, Crawley WA 6009',
            '3/129 Derby Rd, Shenton Park WA 6008',
            '1 Graylands Rd, Claremont WA 6010',
            '131 Stirling Hwy, Nedlands WA 6009',
            '122 Dalkeith Rd, Nedlands WA 6009',
            '622 Hay St, Jolimont WA 6014',
            '81 Royal St, East Perth WA 6004',
            '150 Bennett St, East Perth WA 6004',
            '4/10 Eastbrook Terrace, Perth WA 6004'
        ]

        faker = Faker()

        R = []
        restaurant_type = ['Chinese', 'Japanese', 'Korean']

        for i, _ in enumerate(range(10)):
            R.append({'name': faker.company(), 'location': address[i], 'type': restaurant_type[randint(0,len(restaurant_type)-1)]})
            
        for i in R:
            restaurant = Restaurant(name=i['name'], location=i['location'], type=i['type'])
            db.session.add(restaurant)

        db.session.commit()

        # create test client
        self.client = app.test_client()  

        # create a test command runner
        self.runner = app.test_cli_runner()  



    # tear down test environment
    def tearDown(self):

        #stop database session
        db.session.remove()

        #delete test database
        db.drop_all()

        # pop test script from current running thread
        self.app_context.pop()
   


    # test for 404 page
    def test_404_page(self):
        response = self.client.get('/nothing')  # 传入错误URL
        data = response.get_data(as_text=True)
        self.assertIn('File Not Found', data)
        self.assertIn('Back', data)
        self.assertEqual(response.status_code, 404)  # 判断响应状态码

    # test for the chatting page
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('I am your Meal Mate Max', data)
        # self.assertIn('Meet your Meal Mate Max!', data)
        self.assertEqual(response.status_code, 200)

    # test for the login page
    def test_login_success(self):
        response = self.client.post(
            url_for('login'),
            data={'username': 'wanghaitian2', 'password': '1234'},
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to MealMate', data)
        

    # test for the register page
    def test_login_invalid_credentials(self):
        response = self.client.post(
            url_for('login'),
            data={'username': 'wanghaitian', 'password': '1234'},
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Click', data)
       

    # test for reset password page
    def test_reset_password_request(self):
        # create test user
        user = User(username='liangzhenyi', email='liangzhenyi@gmail.com')
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

        # send reset password request
        response = self.client.post(url_for('reset_password_request'), 
                                    data=dict(email='liangzhenyi@gmail.com'), 
                                    follow_redirects=True)
        
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Reset Password', data)

    # test for reset password script
    def test_reset_password(self):
        # create test user
        user = User(username='liangzhener', email='liangzhener@gmail.com')
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

        # generate reset password token
        token = user.get_reset_password_token()

        # vist reset password page
        response = self.client.get(url_for('reset_password', token=token))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Reset Your Password', data)

    

    # login user
    def login(self, username, password):
        return self.client.post(
            url_for('login'),
            data={
                'username': username,
                'password': password
            },
            follow_redirects=True
        )


    # logout user
    def test_logout(self):
        # user login
        self.login(username='liangzhener', password='1234')

        # send logout request
        response = self.client.get(url_for('logout'), follow_redirects=True)

        data = response.get_data(as_text=True)

        # check response status code and redirect to index page
        self.assertEqual(response.status_code, 200)
        self.assertIn('Forgot Your Password', data)


    # test register
    def test_register(self):
    # send register request
        response = self.client.post(
            url_for('register'),
            data={
                'username': 'liangzhensan',
                'email': 'liangzhensan@example.com',
                'password': '1234',
                'password2': '1234'
            },
            follow_redirects=True
        )

        data = response.get_data(as_text=True)

        # check response status code and redirect to login page
        self.assertEqual(response.status_code, 200)
        self.assertIn('MealMate', data)

        # create test user
        user = User(username='liangzhensi', email='liangzhensi@gmail.com')
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

        # check user in database
        user = User.query.filter_by(username='liangzhensi').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'liangzhensi@gmail.com')


if __name__ == '__main__':
   
    unittest.main(verbosity=2)



















