from itertools import product

from models import Room, Account, User, UserRole, BaseModel
from app import app, db
import hashlib
import cloudinary.uploader

def add_user(first_name, last_name, email, phone, avatar):

    # Thêm người dùng vào cơ sở dữ liệu
    u = User(first_name=first_name, last_name=last_name,
             email=email, phone=phone, avatar=avatar, user_role=UserRole.CUSTOMER)

    # # Upload avatar nếu có
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    db.session.commit()
