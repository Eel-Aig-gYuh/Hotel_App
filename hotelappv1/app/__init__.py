from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask import Flask
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# check file sql
# app.config["SQLALCHEMY_ECHO"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name="dnqt29l2e",
    api_key="891424754983193",
    api_secret="eDjYHZr6m13AH_BHZyxXkxDt7Ak",
    secure=True
)
