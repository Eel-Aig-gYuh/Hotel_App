import datetime
import hashlib

from sqlalchemy import Column, Integer, NVARCHAR, ForeignKey, DateTime, Boolean, CHAR, Enum, DECIMAL, Time, String
from sqlalchemy.orm import relationship, backref, mapped_column

from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserRole(RoleEnum):
    ADMIN = 1
    EMPLOYEE = 2
    CUSTOMER = 3


class CustomerType(RoleEnum):
    NOI_DIA = 1
    NUOC_NGOAI = 2


class BookingStatus(RoleEnum):
    YEU_CAU = 1
    XAC_NHAN = 2
    HUY_PHONG = 3
    CHECK_IN = 4
    CHECK_OUT = 5


class RoomStatus(RoleEnum):
    CON_TRONG = 1
    DA_DAT = 2
    DANG_SU_DUNG = 3
    DANG_DON_DEP = 4


class RoomStyle(RoleEnum):
    BINH_THUONG = 1
    GIA_DINH = 2
    DOANH_NHAN = 3
    VIP = 4


class PaidMethod(RoleEnum):
    TIEN_MAT = 1
    CHUYEN_KHOAN = 2


class BedType(RoleEnum):
    DON = 1
    DOI = 2


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    created_day = Column(DateTime, default=datetime.datetime.now)
    updated_day = Column(DateTime, onupdate=datetime.datetime.now)


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(NVARCHAR(255), nullable=False)
    last_name = Column(NVARCHAR(255), nullable=False)
    email = Column(NVARCHAR(100), nullable=False, unique=True)
    phone = Column(CHAR(10), nullable=False, unique=True)
    avatar = Column(String(100), nullable=True)
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    # relationships
    # with user_admin (one - to - one)
    user_admin = relationship('Admin', backref='admin_user', uselist=False)

    # with user_employee (one - to - one)
    user_employee = relationship('Employee', backref='employee_user', uselist=False)

    # with user_customer (one - to - one)
    user_customer = relationship('Customer', backref='customer_user', uselist=False)

    # with user_account (many - to - one)
    user_accounts = relationship('Account',
                                 backref='account_user', cascade='all, delete', lazy=True)


class Rule(BaseModel):
    __tablename__ = 'rule'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(NVARCHAR(255), nullable=False, unique=True)
    rule_value = Column(DECIMAL(18, 2), nullable=True, default=0.00)

    # relationships
    # with admin_rule (many - to - many)
    admins = relationship('Admin',
                          secondary='admin_rules',
                          lazy='subquery',
                          backref=backref('rule', lazy=True),
                          overlaps='rule, admin',
                          viewonly=True)


class Admin(db.Model):
    __tablename__ = 'admin'

    # bị dính bảng với user
    id = Column(Integer, primary_key=True, autoincrement=True)

    # sửa lại giải pháp chuyển thành quan hệ (one - to - one)

    # with user_admin (one - to - one)
    user_id = mapped_column(ForeignKey('user.id'), nullable=False)

    # relationships
    # with user_admin (one - to - one)
    # admin_user = relationship('User', backref='user_admin')

    # with admin_rule (many - to - many)
    rules = relationship('Rule',
                         secondary='admin_rules',
                         lazy='subquery',
                         backref=backref("admin", lazy=True),
                         overlaps='admin, rule',
                         viewonly=True)

    # with admin_room_management (many - to - one)
    room_managements = relationship('RoomManagement',
                                    backref='admin', lazy=True)


