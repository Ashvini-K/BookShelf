import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

#from sqlalchemy import create_engine
#engine = create_engine('sqlite:///C:/Users/ashwi/Desktop/cs50/book_shelf/bookshelf/bookshelfs.db')





#application configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = "Ashiwni08"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/ashwi/Desktop/cs50/book_shelf/bookshelf/bookshelfs.db'
app.config['TESTING'] = False #if this enabled the login_required won't work
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') #use Set EMAIL_USER = your email address in the cmd 
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') #use Set EMAIL_PASS = your email address pwd

mail = Mail(app)


from bookshelf import routes