import hashlib
from models import Room, Account, User, UserRole
from app import db, app
import cloudinary.uploader
from flask_login import current_user


def get_account_by_id(ids):
    return Account.query.get(ids)


def get_user_by_id(ids):
    return User.query.get(ids)


def auth_account(username, password, role=None):
    # băm mật khẩu
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    account = Account.query.filter(Account.username.__eq__(username),
                                   Account.password.__eq__(password))

    if role:
        account = account.filter(get_role().__eq__(role))

    return account.first()


def add_user(first_name, last_name, email, phone, avatar):

    # Thêm người dùng vào cơ sở dữ liệu
    user = User(first_name=first_name, last_name=last_name,
                email=email, phone=phone, avatar=avatar)

    # Upload avatar nếu có
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        # print(res)
        user.avatar = res.get("secure_url")

    db.session.add(user)
    db.session.commit()


def add_account(username, password, user_id):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    account = Account(username=username, password=password, user_id=user_id)

    db.session.add(account)
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


def read_hotel():
    pass


def get_role():
    account = db.session.query(Account).filter_by(username=current_user.username).first()

    if account:
        return account.account_user.user_role
