from flask import render_template
from MealMate import app
from MealMate.forms import LoginForm
from flask import render_template, flash, redirect
from flask_login import current_user, login_user
from MealMate.models import User
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from MealMate import db
from MealMate.forms import RegistrationForm
from flask import url_for
from datetime import datetime
from MealMate.forms import EditProfileForm, chatWithMealMateForm
from MealMate.models import Restaurant, Conversation, History, Dish
from MealMate.forms import ResetPasswordRequestForm
from MealMate.forms import ResetPasswordForm
from pytz import timezone
import random 

import sendgrid
from sendgrid.helpers.mail import Mail
from MealMate.forms import ResetPasswordRequestForm, ResetPasswordForm

import googlemaps 
from geopy.distance import geodesic

import openai
from markdown_it import MarkdownIt


# initialize list for chatting history 
messages = []

# config google map API
GOOGLEMAPS_API_KEY = ''
app.config['GOOGLEMAPS_API_KEY'] = GOOGLEMAPS_API_KEY
gmaps = googlemaps.Client(key=app.config['GOOGLEMAPS_API_KEY'])

# config openAI API 
openai.api_key = ""

dish_list = ['Sweet and Sour Pork', 'Kung Pao Chicken', 'Mapo Tofu', 'Peking Duck', 'Dumplings', 
             'Hot Pot', 'Malatang', 'General Tso Chicken', 'Beijing Beef', 'Egg Foo Young', 
             'Sushi', 'Ramen', 'Tempura', 'Teriyaki Chicken', 'Miso Soup', 'Wrap', 'Yakitori', 
             'Udon Noodles', 'Tonkatsu', 'Sashimi', 'Bibimbap', 'Kimchi', 'Bulgogi', 'Japchae', 
             'Korean BBQ', 'Tteokbokki', 'Samgyeopsal', 'Galbi', 'Bibim Naengmyeon', 'Jjajangmyeon']

# config SendGrid API
YOUR_SENDGRID_ID = ''
sg = sendgrid.SendGridAPIClient(api_key= YOUR_SENDGRID_ID)


def contains_item_from_list(string, items_list):
    for item in items_list:
        if item in string:
            return True
    return False

@app.route('/')
@app.route('/intro')
def intro():
   return render_template('intro.html')


@app.route('/readme')
def readme():
    md = MarkdownIt()
    with open('README.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    html_content = md.render(markdown_content)
    return render_template('readme.html', content=html_content)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        # check if session id is none
        if user.session_id is None:
            user.session_id = 0  
            db.session.commit()

        # check if status_index is none
        if user.status_index is None:
            user.status_index = 0 
            db.session.commit()

        # check if is_talking is none
        if user.is_talking is None:
            user.is_talking = False 
            db.session.commit()

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():

    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():

        email=form.email.data
        user = User.query.filter_by(email=email).first()
        
        if user:

            token = user.get_reset_password_token()
            html_content = f'''
                <p>Dear { user.username },</p>
                <p>
                    To reset your password
                    <a href="{ url_for('reset_password', token=token, _external=True) }">
                        click here
                    </a>.
                </p>
                <p>Alternatively, you can paste the following link in your browser's address bar:</p>
                <p>{ url_for('reset_password', token=token, _external=True) }</p>
                <p>If you have not requested a password reset simply ignore this message.</p>
                <p>Sincerely,</p>
                <p>The Microblog Team</p>
            '''

            message = Mail(
            from_email='simonqiu4@gmail.com',
            to_emails= email,
            subject='MealMate Password Reset Request',
            html_content= html_content
            )
            
            response = sg.send(message)
            print('Email sent process end.')

            flash(str(response.status_code))
                # check if email is sent successfully
            if response.status_code == 202:
                print('Email sent successfully.')

            else:
                print('Failed to send email. Status code:', response.status_code)
                flash('Check your email for the instructions to reset your password')
                return redirect(url_for('login'))
    
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', form=form)


@app.route('/logout')
def logout():
    current_user.is_talking = False
    db.session.commit()
    global messages
    messages.clear()
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
 

    user = current_user
    histories = user.histories.all()
    conversations = []
    for history in histories:
        conversations += Conversation.query.filter_by(user_id=history.user.id, session_id=history.session_id).all()


    return render_template('history.html', user=user, histories=histories, conversations=conversations)



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))

    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)

