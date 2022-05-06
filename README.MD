Web application on Flask for Project Management

## Description

This application allows you to manage your projects. You can create users via Sign Up form or use admin user (login: admin@admin.com, password: admin) to create new users. Admin user has unlimited access to web-application. He can edit/delete/complete any project/task, while other users can only edit/delete/complete those projects where they are managers and those tasks where they are executors.

## Installation

First, clone this repository.

```
git clone http://github.com/ShabUlysses/task-tracker
```

```
cd task-tracker
```

Then, install plugins and packages that are necessary for this project to run:

```
pip install -r requirements.txt
```

Create .env file in root directory of the project. Inside .env file create variable SECRET_KEY and assign any key to it.
Also create variable SQLALCHEMY_DATABASE_URI = sqlite:///pmadpp.db

```
Example:
SECRET_KEY = 5122955e3bfb722eb16b7b7664fa9727

SQLALCHEMY_DATABASE_URI = sqlite:///pmapp.db
```

Then, run the application:

```
python run.py
```

To see application, access this url in your browser:
http://localhost:5000

You should see the welcome page if everything has been done correctly.

## Usage example