#
class Employee(db.Model):
    __tablename__ = 'employee'

    # bị dính bảng với user
    id = Column(Integer, primary_key=True, autoincrement=True)

    # sửa lại giải pháp chuyển thành quan hệ (one - to - one)

    # foreign key
    # with user_employee (one - to - one)
    user_id = mapped_column(ForeignKey('user.id'), nullable=False)

    # relationships
    # with user_employee (one - to - one)
    # employee_user = relationship('User', backref='user_employee')

    # with employee_room_booking (many - to - one)
    e_bookings = relationship("RoomBooking",
                              backref="employee", lazy=True)
    # with employee_report (many - to - one)
    reports = relationship("Report",
                           backref="employee", lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'

    # bị dính bảng với user
    id = Column(Integer, primary_key=True, autoincrement=True)

    # sửa lại giải pháp chuyển thành quan hệ (one - to - one)

    cmnd = Column(CHAR(12), nullable=True, unique=True)
    address = Column(NVARCHAR(255), nullable=True, default=None)
    customer_type = Column(Enum(CustomerType), default=CustomerType.NOI_DIA)

    # foreign key
    # with user_customer (one - to - one)
    user_id = mapped_column(ForeignKey('user.id'), nullable=False)

    # relationships
    # with user_customer (one - to - one)
    # customer_user = relationship('User', backref='user_customer')

    # with customer_room_booking (many - to - one)
    c_bookings = relationship("RoomBooking",
                              backref="customer", lazy=True)


class Account(BaseModel, UserMixin):
    __tablename__ = 'account'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(NVARCHAR(250), nullable=False, unique=True)
    password = Column(NVARCHAR(250), nullable=False)

    # foreign key
    # with user_account (many - to - one)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    # relationships
    # with user (many - to - one)
    # account_user = relationship('User', backref='user_accounts')


class Hotel(BaseModel):
    __tablename__ = 'hotel'

    name = Column(NVARCHAR(255), nullable=False, unique=True)
    description = Column(NVARCHAR(255), nullable=True, default=None)

    # relationships
    # with hotel_hotel_location (many - to - one)
    locations = relationship('HotelLocation',
                             backref='hotel', cascade='all, delete', lazy=True)

    def __str__(self):
        return self.name


class HotelLocation(BaseModel):
    __tablename__ = 'hotelLocation'

    address = Column(NVARCHAR(255), nullable=False)
    hot_line = Column(CHAR(10), nullable=False)

    # foreign key
    # with hotel_hotel_location (many - to - one)
    hotel_id = Column(Integer,
                      ForeignKey('hotel.id', ondelete="CASCADE"), nullable=False)

    # relationships
    # with hotel_hotel_location (many - to - one)
    # hotel = relationship('Hotel', backref='locations')
    # with hotel_location_room (many - to - one)
    rooms = relationship('Room',
                         backref='hotel', cascade='all, delete', lazy=True)
    # with hotel_location_service (many - to - one)
    services = relationship('Service',
                            backref='hotel_location', lazy=True)

    def __str__(self):
        return self.address


class Room(BaseModel):
    __tablename__ = 'room'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(NVARCHAR(100), nullable=False, unique=True)
    room_prices = Column(DECIMAL(18, 2), nullable=False, default=0.00)
    notes = Column(NVARCHAR(255), nullable=True, default=None)

    # Enum
    room_status = Column(Enum(RoomStatus), nullable=False, default=RoomStatus.CON_TRONG)
    room_style = Column(Enum(RoomStyle), nullable=False, default=RoomStyle.BINH_THUONG)

    # foreign key
    # with hotel_location_room (many - to - one)
    hotel_location_id = Column(Integer,
                               ForeignKey('hotelLocation.id', ondelete="CASCADE"), nullable=False)

    # relationships
    # with room_service (many - to - many)
    services = relationship('Service',
                            secondary='room_services',
                            lazy='subquery',
                            backref=backref('room', lazy=True),
                            overlaps='rooms, service',
                            viewonly=True)

    # with hotel_location_room (many - to - one)
    # hotel = relationship('HotelLocation', backref='rooms')
    # with admin_room_management (many - to - one)
    room_managements = relationship('RoomManagement',
                                    backref='room', lazy=True)
    # with room_room_booking (many - to - one)
    r_bookings = relationship('RoomBooking',
                              backref='', lazy=True)
    # with room_feature (many - to - one)
    features = relationship('Feature',
                            backref='room', lazy=True)
    # with room_bed (many - to - one)
    beds = relationship('Bed',
                        backref='room', lazy=True)
    # with room_image (many - to - one)
    images = relationship("Image",
                          backref="room", lazy=True)

    def __str__(self):
        return self.room_name


class Bed(BaseModel):
    __tablename__ = 'bed'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    bed_type = Column(Enum(BedType), default=BedType.DON)

    # foreign key
    # with room_bed (many - to - one)
    room_id = Column(Integer,
                     ForeignKey('room.id'), nullable=False)

    # relationships
    # with room_bed (many - to - one)
    # room = relationship('Room', backref='beds')


class Feature(BaseModel):
    __tablename__ = 'feature'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(NVARCHAR(100), nullable=False)
    amount = Column(Integer, nullable=False, default=1)

    # foreign key
    # with room_feature (many - to - one)
    room_id = Column(Integer,
                     ForeignKey('room.id'), nullable=False)

    # relationships
    # with room_feature (many - to - one)
    # room = relationship('Room', backref='features')


class Image(db.Model):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100), nullable=False)

    # foreign key
    # with room_image (many - to - one)
    room_id = Column(Integer,
                     ForeignKey('room.id'), nullable=False)

    # relationships
    # with room_image (many - to - one)
    # room = relationship('Room', backref='images')


