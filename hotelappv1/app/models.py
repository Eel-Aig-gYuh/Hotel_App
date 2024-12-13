import datetime
import hashlib

from sqlalchemy import Column, Integer, NVARCHAR, ForeignKey, DateTime, Boolean, CHAR, Enum, DECIMAL, Time, String
from sqlalchemy.orm import relationship, backref

from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin


class PaidMethod(RoleEnum):
    TIEN_MAT = 1
    CHUYEN_KHOAN = 2

class RoomStyle(RoleEnum):
    BINH_THUONG = 1
    GIA_DINH = 2
    DOANH_NHAN = 3
    VIP = 4


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

    def __str__(self):
        return self.username


class Profile(db.Model):
    __abstract__ = True

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    CMND = Column(CHAR(12), unique=True, nullable=False)
    last_name = Column(NVARCHAR(50), nullable=True)
    first_name = Column(NVARCHAR(20), nullable=False)
    phone = Column(CHAR(10), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)


class Staff(Profile):
    __tablename__ = 'staff'

    salary = Column(DECIMAL(18,2), nullable=True, default=0.0)

    # relationship with user_staff (one - to - one)
    user = relationship('User', backref='staff_user', lazy=True)
    # relationship with hotel_staff (many - to - one)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    # relationship with bill_staff (many - to - one)
    bills = relationship('Bill', backref='staff_bill', lazy=True)

    def __str__(self):
        return self.first_name


class Customer(Profile):
    __tablename__ = 'customer'

    is_foreign = Column(Boolean, default=False)

    # relationship with user_customer (one - to - one)
    user = relationship('User', backref='cus_user', lazy=True)
    # relationship with booking_customer (many - to - one)
    bookings = relationship('Booking', backref='cus_booking', lazy=True)

    def __str__(self):
        return self.first_name


class Rule(db.Model):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    value = Column(DECIMAL(18,2), nullable=False)

    # relationship with rule_hotel (many - to - one)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)

    # relationship with user_rule (many - to - many)
    staffs = relationship('Staff',
                         secondary='rule_staff',
                         lazy='subquery',
                         backref=backref('rules', lazy=True))

    def __str__(self):
        return self.name


class Hotel(db.Model):
    __tablename__ = 'hotel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(NVARCHAR(255), nullable=False)
    address = Column(NVARCHAR(255), nullable=False)
    phone = Column(CHAR(10), nullable=False)
    email = Column(String(100), nullable=False)
    checkin_time = Column(Time, nullable=False)
    checkout_time = Column(Time, nullable=False)
    active = Column(Boolean, default=True)

    # relationship with rule_hotel (many - to - one)
    rules = relationship('Rule', backref='rule_hotel', lazy=True)
    # relationship with hotel_staff (many - to - one)
    staffs = relationship('Staff', backref='staff_hotel', lazy=True)
    # relationship with hotel_room (many - to - one)
    rooms = relationship('Room', backref='room_hotel', lazy=True)

    # relationship with room_type_image (many - to - many)
    images = relationship('Image',
                          secondary='hotel_image',
                          lazy='subquery',
                          backref=backref('image_hotel', lazy=True))

    def __str__(self):
        return self.name


class Room(db.Model):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(CHAR(10), unique=True, nullable=False)
    is_available = Column(Boolean, default=True)
    active = Column(Boolean, default=True)

    # relationship with room_room_type (many - to - one)
    room_type_id = Column(Integer, ForeignKey('room_type.id'), nullable=False)

    # relationship with hotel_room (many - to - one)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    # relationship with booking_room (many - to - one)
    bookings = relationship('Booking', backref='room_booking', lazy=True)

    def __str__(self):
        return self.name


class RoomType(db.Model):
    __tablename__ = 'room_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(RoomStyle), nullable=False)
    description = Column(NVARCHAR(255), nullable=True)
    price_per_night = Column(DECIMAL(18,2), nullable=False)
    capacity = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

    # relationship with room_room_type (many - to - one)
    rooms = relationship('Room', backref='room_room_type', lazy=True)

    # relationship with room_type_service (many - to - many)
    services = relationship('Service',
                              secondary='room_service',
                              lazy='subquery',
                              backref=backref('service_room_type', lazy=True))

    # relationship with room_type_image (many - to - many)
    images = relationship('Image',
                            secondary='room_type_image',
                            lazy='subquery',
                            backref=backref('image_room_type', lazy=True))

    def __str__(self):
        return self.name