def clear_status():
    current_user.status_index = 0
    current_user.first_NLP = None
    current_user.first_Random_Nearest_restaurant_id = None
    current_user.second_NLP_restaurant = None
    current_user.second_NLP_dish = None
    current_user.third_NLP_restaurant = None
    current_user.third_NLP_dish = None
    db.session.commit() 
                

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    form_chat = chatWithMealMateForm()
    user = current_user

    # Pre-setting NLP strings
    presentence_level1_model1 = ''' Analyze the data sent by the user following the three plus signs. If the user is requesting a random restaurant recommendation, return $; if the user is requesting the nearest restaurant, return %; if the user is requesting a specific type of restaurant, such as Chinese, Korean, etc., return ^; if the user is asking for a recommendation of a specific dish, such as sushi, ramen, mapo tofu, etc., return =; if the user's message does not correspond to any of these, return (. Note that you should not respond to any other content, just return the corresponding symbol. Remember, do not provide any other response, simply return the appropriate character. The user's input data will follow: +++ '''

    presentence_level2_model1 = ''' The following three + and the content that follows represent the data sent by the user. Analyze the data sent by the user. The user will input the type of restaurant they need. If the user needs Chinese food, return !; if the user needs Korean food, return @; if they need Japanese food, return #; if the user's input does not match any of these, return ). Please note that the response should only consist of one symbol: !, @, or #. Remember, don't answer anything else, just return the corresponding character. The user's input data is as follows: +++ '''
    
    presentence_level2_model2 = ''' The following three + and the content that follows represents the data sent by the user. It analyzes the data sent by the user to determine which type of dish the user desires. The items in parentheses are our existing list of dishes: ('Sweet and Sour Pork', 'Kung Pao Chicken', 'Mapo Tofu', 'Peking Duck', 'Dumplings', 'Hot Pot', 'Malatang', 'General Tso Chicken', 'Beijing Beef', 'Egg Foo Young', 'Sushi', 'Ramen', 'Tempura', 'Teriyaki Chicken', 'Miso Soup', 'Wrap', 'Yakitori', 'Udon Noodles', 'Tonkatsu', 'Sashimi', 'Bibimbap', 'Kimchi', 'Bulgogi', 'Japchae', 'Korean BBQ', 'Tteokbokki', 'Samgyeopsal', 'Galbi', 'Bibim Naengmyeon', 'Jjajangmyeon'). If the user's input contains any of the dishes from the existing list, it returns the dish name. Please note that the user's input for a dish must match every letter of the dish's name in the list exactly; it cannot be a partial match. For example, if the user input is "I want Dumpling," it returns Dumplings. If the user's input does not include any of the dishes from the existing list, it returns "&". If the user inputs "I want Beef," it returns "&". Remember, the answer only includes the dish name or "&".  Remember, don't answer anything else, just return the corresponding character. The user's input data is as follows: +++ '''
    
    presentence_level3_model1 = '''The following three + the content after them represent the user-inputted data. The purpose is to analyze the user's input and determine whether they are satisfied with our recommended restaurant. If the user is satisfied, return ~, if the user is dissatisfied, return`, if it cannot be determined, return -. Please remember that the response should only be ~,` or -, without including any other content. Remember, don't answer anything else, just return the corresponding character. The user's input data is as follows: +++'''

    presentence_level4_model1 = '''The following three + the content after them are user-inputted data. We analyze the user-inputted data to determine if the user is satisfied with the restaurant we ultimately recommend. If the user is satisfied, return (<). If the user is not satisfied, return (|). If it cannot be determined, return (?). Remember, the response should only include <, |, or ?, without any other content. Remember, don't answer anything else, just return the corresponding character. The user's input data is as follows: +++'''

    presentence_level2_model3_model4 = ''' Upon receiving user input '+++XXX+++', analyze and determine whether they express satisfaction with our recommended restaurant. If their input indicates satisfaction, such as a response like 'Sounds good, any contact number?', return 'YYY'. If their input demonstrates dissatisfaction, return 'NNN'. If their sentiment is ambiguous or uncertain, return 'GGG'. Please note that the return response should only consist of one of these three-letter codes, with no additional text or characters. The user's input data is as follows: +++ '''

    # Strings returned to sent to user 
    afterresponse_invalidinput_level1_model1 = ''' Hi there, I'm Max! I'm here to offer you random restaurant suggestions, recommend restaurants based on types, help you find restaurants by location, and assist in discovering specific dishes that you might enjoy. How can I assist you today? '''
    
    afterresponse_invalidinput_level2_model1 = '''Sorry, could you please clarify what type of restaurant you would like to choose? We can only offer options for Chinese, Korean, and Japanese cuisine.'''
    
    afterresponse_invalidinput_level2_model2 = ''' Sorry, I have searched all databases for the dish you input but unfortunately it could not be found, could you input again'''

    afterresponse_invalidinput_level2_model3_model4 = ''' Sorry, Maybe you do not satisfy the restaurant we recommand'''
    
    afterresponse_invalidinput_level3_model1 = '''Sorry, we could not recognize if you satisfy or not to the restaurant we recommend which has the dish you want, please retry again.'''

    afterresponse_invalidinput_level4_model1 = '''Sorry, we do not know if you satisfy or not to the restaurant which has the lowest price of the dish you want, please retry again'''
    
    
    if form_chat.validate_on_submit() or current_user.status_index != 0 :

        if  current_user.status_index == 0 or current_user.status_index == 5 or current_user.status_index == 99 or current_user.status_index == 199:


            text_input = form_chat.chat.data
            form_chat.chat.data = None

            if text_input is None:
                clear_status()
                return render_template('chat.html', title='Home',form_chat=form_chat, messages=messages)

            messages.append({'type': current_user, 'text': text_input})


            if user.is_talking == False:
                user.session_id += 1  
                user.is_talking = True
                db.session.commit()            

            # check if user is still in the same session
            history = History.query.filter_by(user_id=current_user.id, session_id=user.session_id).first()

            if history is None:

                # if user is not in the same session, create one and connct to history data
                history = History(user_id=user.id, session_id=user.session_id)

                # add chatting session to history data
                db.session.add(history)
                db.session.commit()

            # adding conversations into history data
            conversation_people = Conversation(session_id=current_user.session_id, message={'type': current_user.username, 'text': text_input}, user_id=current_user.id)
            db.session.add(conversation_people)
            db.session.commit()

        elif current_user.status_index == 1 or current_user.status_index == 2:
            if user.first_NLP is None:
                clear_status()
                return render_template('chat.html', title='Home',form_chat=form_chat, messages=messages)
            text_input = user.first_NLP

        
        final_output = ""

        # combine user input with pre-setting strings
        if current_user.status_index == 0:
            final_input_text = presentence_level1_model1 + text_input
        elif current_user.status_index == 1:
            final_input_text = presentence_level2_model1 + text_input
        elif current_user.status_index == 2:
            final_input_text = presentence_level2_model2 + text_input
        elif current_user.status_index == 5:
            print('it is in no. 5')
            final_input_text = presentence_level2_model3_model4 + text_input
        elif current_user.status_index == 99:
            final_input_text = presentence_level3_model1 + text_input
        elif current_user.status_index == 199:
            final_input_text = presentence_level4_model1 + text_input
        else:
            return render_template('chat.html', title='Home',form_chat=form_chat, messages=messages)

        print(f"now it is {current_user.status_index}")
        print(f'text_input is {text_input}')
       
        # OpenAI language analysis
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=final_input_text,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.2, # randomness rate (larger numbers with larger randomness)
        )
    
        
        # Response from OpenAI
        ai_response = response.choices[0].text.strip()

        print(f"AI response is {ai_response}")

        # Processing language returned from OpenAI
        if '(' in ai_response:
            final_output = afterresponse_invalidinput_level1_model1
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 0
            user.first_NLP = None
            clear_status()
            db.session.commit()

        elif '$' in ai_response:
            # sugguest a random restaurant from database
            all_restaurants = Restaurant.query.all() 
            randon_restaurants_id = random.randint(1, len(all_restaurants)) 
            randon_restaurants = all_restaurants[randon_restaurants_id - 1] 
            flash('recommend_restaurant successfully')

            print("finish random restaurant")
            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = randon_restaurants_id
           
            print(f"now it is in random module and current_user.status_index is {current_user.status_index}")

            final_output = f"You should give {randon_restaurants.name} a try! It's a {randon_restaurants.type} restaurant located at {randon_restaurants.location}, and it's worth checking out."
            messages.append({'type': 'ai', 'text': final_output})

        elif 'YYY' in ai_response or 'GGG' in ai_response:
            final_recommand_restaurant = Restaurant.query.filter_by(id=current_user.first_Random_Nearest_restaurant_id).first()
            final_recommand_restaurant_location = final_recommand_restaurant.location
            final_recommand_restaurant_phone = final_recommand_restaurant.phone

            final_output = f" To make a reservation, please contact {final_recommand_restaurant_phone}. The opening hours of the restaurant is {final_recommand_restaurant.opening_hours()}. I wish you a delightful dining experience !"
            messages.append({'type': 'ai', 'text': final_output})
            clear_status()
            db.session.commit()

        elif 'NNN' in ai_response:
            final_output = afterresponse_invalidinput_level2_model3_model4
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 0
            clear_status()
            db.session.commit()

        elif '%' in ai_response:
            # suggest the closest restaurant
            restaurants = Restaurant.query.all()
            nearest_restaurant = None
            current_location = 'The University of Western Australia, 35 Stirling Hwy, Crawley WA 6009'

            nearest_distance = float('inf')

            i = 0

            for restaurant in restaurants:

                # compare current location with resturant location
                current_location_geocode = gmaps.geocode(current_location)[0]['geometry']['location']
                restaurant_location_geocode = gmaps.geocode(restaurant.location)[0]['geometry']['location']
                distance = geodesic((current_location_geocode['lat'], current_location_geocode['lng']), 
                                    (restaurant_location_geocode['lat'], restaurant_location_geocode['lng'])).km
                if distance < nearest_distance:
                    nearest_restaurant = restaurant
                    nearest_distance = distance

            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = nearest_restaurant.id

            flash('nearest_restaurant')          
            final_output = f"The closest restaurant is {nearest_restaurant.name}. It's a {nearest_restaurant.type} restaurant, it's located at {nearest_restaurant.location}."
            messages.append({'type': 'ai', 'text': final_output})
        
        elif '^' in ai_response:
            # hidden response for better conversation flow
            current_user.status_index = 1
            user.first_NLP = text_input
            db.session.commit()
            return redirect(url_for("index"))
        
        
        elif '!' in ai_response:
            
            chinese_restaurants = Restaurant.query.filter_by(type='Chinese').all()
            randon_chinese_restaurant_id = random.randint(1, len(chinese_restaurants)) 
            randon_chinese_restaurant = chinese_restaurants[randon_chinese_restaurant_id - 1] 
            flash('recommend randon chinese restaurant successfully')
            
            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = randon_chinese_restaurant_id
            
            final_output = f"You might want to consider trying out {randon_chinese_restaurant.name}. It's a {randon_chinese_restaurant.type} restaurant located at {randon_chinese_restaurant.location}."
            messages.append({'type': 'ai', 'text': final_output})
            
            user.first_NLP = None
            db.session.commit()

        elif '#' in ai_response:
             
            Japanese_restaurants = Restaurant.query.filter_by(type='Japanese').all()
            randon_Japanese_restaurant_id = random.randint(1, len(Japanese_restaurants)) 
            randon_Japanese_restaurant = Japanese_restaurants[randon_Japanese_restaurant_id - 1] 
            flash('recommend randon Japanese restaurant successfully')
         
            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = randon_Japanese_restaurant_id
            
            final_output = f"How about giving {randon_Japanese_restaurant.name} a try? It's a {randon_Japanese_restaurant.type} restaurant located at {randon_Japanese_restaurant.location}."
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 5

            user.first_NLP = None
            db.session.commit()
            

        elif '@' in ai_response:
            
            Korean_restaurants = Restaurant.query.filter_by(type='Korean').all()
            randon_Korean_restaurant_id = random.randint(1, len(Korean_restaurants)) 
            randon_Korean_restaurant = Korean_restaurants[randon_Korean_restaurant_id - 1] 
            flash('recommend randon Korean restaurant successfully')
           
            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = randon_Korean_restaurant_id
            
            final_output = f"I recommend checking out {randon_Korean_restaurant.name}, a {randon_Korean_restaurant.type} restaurant situated at {randon_Korean_restaurant.location}."
            messages.append({'type': 'ai', 'text': final_output})

            current_user.status_index = 5
            user.first_NLP = None
            db.session.commit()

        elif '=' in ai_response:
            current_user.status_index = 2
            user.first_NLP = text_input
            db.session.commit()
            print("&&&&&&&&&&enter level1 model1")
            return redirect(url_for("index"))

        elif contains_item_from_list(string=ai_response, items_list=dish_list):

            dish_name = next((dish for dish in dish_list if dish in ai_response), None)
            restaurants = Restaurant.query.join(Dish).filter(Dish.name == dish_name).all()

            best_restaurant = max(restaurants, key=lambda r: r.dishes[0].rate)
            restaurant_name = best_restaurant.name
            restaurant_location = best_restaurant.location
            restaurant_phone = best_restaurant.phone

            current_user.second_NLP_restaurant = best_restaurant.id
            current_user.second_NLP_dish = dish_name
            db.session.commit()

            dish = Dish.query.filter_by(restaurant_id=best_restaurant.id, name=dish_name).first()
            dish_price = dish.price
            dish_rate = dish.rate

            final_output = f"If you're in the mood for  {dish_name}, I highly recommend trying out {restaurant_name} and it is located in {restaurant_location}. It has a {dish_rate} rating and the price is around ${dish_price}. I hope you enjoy your dining experience there!"
            messages.append({'type': 'ai', 'text': final_output})

            current_user.status_index = 99
            user.first_NLP = None
            db.session.commit()
            print("recommand#########enter level2 model2")

        elif '~' in ai_response:
            final_recommand_restaurant = Restaurant.query.filter_by(id=current_user.second_NLP_restaurant).first()
            final_recommand_restaurant_location = final_recommand_restaurant.location
            final_recommand_restaurant_phone = final_recommand_restaurant.phone

           
            final_output = f"Please call {final_recommand_restaurant_phone} for reservation and its opening hours is {final_recommand_restaurant.opening_hours()}"
            messages.append({'type': 'ai', 'text': final_output})

            current_user.status_index = 0
            current_user.second_NLP_restaurant = None
            current_user.second_NLP_dish = None
            db.session.commit()
            print("satistify***********enter level3 model1")

        elif '`' in ai_response or '-' in ai_response:

            dish_name = current_user.second_NLP_dish  
            restaurants = Restaurant.query.join(Dish).filter(Dish.name == dish_name).all()
            cheapest_restaurant = min(restaurants, key=lambda r: r.dishes[0].price)

            restaurant_name = cheapest_restaurant.name
            restaurant_location = cheapest_restaurant.location
            restaurant_phone = cheapest_restaurant.phone

            dish = Dish.query.filter_by(restaurant_id=cheapest_restaurant.id, name=dish_name).first()
            dish_price = dish.price

            current_user.third_NLP_restaurant = cheapest_restaurant.id
            current_user.third_NLP_dish = dish_name

            final_output = f" Try {dish_name} at {restaurant_name} Restaurant and it is located in {restaurant_location}, the price is around ${dish_price} and pretty good for its value!"
            messages.append({'type': 'ai', 'text': final_output})

            current_user.status_index = 5
            current_user.first_Random_Nearest_restaurant_id = cheapest_restaurant.id
            current_user.second_NLP_restaurant = None
            current_user.second_NLP_dish = None
            
            db.session.commit()
            print("unsatistify***********enter level3 model1")

        elif '<' in ai_response:
            final_recommand_restaurant = Restaurant.query.filter_by(id=current_user.third_NLP_restaurant).first()
            final_recommand_restaurant_location = final_recommand_restaurant.location
            final_recommand_restaurant_phone = final_recommand_restaurant.phone

          

            final_output = f"It is located a{final_recommand_restaurant_location} and please call {final_recommand_restaurant_phone} for reservation."

            print("satistify***********enter level4 model1")
            current_user.status_index = 0
            current_user.third_NLP_dish = None
            current_user.third_NLP_dish = None
            db.session.commit()

        elif '|' in ai_response:
           
            final_output = f"Apologies, but we don't currently have a suitable restaurant recommendation for the dish you're looking for: {current_user.third_NLP_dish}. I apologize for any inconvenience caused."
            messages.append({'type': 'ai', 'text': final_output})

            print("unsatistify***********enter level4 model1")
            current_user.status_index = 0
            current_user.third_NLP_dish = None
            current_user.third_NLP_dish = None
            db.session.commit()



        elif '?' in ai_response:
            final_output = afterresponse_invalidinput_level4_model1
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 0
            clear_status()
            db.session.commit()

       

        elif '&' in ai_response:
            final_output = afterresponse_invalidinput_level2_model2
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 0
            user.first_NLP = None
            clear_status()
            db.session.commit()


        elif ")" in ai_response:
            final_output = afterresponse_invalidinput_level2_model1
            messages.append({'type': 'ai', 'text': final_output})
            current_user.status_index = 0
            user.first_NLP = None
            clear_status()
            db.session.commit()

        else:
            final_output = "Apologies for the confusion. Could you please provide more information or clarify your request? I'll do my best to assist you once again."
            messages.append({'type': 'ai', 'text': "Apologies for the confusion. Could you please provide more information or clarify your request? I'll do my best to assist you once again."})
            current_user.status_index = 0
            clear_status()
            db.session.commit()
            print(f"now it is {current_user.status_index}")
            print(f'text_input is {text_input}')

        conversation_ai = Conversation(session_id=current_user.session_id, message={'type': 'ai', 'text': final_output}, user_id=current_user.id)
        db.session.add(conversation_ai)
        db.session.commit()

        

        return render_template('chat.html', title='Home',form_chat=form_chat, messages=messages)
    
      
    return render_template('chat.html', title='Home',form_chat=form_chat, messages=messages)
    


















