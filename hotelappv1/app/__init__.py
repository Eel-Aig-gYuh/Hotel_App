from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask import Flask
from flask_login import LoginManager
import cloudinary
from datetime import timedelta


app = Flask(__name__)


app.secret_key = 'GH33*1SD4P03M*0FTH3DR34MC1TY'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldbfix?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# check file sql
# app.config["SQLALCHEMY_ECHO"] = True
app.config["PAGE_SIZE"] = 4
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app=app)

login = LoginManager()
login.init_app(app=app)


cloudinary.config(
    cloud_name="dnqt29l2e",
    api_key="891424754983193",
    api_secret="eDjYHZr6m13AH_BHZyxXkxDt7Ak",
    secure=True
)