class Service(BaseModel):
    __tablename__ = 'service'

    service_name = Column(NVARCHAR(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(Integer, nullable=False)

    # foreign key
    # with hotel_location_service (many - to - one)
    hotel_location_id = Column(Integer,
                               ForeignKey('hotelLocation.id'), nullable=False)
    # with bill_detail_service (many - to - one)
    # bill_detail_id = Column(Integer,
    #                         ForeignKey('billDetail.id'), nullable=False)

    # relationships
    # with room_service (many - to - many)
    rooms = relationship('Room',
                         secondary='room_services',
                         lazy='subquery',
                         backref=backref('service', lazy=True),
                         overlaps='services, room',
                         viewonly=True)

    # with hotel_location_service (many - to - one)
    # hotel_location = relationship('HotelLocation', backref='services')
    # with bill_detail_service (many - to - one)
    bill_details = relationship('BillDetail',
                                backref='service', lazy=True)
    # bill_detail = relationship('BillDetail', backref='services')


class RoomBooking(BaseModel):
    __tablename__ = 'roomBooking'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    check_in_day = Column(DateTime, nullable=False)
    check_out_day = Column(DateTime, nullable=False)
    duration_in_day = Column(DECIMAL(18, 2), nullable=True, default=None)
    booking_status = Column(Enum(BookingStatus), default=BookingStatus.YEU_CAU)

    # foreign key
    # with customer_room_booking (many - to - one)
    customer_id = Column(Integer,
                         ForeignKey(Customer.id), nullable=False)
    # with employee_room_booking (many - to - one)
    employee_id = Column(Integer,
                         ForeignKey(Employee.id), nullable=False)
    # with room_room_booking (many - to - one)
    room_id = Column(Integer,
                     ForeignKey('room.id'), nullable=False)

    # relationships
    # with customer_room_booking (many - to - one)
    # customer = relationship('Customer', backref='c_bookings')
    # with employee_room_booking (many - to - one)
    # employee = relationship('Employee', backref='e_bookings')
    # with room_room_booking (many - to - one)
    # room = relationship('Room', backref='r_bookings')

    # with room_booking_room_booking_detail (one - to - one)
    detail = relationship('RoomBookingDetail', backref='room_booking', uselist=False)
    # room_booking_bill (one - to - one)
    bill = relationship('Bill', backref='room_booking', uselist=False)


class RoomBookingDetail(db.Model):
    __tablename__ = 'roomBookingDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num_normal_guest = Column(Integer, nullable=True, default=0)
    num_foreign_guest = Column(Integer, nullable=True, default=0)

    # foreign key
    # with room_booking_room_booking_detail (one - to - one)
    room_booking_id = Column(Integer,
                             ForeignKey('roomBooking.id'), nullable=False)

    # relationships
    # with room_booking_room_booking_detail (one - to - one)
    # room_booking = relationship('RoomBooking', backref='detail')


class RoomManagement(db.Model):
    __tablename__ = 'roomManagement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False, default=datetime.date.month)
    updated_day = Column(DateTime, onupdate=datetime.datetime.now)

    # foreign key
    # with admin (many - to - one)
    admin_id = Column(ForeignKey(Admin.id), primary_key=True, nullable=False)
    # with room (many - to - one)
    room_id = Column(ForeignKey(Room.id), primary_key=True, nullable=False)

    # relationships
    # with admin (many - to - one)
    # admins = relationship('Admin', backref='room_managements')
    # with room (many - to - one)
    # rooms = relationship('Room', backref='room_managements')


class Bill(db.Model):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(DECIMAL(18, 2), nullable=False)
    created_day = Column(DateTime, default=datetime.datetime.now)
    paid_method = Column(Enum(PaidMethod), nullable=False, default=PaidMethod.TIEN_MAT)
    is_paid = Column(Boolean, default=False)

    # foreign key
    # room_booking_bill (one - to - one)
    room_booking_id = Column(Integer,
                             ForeignKey('roomBooking.id'), nullable=False)

    # relationships
    # with report_bill (many - to - many)
    reports = relationship("Report",
                           lazy='subquery',
                           secondary='report_bills',
                           backref=backref('bill', lazy=True),
                           overlaps='bill, reports',
                           viewonly=True)

    # with bill_bill_detail (many - to - one)
    bill_details = relationship('BillDetail',
                                backref='bill', lazy=True)

    # with room_booking_bill (one - to - one)
    # room_booking = relationship('RoomBooking', backref='bill')


class BillDetail(db.Model):
    __tablename__ = 'billDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(NVARCHAR(255), nullable=False, unique=True)
    value = Column(DECIMAL(18, 2), nullable=False, default=0.00)

    # foreign key
    # with bill_bill_detail (many - to - one)
    bill_id = Column(Integer,
                     ForeignKey("bill.id"), nullable=False)
    # with bill_detail_service (many - to - one)
    service_id = Column(Integer,
                        ForeignKey('service.id'), nullable=False)

    # relationships
    # with bill_bill_detail (many - to - one)
    # bill = relationship('Bill', backref='bill_details')
    # with bill_detail_service (many - to - one)
    # services = relationship('Service',
    #                         backref='bill_detail', lazy=True)


class Report(db.Model):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_month = Column(Integer, nullable=True, default=datetime.date.month)
    created_day = Column(DateTime, default=datetime.datetime.now)
    total = Column(DECIMAL(18, 2), nullable=False)

    room_style = Column(Enum(RoomStyle), nullable=False, default=RoomStyle.BINH_THUONG)

    # foreign key
    # with employee_report (many - to - one)
    employee_id = Column(Integer,
                         ForeignKey(Employee.id), nullable=False)

    # relationships
    # with report_report_detail (one - to - one)
    detail = relationship('ReportDetail', backref='report', uselist=False)

    # with employee_report (many - to - one)
    # employee = relationship("Employee", backref='reports')

    # with report_bill (many - to - many)
    bills = relationship("Bill",
                         lazy='subquery',
                         secondary='report_bills',
                         backref=backref('report', lazy=True),
                         overlaps='reports, bill',
                         viewonly=True)


class ReportDetail(db.Model):
    __tablename__ = 'reportDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rent_amount = Column(Integer, nullable=False)
    rent_percent = Column(DECIMAL(18, 2), nullable=False)
    rent_total = Column(DECIMAL(18, 2), nullable=False)

    # foreign key
    # with report_report_detail (one - to - one)
    report_id = Column(Integer,
                       ForeignKey('report.id'), nullable=False)

    # relationships
    # with report_report_detail (one - to - one)
    # report = relationship('Report', backref='detail')


admin_rules = db.Table('admin_rules',
                       Column('admin_id', Integer, ForeignKey(Admin.id), primary_key=True),
                       Column('rule_id', Integer, ForeignKey(Rule.id), primary_key=True)
                       )

report_bills = db.Table('report_bills',
                        Column('report_id', Integer, ForeignKey(Report.id), primary_key=True),
                        Column('bill_id', Integer, ForeignKey(Bill.id), primary_key=True)
                        )

room_services = db.Table('room_services',
                         Column('room_id', Integer, ForeignKey(Room.id), primary_key=True),
                         Column('service_id', Integer, ForeignKey(Service.id), primary_key=True)
                         )

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()

        # u = User(first_name='Huy', last_name='Le',
        #          email='giahuyle1030@gmail.com', phone='0899308758', user_role=UserRole.ADMIN)
        # acc = Account(username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_id=1)
        #
        # user = User(first_name='Phu', last_name='Nguyen',
        #          email='phunguyen36@gmail.com', phone='3850790', user_role=UserRole.CUSTOMER)
        # db.session.add(user)
        # db.session.add(u)
        # db.session.add(acc)

        db.session.commit()