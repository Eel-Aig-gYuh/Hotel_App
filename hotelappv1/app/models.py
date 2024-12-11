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


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False, unique=True)

    def __str__(self):
        return self.username


class Profile(db.Model):
    __tablename__ = 'profile'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    CMND = Column(CHAR(12), unique=True, nullable=False)
    last_name = Column(NVARCHAR(50), nullable=True)
    first_name = Column(NVARCHAR(20), nullable=False)
    phone = Column(CHAR(10), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)

    def __str__(self):
        return self.first_name


class Staff(db.Model):
    __tablename__ = 'staff'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    salary = Column(DECIMAL(18,2), nullable=True, default=0.0)

    # relationship with hotel_staff (many - to - one)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    # relationship with bill_staff (many - to - one)
    bills = relationship('Bill', backref='staff_bill', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    is_foreign = Column(Boolean, default=False)

    # relationship with booking_customer (many - to - one)
    bookings = relationship('Booking', backref='cus_booking', lazy=True)


class Rule(db.Model):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    value = Column(DECIMAL(18,2), nullable=False)

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
    image = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)

    # relationship with hotel_staff (many - to - one)
    staffs = relationship('Staff', backref='staff_hotel', lazy=True)
    # relationship with hotel_room (many - to - one)
    rooms = relationship('Room', backref='room_hotel', lazy=True)

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
    name = Column(NVARCHAR(100), nullable=False)
    description = Column(NVARCHAR(255), nullable=True)
    price_per_night = Column(DECIMAL(18,2), nullable=False)
    capacity = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

    # relationship with room_room_type (many - to - one)
    rooms = relationship('Room', backref='room_room_type', lazy=True)
    # relationship with room_type_image (many - to - one)
    images = relationship('Image', backref='image_room_type', lazy=True)

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

    # relationship with room_type_service (many - to - many)
    room_types = relationship('room_type',
                              secondary='room_service',
                              lazy='subquery',
                              backref=backref('services', lazy=True))

    def __str__(self):
        return self.name


class Image(db.Model):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uri = Column(String(100), nullable=True)

    # relationship with room_type_image (many - to - one)
    room_type_id = Column(Integer, ForeignKey('room_type.id'), nullable=False)

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


rule_staff = db.Table('rule_staff',
                 Column('staff_id', Integer, ForeignKey('staff.id'), primary_key=True),
                 Column('rule_id', Integer, ForeignKey('rule.id'), primary_key=True))
room_service = db.Table('service_room',
                        Column('room_type_id', Integer, ForeignKey('room_type.id'), primary_key=True),
                        Column('service_id', Integer, ForeignKey('service.id'), primary_key=True))


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
