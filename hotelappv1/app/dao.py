import hashlib

from models import Room, User, Staff, Hotel, Customer, RoomType, Rule, Image, Service
from app import db, app


def get_user_by_id(ids):
    return User.query.get(ids)

def get_user_by_username(username):
    return User.query.filter(User.username.__eq__(username)).first().id

def auth_user(username, password, is_admin=None):
    # băm mật khẩu
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    account = User.query.filter(User.username.__eq__(username),
                                User.password.__eq__(password))

    if is_admin:
        account = account.filter(User.is_admin.__eq__(True))

    return account.first()

def check_user(username):
    return User.query.filter(User.username.__eq__(username)).first()

def check_email(email):
    return Customer.query.filter(Customer.email.__eq__(email)).first()

def add_user(first_name, last_name, cmnd, email, phone, username, password):

    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    # Thêm người dùng vào cơ sở dữ liệu
    user = User(username=username, password=password, is_admin=False)
    db.session.add(user)
    customer = Customer(id=get_user_by_username(username), first_name=first_name, last_name=last_name, email=email, phone=phone, CMND=cmnd)
    db.session.add(customer)
    db.session.commit()


def load_room(room_id=None, kw=None, page=1):
    # lấy phòng trống.
    available_room = db.session.query(Room).filter(Room.active==True and Room.is_available==True).order_by('id').all()

    # lấy room_type tương ứng.
    available_room_types = set()
    for room in available_room:
        room_type = room.room_room_type
        available_room_types.add(room_type)

    return available_room_types


def load_img(type_img):
    img = Image.query.filter(Image.uri.contains(type_img)).all()
    return img

def load_service():
    service = db.session.query(Service).filter(Service.active==True).all()

    return service

def pagination(page=1):
    query = Room.query.order_by('id')
    page_size = app.config['PAGE_SIZE']
    start = (int(page) - 1) * page_size

    return query.slice(start, start + page_size)


def count_rooms():
    return Room.query.count()
