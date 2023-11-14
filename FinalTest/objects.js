let steps = [  
    {
        "title": "Step1: Navigate to the Project Directory",
        "text": "When you have cloned the repository from GitHub to your local machine with git clone, change your current directory to our project's directory.",
        "image": "images/step1.png",
        "aside": {
            "label": "aside1",
            "note": "aside content "
        }
    },
    {
        "title": "Step2: Set up python virtual environment",
        "text": "It's a good practice to create a virtual environment for Python projects to isolate the project-specific dependencies. You can create a virtual environment using the command: python3 -m MealMate_venv venv",
        "image": "images/step2.png",
        "aside": {
            "label": "aside2",
            "note": "aside content "
        }
    },
    {
        "title": "Step3: Install the required packages",
        "text": "Since the libraries provide specific functionalities and features that are not included in the base Python language, you need to ensure that all the external libraries and dependencies the project needs to function correctly and available.Our project file includes a 'requirement.txt' file, you can install required packages using the command: pip install -r requirements.txt",
        "image": "images/step3.png",
        "aside": {
            "label": "aside3",
            "note": "aside content "
        }
    },

    {
        "title": "Step4: Set the FLASK_APP environment Variable",
        "text": " You need to tell Flask where your application is located. Our file is named app.py, so you can use the command: export FLASK_APP = app.py. On Windows, use the 'set' command instead of export.",
        "image": "images/step4.png",
        "aside": {
            "label": "aside4",
            "note": "aside content "
        }
     
    },

    {
        "title": "Step5: Initialize the database",
        "text": " To initialize the database, create the necessary tables, and apply any existing migrations. You can usually initialize the database using these commands:",
        "image": "images/step5.png",
        "aside": {
            "label": "aside5",
            "note": "aside content "
        }
     
    },
    
    {
        "title": "Step6: Run the application",
        "text": "Finally, you can run the Flask application using the following command: 'flask run'.  Your Flask application should now be running on your local machine. By default, Flask applications run on port 5000. You can access it by opening a web browser and navigating to http://localhost:5000.",
        "image": "images/step6.png",
        "aside": {
            "label": "aside6",
            "note": "aside content "
        }
     
    },

];

        function createStepElement(step) {
        let stepElement = document.createElement('section');

        // Create the header element
        let header = document.createElement('div');
        header.classList.add('header');
        stepElement.appendChild(header);

        // Create and append the title
        let title = document.createElement('h2');
        title.textContent = "Step " + (steps.indexOf(step) + 1) + ": " + step.title;
        header.appendChild(title);

        // Create and append the aside in the header
        let aside = document.createElement('div');
        let button = document.createElement('button');
        button.classList.add('help-icon');  // add class to button
        let icon = document.createElement('img');
        icon.src = "./images/question_icon.png"; 
        button.appendChild(icon);


        let note = document.createElement('p');
        note.style.display = 'none'; 
        note.textContent = step.aside.note;
        button.addEventListener('mouseenter', function() {
            note.style.display = 'block'; 
        });
        button.addEventListener('mouseleave', function() {
            note.style.display = 'none'; 
        });
        aside.appendChild(button);
        aside.appendChild(note);
        header.appendChild(aside);

        // Create and append the description
        let text = document.createElement('p');
        text.innerHTML = step.text;
        stepElement.appendChild(text);

        // Create and append the image
        let image = document.createElement('img');
        image.src = step.image;
        stepElement.appendChild(image);

        return stepElement;
    }

    // Append each step to the build-run-instructions section
    let instructionsElement = document.getElementById('build-run-instructions');
    steps.forEach(function(step) {
        instructionsElement.appendChild(createStepElement(step));
    });