# Project Name: Meal Mate

## Purpose of the web application

Introducing MealMate - the ultimate chatbot companion designed for busy young professionals and students. With countless dining options available today, choosing what to eat can be time-consuming and tiring. That's where MealMate comes in, aiming to simplify your life through simple conversations, understanding your preferences, and providing you with the restaurant and food information you need.

MealMate is your go-to solution for a smarter and more efficient dining experience. Using artificial intelligence, MealMate acts as your virtual assistant, giving personalized recommendations based on your unique tastes, dietary preferences, and budget. Whether you want a quick lunch during a busy workday or are up for a new culinary adventure, MealMate has got you covered.

With a vast database of restaurants, including hidden local gems, trendy cafes, and popular eateries, MealMate ensures there's something for everyone. By considering your location and preferences, MealMate provides details like menus, operating hours, customer reviews, and even delivery options for nearby restaurants.

Say goodbye to decision stress and let MealMate revolutionize your dining experience. With the power of AI, MealMate empowers you to make informed choices effortlessly, saving you time, energy, and unnecessary anxiety. Embrace smart living with MealMate, your personalized dining companion.

## The architecture of the web application
**Model View Controller**
<br>
<div align=center><img src="https://www.mathworks.com/company/newsletters/articles/developing-matlab-apps-using-the-model-view-controller-pattern/_jcr_content/mainParsys/image.adapt.full.medium.jpg/1668175030977.jpg"[1] width="420" height="280" alt="MVC"/>
</div>
<br>
MVC is widely attributed to Trygve Reenskaug, who reportedly invented it in the 1970s. Since then, it has gained immense popularity as a dominant pattern for server-side web applications[2].
<br>

**Model**

The model encompasses the app's data and logic, and it is paired with an entity in a database, such as the "User" entity in this app. Upon receiving a request from the controller, the model retrieves the necessary data and returns it to the controller..<br>

**Controller**

The controller acts as an intermediary between the models and views. It facilitates the transfer of data between the browser and the app, as well as vice versa. In this project, the "routes.py" file functions as the controller. When users wish to navigate to a new page, they send a request to the controller, which then renders the appropriate view.

**View**

The view is the component of the app through which users directly interact. It is linked to the model and displays the data stored within the model. The HTML files within the "template" folder serve as the views. Users can access information, read it, and interact with it[3].

## Getting Started

Install virtual envinronment: `python -m venv MealMate_venv` 

##### if you using linux/MacOs:
To open Visual Studio Code: `code .`

Activate the python virtual environment: `source venv/bin/activate`

Install required packages: `pip install -r requirements.txt`

Set FLASK_APP=project2.py: `export FLASK_APP=MealMate.py`

To run the app: `flask run`

To stop the app: `$deactivate`

##### if you using Windows:
Activate the python virtual environment: `./MealMate_venv/bin/activate`

Install required packages: `pip install -r requirements.txt`

Set FLASK_APP=project2.py: `export FLASK_APP=MealMate.py`

To run the app: `flask run`

To stop the app: `deactivate`


## Database
##### We have a database with 4 tables and 2 relationships:
##### tables:
- User: to store user information
- Restaurant: to store restaurant information
- History: to store chat history
- Conversation: to store chat contents
##### relationships:
- User --> History：One user may have multiple chat history entries
- History --> Conversation：One chat history entry may contain multiple conversations


##### To use the database, we need to configure the database

initialize the database and create all tables: `flask initdb -d`

Then we need to generate the restaurants data for restaurant table: `flask run`

## Source code
The source code is organised under the `5505PROJECT` directory which is the project root dictionary.

- **MealMate** directory: a file directory containing a Flask application.
  - **static** directory: contains CSS, JavaScript and images required for the user interface.
    - **CSS** directory: Contains the style.css file with the CSS styles for the user interface.
    - **images** directory: contains all images resources.
    - **JS** directory: contains JavaScript files for the Index, Historical, and Advanced pages. These scripts facilitate the functionality of the website (pressing buttons, etc) and updating the values on the screen in near real-time.
  - **template** directory: contains code for testing each sensor individually.
    - `base.html`: The base HTML template that serves as the foundation for all other templates. It defines the common structure and layout shared across multiple pages of the MealMate application.
    - `chat.html`: The main page of the MealMate application where users can interact with the chatbot, input their preferences, and receive restaurant recommendations.
    - `login.html`: The login page of the MealMate application where users can authenticate themselves to access personalized features and services.
    - `history.html`: The history page of the MealMate application where users can the previous conversations with Max.
  - `__init__.py`: The initialization file that sets up the MealMate application and defines its configuration.
  - `models.py`: Contains the database models and defines the structure of the database tables used in the MealMate application.
  - `forms.py`: Defines the forms used in the MealMate application, including user input forms and validation rules.
  - `routes.py`: Contains the route handlers for different URLs in the MealMate application, defining the logic and behavior of each page or endpoint.
  - `commands.py`: Defines custom Flask CLI commands that can be executed from the command line to perform various tasks related to the MealMate application, such as database migrations or data population.
- `MealMate.py`: The main entry point of the MealMate application, responsible for creating and running the Flask app.
- `config.py`: Contains the configuration settings for the MealMate application, such as database connection details, secret keys, and other environment-specific variables.
- `test.py`: Contains unit tests for the MealMate application, ensuring the correctness of its functionality.
- `app.db`: The SQLite database file used by the MealMate application to store data.


## Running the test
To ensure the correctness of the MealMate application, you can run the provided unit tests. The tests are written in a script named [tests.py](./tests.py), located in the root directory of the project.

To run the tests, follow these steps:

1. Make sure you have all the project dependencies installed. You can install them by running pip install -r requirements.txt.

2. Open a terminal or command prompt and navigate to the root directory of the project.

3. Execute the command to run the tests: `python tests.py`

This will execute the test script and display the results in the terminal.

Review the test results to ensure that all tests have passed successfully. Any failed tests will be indicated along with the relevant error messages.

It's recommended to run the tests whenever you make changes to the codebase to verify that everything is functioning as expected.


## Contributing

Please read [log.txt](./log.txt) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

Zhenyi Liang - 23461235@student.uwa.edu.au
Haitian Wang - 23815631@student.uwa.edu.au


## Deployment

Via localhost: `http://127.0.0.1:5000`

## Acknowledgments

* Built following the [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by **Miguel Grinberg**.


[1] https://www.mathworks.com/company/newsletters/articles/developing-matlab-apps-using-the-model-view-controller-pattern.html
[2] Reenskaug, T. (1979). Models-Views-Controllers. Retrieved from http://heim.ifi.uio.no/~trygver/themes/mvc/mvc-index.html
[3] http://heim.ifi.uio.no/~trygver/themes/mvc/mvc-index.html
 






