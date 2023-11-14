import click
from MealMate import app, db
from MealMate.models import User,Restaurant, Dish
from faker import Faker 
import random


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

# name of the dish list
dish_names = {
    'Chinese': ['Peking duck'],
    'Japanese': ['Sushi'],
    'Korean': ['Bibimbap']
    }

    
# Script for initialization database and creating tables.
#  "flask initdb" creates all new tables 
#  "flask initdb -d" deletes all existing tables and recreate tables

@app.cli.command() 
@click.option('--drop', '-d',is_flag=True, help='Create after drop.') 
def initdb(drop):
    """Initialize the database."""
    if drop:  
        click.echo("drop all database")
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  


# initialize restaurant data
@app.cli.command()
def forger():

    # fake restaurant names
    faker = Faker('en_AU')

    R = []
    restaurant_type = ['Chinese', 'Japanese', 'Korean']

    for i, _ in enumerate(range(6)):
        R.append({'name': faker.company(), 
                  'location': address[i], 
                  'type': restaurant_type[random.randint(0,len(restaurant_type)-1)],
                  'phone': faker.phone_number()
                  })
        
    for i in R:
        restaurant = Restaurant(name=i['name'], 
                                location=i['location'], 
                                type=i['type'],
                                phone=i['phone'])
        
        db.session.add(restaurant)

    db.session.commit()
    click.echo('Done forge restaurants')


# initialize dish data
@app.cli.command()
def forged():

    faker = Faker('en_AU')

    all_restaurants = Restaurant.query.all()

    all_restaurants_id = [restaurant.id for restaurant in all_restaurants]

    for restaurant_id in all_restaurants_id:

        restaurant_type = Restaurant.query.get(restaurant_id).type
        dish_names_for_type = dish_names.get(restaurant_type, [])

    
        num_dishes = random.randint(1, 1)
        selected_dish_names = random.sample(dish_names_for_type, num_dishes)

        for dish_name in selected_dish_names:
            dish = Dish(
                name=dish_name,
                restaurant_id=restaurant_id,
                price=random.randint(20, 50),
                rate=random.randint(1, 10)
            )
            db.session.add(dish)

    db.session.commit()
    
    click.echo('Done forge dishes')