class Service(db.Model):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(NVARCHAR(100), nullable=False, unique=True)
    floor = Column(Integer, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    active = Column(Boolean, default=True)

    # relationship with service_image (many - to - many)
    images = relationship('Image',
                          secondary='service_image',
                          lazy='subquery',
                          backref=backref('image_service', lazy=True))

    def __str__(self):
        return self.name


class Image(db.Model):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uri = Column(String(100), nullable=True)

    def __str__(self):
        return self.uri


class Booking(db.Model):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    total = Column(DECIMAL(18,2), nullable=False)

    # relationship with booking_customer (many - to - one)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    # relationship with booking_room (many - to - one)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    # relationship with bill_booking (many - to - one)
    bills = relationship('Bill', backref='booking_bill', lazy=True)

    def __str__(self):
        return self.id


class Bill(db.Model):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(DECIMAL(18,2), nullable=False)
    payment_date = Column(DateTime, default=datetime.datetime.now())
    payment_method = Column(Enum(PaidMethod), default=PaidMethod.CHUYEN_KHOAN)
    active = Column(Boolean, default=True)

    # relationship with bill_staff (many - to - one)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    # relationship with bill_booking (many - to - one)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    # relationship with bill_bill_detail (one - to - one)
    detail = relationship('BillDetail', backref='bill_details', lazy=True)

    def __str__(self):
        return self.id


class BillDetail(db.Model):
    __tablename__ = "bill_detail"

    id = Column(Integer, ForeignKey('bill.id'), primary_key=True, autoincrement=True)
    num_foreign_customer = Column(Integer, nullable=False)
    num_local_customer = Column(Integer, nullable=False)

    def __str__(self):
        return self.id


rule_staff = db.Table(
    'rule_staff',
    Column('staff_id', Integer, ForeignKey('staff.id'), primary_key=True),
    Column('rule_id', Integer, ForeignKey('rule.id'), primary_key=True))

room_service = db.Table(
    'room_service',
    Column('room_type_id', Integer, ForeignKey('room_type.id'), primary_key=True),
    Column('service_id', Integer, ForeignKey('service.id'), primary_key=True))

hotel_image = db.Table(
    'hotel_image',
    Column('hotel_id', Integer, ForeignKey('hotel.id'), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id'), primary_key=True)
)

room_type_image = db.Table(
    'room_type_image',
    Column('room_type_id', Integer, ForeignKey('room_type.id'), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id'), primary_key=True)
)

service_image = db.Table(
    'service_image',
    Column('service_id', Integer, ForeignKey('service.id'), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id'), primary_key=True)
)

if __name__ == '__main__':
    with app.app_context():

        db.drop_all()
        db.create_all()

        data = {
            "user": [
                {"id": 1, "username": "admin", "password": str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 "is_admin": True},
                {"id": 2, "username": "staff1", "password": str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 "is_admin": False},
                {"id": 3, "username": "customer1", "password": str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 "is_admin": False},
                {"id": 4, "username": "staff2", "password": str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 "is_admin": False},
                {"id": 5, "username": "customer2", "password": str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 "is_admin": False},
            ],
            "staff": [
                {
                    "id": 2,
                    "CMND": "123456789012",
                    "last_name": "Nguyen",
                    "first_name": "Anh",
                    "phone": "0123456789",
                    "email": "staff1@example.com",
                    "avatar": "avatar_staff1.png",
                    "salary": 5000000.00,
                    "hotel_id": 1,
                },
                {
                    "id": 4,
                    "CMND": "234567890123",
                    "last_name": "Tran",
                    "first_name": "Cuong",
                    "phone": "0987654321",
                    "email": "staff2@example.com",
                    "avatar": "avatar_staff2.png",
                    "salary": 6000000.00,
                    "hotel_id": 1,
                },
            ],
            "customer": [
                {
                    "id": 3,
                    "CMND": "987654321098",
                    "last_name": "Le",
                    "first_name": "Huy",
                    "phone": "0987654321",
                    "email": "customer1@example.com",
                    "avatar": "avatar_customer1.png",
                    "is_foreign": False,
                },
                {
                    "id": 5,
                    "CMND": "876543210987",
                    "last_name": "Pham",
                    "first_name": "Anh",
                    "phone": "0123987654",
                    "email": "customer2@example.com",
                    "avatar": "avatar_customer2.png",
                    "is_foreign": True,
                },
            ],
            "rule": [
                {"id": 1, "name": "Thời gian checkin", "value": 28, "hotel_id": 1},
                {"id": 2, "name": "Khách tối đa", "value": 3, "hotel_id": 1},
                {"id": 3, "name": "Khách nước ngoài", "value": 1.5, "hotel_id": 1},
                {"id": 4, "name": "Phụ thu khách ngoài quy định", "value": 0.25, "hotel_id": 1},
            ],
            "hotel": [
                {
                    "id": 1,
                    "name": "Dream Hotel",
                    "address": "371 Nguyễn Kiệm, P.3, Quận Gò Vấp, TP. Hồ Chí Minh",
                    "phone": "0123456789",
                    "email": "dreamhotel@gmail.com",
                    "checkin_time": "14:00:00",
                    "checkout_time": "12:00:00",
                },
                {
                    "id": 2,
                    "name": "Moonlight Resort",
                    "address": "456 Moonlight Avenue",
                    "phone": "0987654321",
                    "email": "contact@moonlightresort.com",
                    "checkin_time": "15:00:00",
                    "checkout_time": "11:00:00",
                },
            ],
            "room_type": [
                {
                    "id": 1,
                    "name": "BINH_THUONG",
                    "description": "",
                    "price_per_night": 525000.00,
                    "capacity": 1,
                },
                {
                    "id": 2,
                    "name": "BINH_THUONG",
                    "description": "",
                    "price_per_night": 725000.00,
                    "capacity": 2,
                },
                {
                    "id": 3,
                    "name": "BINH_THUONG",
                    "description": "",
                    "price_per_night": 975000.00,
                    "capacity": 3,
                },
                {
                    "id": 4,
                    "name": "GIA_DINH",
                    "description": "Family-style room with extra space",
                    "price_per_night": 975000.00,
                    "capacity": 2,
                },
                {
                    "id": 5,
                    "name": "GIA_DINH",
                    "description": "Family-style room with extra space",
                    "price_per_night": 1255000.00,
                    "capacity": 3,
                },
                {
                    "id": 6,
                    "name": "DOANH_NHAN",
                    "description": "",
                    "price_per_night": 975000.00,
                    "capacity": 1,
                },
                {
                    "id": 7,
                    "name": "DOANH_NHAN",
                    "description": "",
                    "price_per_night": 1255000.00,
                    "capacity": 2,
                },
                {
                    "id": 8,
                    "name": "DOANH_NHAN",
                    "description": "",
                    "price_per_night": 1725000.00,
                    "capacity": 3,
                },
                {
                    "id": 9,
                    "name": "VIP",
                    "description": "Luxury room with premium amenities",
                    "price_per_night": 3000000.00,
                    "capacity": 2,
                },
                {
                    "id": 10,
                    "name": "VIP",
                    "description": "Luxury room with premium amenities",
                    "price_per_night": 3950000.00,
                    "capacity": 3,
                },
            ],
            "room": [
                {
                    "id": 1,
                    "name": "201",
                    "is_available": True,
                    "room_type_id": 1,
                    "hotel_id": 1,
                },
                {
                    "id": 2,
                    "name": "202",
                    "is_available": True,
                    "room_type_id": 1,
                    "hotel_id": 1,
                },
                {
                    "id": 3,
                    "name": "203",
                    "is_available": True,
                    "room_type_id": 1,
                    "hotel_id": 1,
                },
                {
                    "id": 4,
                    "name": "204",
                    "is_available": True,
                    "room_type_id": 2,
                    "hotel_id": 1,
                },
                {
                    "id": 5,
                    "name": "205",
                    "is_available": True,
                    "room_type_id": 3,
                    "hotel_id": 1,
                },
                {
                    "id": 6,
                    "name": "301",
                    "is_available": True,
                    "room_type_id": 4,
                    "hotel_id": 1,
                },
                {
                    "id": 7,
                    "name": "302",
                    "is_available": True,
                    "room_type_id": 4,
                    "hotel_id": 1,
                },
                {
                    "id": 8,
                    "name": "303",
                    "is_available": True,
                    "room_type_id": 5,
                    "hotel_id": 1,
                },
                {
                    "id": 9,
                    "name": "304",
                    "is_available": True,
                    "room_type_id": 5,
                    "hotel_id": 1,
                },
                {
                    "id": 10,
                    "name": "305",
                    "is_available": True,
                    "room_type_id": 5,
                    "hotel_id": 1,
                },
                {
                    "id": 11,
                    "name": "401",
                    "is_available": True,
                    "room_type_id": 6,
                    "hotel_id": 1,
                },
                {
                    "id": 12,
                    "name": "402",
                    "is_available": True,
                    "room_type_id": 6,
                    "hotel_id": 1,
                },
                {
                    "id": 13,
                    "name": "403",
                    "is_available": True,
                    "room_type_id": 7,
                    "hotel_id": 1,
                },
                {
                    "id": 14,
                    "name": "404",
                    "is_available": True,
                    "room_type_id": 7,
                    "hotel_id": 1,
                },
                {
                    "id": 15,
                    "name": "405",
                    "is_available": True,
                    "room_type_id": 8,
                    "hotel_id": 1,
                },
                {
                    "id": 16,
                    "name": "501",
                    "is_available": True,
                    "room_type_id": 9,
                    "hotel_id": 1,
                },
                {
                    "id": 17,
                    "name": "502",
                    "is_available": True,
                    "room_type_id": 10,
                    "hotel_id": 1,
                },
            ],
            "service": [
                {
                    "id": 1,
                    "name": "Spa",
                    "floor": 8,
                    "start_time": "08:00:00",
                    "end_time": "20:00:00",
                },
                {
                    "id": 2,
                    "name": "Gym",
                    "floor": 7,
                    "start_time": "06:00:00",
                    "end_time": "22:00:00",
                },
                {
                    "id": 3,
                    "name": "Restaurant",
                    "floor": 1,
                    "start_time": "07:00:00",
                    "end_time": "22:00:00",
                    "active": True,
                },
                {
                    "id": 4,
                    "name": "Pool",
                    "floor": 9,
                    "start_time": "06:00:00",
                    "end_time": "21:00:00",
                    "active": True,
                }
            ],
            "image": [
                {
                    "id": 1,
                    "uri": "room_type1_image1.png",
                    "room_type_id": 1,
                },
                {
                    "id": 2,
                    "uri": "room_type2_image1.png",
                    "room_type_id": 2,
                },
            ],
            "rule_staff": [
                {"staff_id": 2, "rule_id": 1},
                {"staff_id": 4, "rule_id": 2},
            ],
            "room_service": [
                {"room_type_id": 10, "service_id": 1},
                {"room_type_id": 10, "service_id": 2},
                {"room_type_id": 10, "service_id": 3},
                {"room_type_id": 10, "service_id": 4},

                {"room_type_id": 9, "service_id": 1},
                {"room_type_id": 9, "service_id": 2},
                {"room_type_id": 9, "service_id": 3},
                {"room_type_id": 9, "service_id": 4},

                {"room_type_id": 8, "service_id": 1},
                {"room_type_id": 8, "service_id": 2},
                {"room_type_id": 8, "service_id": 3},

                {"room_type_id": 7, "service_id": 1},
                {"room_type_id": 7, "service_id": 2},
                {"room_type_id": 7, "service_id": 3},

                {"room_type_id": 6, "service_id": 1},
                {"room_type_id": 6, "service_id": 2},
                {"room_type_id": 6, "service_id": 3},

                {"room_type_id": 5, "service_id": 3},
                {"room_type_id": 4, "service_id": 3},
            ],
        }

        for user in data['user']:
            db.session.add(User(**user))

        for staff in data['staff']:
            db.session.add(Staff(**staff))

        for customer in data['customer']:
            db.session.add(Customer(**customer))

        for rule in data['rule']:
            db.session.add(Rule(**rule))

        for hotel in data['hotel']:
            db.session.add(Hotel(**hotel))

        for room_type in data['room_type']:
            db.session.add(RoomType(**room_type))

        for room in data['room']:
            db.session.add(Room(**room))

        for service in data['service']:
            db.session.add(Service(**service))

        db.session.commit()
