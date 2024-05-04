# TextbookApp
### Final Project

College students are spending thousands each year on textbooks they will use for a semester. <br>

With no system in place for colleges to facilitate inter-student exchanges of textbooks to save money. <br>

This app will change that. With this app, students can post their used textbooks for free and this way new students can go on here and when they are finished, post it again. With this method, students won't have to buy textbooks.<br>

## How it works: 
Students sign up using their email. They then input the ISBN information of the textbook and find a post. Once found they can contact the person and set up an exchange date.

## Those involved: 
Professors will be the driving force in getting this out as they can introduce it to their classes for students who need textbooks and can't afford them. Admin users will be moderating posts and verifying the identities of all users via email and other sources. Students can also add comments on whether this textbook is needed.

## What will be used: 
To make this app we would be using fast API, MongoDB, along with Python, HTML, and CSS MongoDB will be used as a database to store the textbooks along with storing students and admin information to specify roles and user data. For the textbook data, we will be using the Google Books API key.

## Procedure
Once you open up our app you will be greeted with a login/sign-up option and from there they can search for their desired textbook and once found, reserve it and contact the user who posted it. 

To run this code, follow the steps outlined below: <br>

## Step 1: Ensure that the latest version of python is installed. <br>

## Step 2: Create and activate a virtual python environment using the following commands: <br>
        python -m venv venv
        .\venv\Scripts\activate

Once done using this code, use 'deactivate' to deactivate the venv <br>

## Step 3: Install fastAPI/uvicorn <br>
        pip install fastapi uvicorn

## Step 3: Connect FastAPI to MongoDB <br>
        pip install motor


This should install all the required dependencies <br>
Alternatively, you can use 'pip install -r requirements.txt' <br>

Use 'python -m pip list' to view all the currently installed dependencies <br>
You can view requirements.txt to see all required dependencies <br>

Use 'pip freeze > requirements.txt' command to create a file with all required dependencies


