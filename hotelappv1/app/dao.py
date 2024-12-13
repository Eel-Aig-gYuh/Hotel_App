import hashlib

from models import Room, User, Staff, Hotel, Customer, RoomType, Rule
from app import db, app
import cloudinary.uploader
from flask_login import current_user


def get_user_by_id(ids):
    return User.query.get(ids)


def auth_user(username, password, is_admin):
    # băm mật khẩu
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    account = User.query.filter(User.username.__eq__(username),
                                User.password.__eq__(password),
                                User.is_admin.__eq__(is_admin))

    return account.first()


def add_user(username, password, first_name, last_name, email, phone, avatar):

    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    # Thêm người dùng vào cơ sở dữ liệu
    user = User(username=username, password=password, is_admin=False)

    # Upload avatar nếu có
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        # print(res)
        user.avatar = res.get("secure_url")

    db.session.add(user)
    db.session.commit()


def load_room(room_id=None, kw=None, page=1):
    rooms = Room.query.order_by('id')

    # tìm kiếm phòng
    if kw:
        rooms = rooms.filter(Room.room_name.contains(kw))

    if room_id:
        rooms = rooms.filter(Room.id == room_id)

    rooms = pagination(page=page)

    return rooms.all()


def pagination(page=1):
    query = Room.query.order_by('id')
    page_size = app.config['PAGE_SIZE']
    start = (int(page) - 1) * page_size

    return query.slice(start, start + page_size)


def count_rooms():
    return Room.query.count()

def count_users():
    return User.query.count()

def read_hotel():
    pass
