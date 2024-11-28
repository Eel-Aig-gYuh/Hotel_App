import hashlib
from models import Room, Account
from app import db, app
import cloudinary.uploader


def load_room(page=1):
    rooms = Room.query.order_by('id')
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    rooms = rooms.slice(start, start + page_size)

    return rooms.all()

def count_rooms():
    return Room.query.count()


def get_account_by_id(id):
    return Account.query.get(id)


def auth_account(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return Account.query.filter(Account.username.__eq__(username),
                                Account.password.__eq__(password)).first()


def add_account(username, password, avatar=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = Account(username=username, password=password)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())

    return Account.query.filter(Account.username == username,
                                Account.password == password).first()
