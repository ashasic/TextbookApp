# TextbookApp
Final Project

College students are spending thousands each year on textbooks they will use for a semester. <br>

With no system in place for colleges to facilitate inter-student exchanges of textbooks to save money. <br>

This app will change that. With this app, students can post their used textbooks for free and this way new students can go on here and when they are finished, post it again. with this method, students won't have to buy textbooks.<br>

## How it works: Students sign up using their University of Iowa email. They then input the isbn information of the textbook and find a post. Once found they can contact the person and set up an exchange date.

## Those involved: Professors will be the driving force in getting this out as they can introduce it to their classes for students who need textbooks and can't afford it. Admin users will be moderating posts and verifying identities of all users via email and other sources. Students can also add comments on whether this textbook is needed, if not available where to find cheaper options and etc..

## What will be used: To make this app we would be using fastAPI, MongoDB, and the 4 languages HTML/CSS/PYTHON/JAVASCRIPT
## MongoDB will be used as a database to store and sort different textbooks for different subjects so that students can use keywords to find what they're looking for.
## 

Below is a short demo on how this app can be used: <br>

![demo](https://github.com/talhanaveed753/Mid-term-Project-TICS1-/blob/main/expenseDEMO.mp4)

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
