import datetime
from sqlalchemy import Column, Integer, NVARCHAR, ForeignKey, DateTime, Boolean, CHAR, Enum, VARCHAR, DECIMAL
from sqlalchemy.orm import relationship, backref

from app import db, app
from enum import Enum as RoleEnum


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
    VIP = 2


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
    avatar = Column(VARCHAR(100), nullable=True, default=None)
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    # relationships
    # with user_account (many - to - one)
    accounts = relationship('Account',
                            backref='user', cascade='all, delete', lazy=True)

    def __str__(self):
        return self.first_name

    def create_user(self):
        pass

    def search_room(self):
        pass


class Rule(BaseModel):
    __tablename__ = 'rule'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(NVARCHAR(255), nullable=False, unique=True)
    rule_value = Column(DECIMAL(18, 2), nullable=True, default=0.00)

    # relationships
    # with admin (many - to - many)
    admins = relationship('Admin',
                          secondary='admin_rules',
                          lazy='subquery',
                          backref=backref('rules', lazy=True))

    def __str__(self):
        return self.rule_name


class Admin(User):
    __tablename__ = 'admin'

    # id = Column(Integer, primary_key=True, autoincrement=True)

    # relationships
    # with rule (many - to - many)
    rules = relationship('Rule',
                         secondary='admin_rules',
                         lazy='subquery',
                         backref=backref("admins", lazy=True))

    # with room_management (many - to - one)
    room_managements = relationship('RoomManagement',
                                    backref='admins', lazy=True)

    def __str__(self):
        return self.id


class Employee(User):
    __tablename__ = 'employee'

    # id = Column(Integer, primary_key=True, autoincrement=True)

    # relationships
    # with RoomBooking (many - to - one)
    e_bookings = relationship("RoomBooking",
                              backref="employee", lazy=True)
    # # with employee_report (many - to - one)
    reports = relationship("Report",
                           backref="employee", lazy=True)

    def __str__(self):
        return self.id


class Customer(User):
    __tablename__ = 'customer'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    cmnd = Column(CHAR(12), nullable=False, unique=True)
    address = Column(NVARCHAR(255), nullable=True, default=None)
    customer_type = Column(Enum(CustomerType), default=CustomerType.NOI_DIA)

    # relationships
    # with customer_room_booking (many - to - one)
    c_bookings = relationship("RoomBooking",
                              backref="customer", lazy=True)

    def __str__(self):
        return self.cmnd


class Account(BaseModel):
    __tablename__ = 'account'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(NVARCHAR(250), nullable=False, unique=True)
    password = Column(NVARCHAR(250), nullable=False)

    # foreign key
    # with user_account (many - to - one)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    # relationships
    # with user (many - to - one)
    user = relationship('User', backref='accounts')

    def __str__(self):
        return self.user_name

    def change_password(self):
        pass

    def reset_password(self):
        pass


class Room(BaseModel):
    __tablename__ = 'room'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(NVARCHAR(100), nullable=False, unique=True)
    room_prices = Column(DECIMAL(18, 2), nullable=False, default=0.00)
    notes = Column(NVARCHAR(255), nullable=True, default=None)

    # Enum
    room_status = Column(Enum(RoomStatus), nullable=False, default=RoomStatus.CON_TRONG)
    room_style = Column(Enum(RoomStyle), nullable=False, default=RoomStyle.BINH_THUONG)

    # relationships
    # with admin_room_management (many - to - one)
    room_managements = relationship('RoomManagement',
                                    backref='rooms', lazy=True)
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
    room = relationship('Room', backref='beds')

    def __str__(self):
        return self.key


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
    room = relationship('Room', backref='features')

    def __str__(self):
        return self.feature_name


class Image(db.Model):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(VARCHAR(255), nullable=True, default=None)

    # foreign key
    # with room_image (many - to - one)
    room_id = Column(Integer,
                     ForeignKey('room.id'), nullable=False)

    # relationships
    # with room_image (many - to - one)
    room = relationship('Room', backref='images')

    def __str__(self):
        return self.url


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
    customer = relationship('Customer', backref='c_bookings')
    # with employee_room_booking (many - to - one)
    employee = relationship('Employee', backref='e_bookings')
    # with room_room_booking (many - to - one)
    room = relationship('Room', backref='r_bookings')

    # with room_booking_room_booking_detail (one - to - one)
    detail = relationship('RoomBookingDetail', backref='room_booking', uselist=False)
    # room_booking_bill (one - to - one)
    bill = relationship('Bill', backref='room_booking', uselist=False)

    def __str__(self):
        return self.id


class RoomBookingDetail(db.Model):
    __tablename__ = 'roomBookingDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num_normal_guest = Column(Integer, nullable=True, default=0)
    num_foreign_guest = Column(Integer, nullable=True, default=0)

    # foreign key
    # with room_booking_room_booking_detail (one - to - one)
    room_booking_id = Column(Integer,
                             ForeignKey('roomBooking.id'), unique=True)

    # relationships
    # with room_booking_room_booking_detail (one - to - one)
    room_booking = relationship('RoomBooking',
                                backref='detail')

    def __str__(self):
        return self.id


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
    admins = relationship('Admin', backref='room_managements')
    # with room (many - to - one)
    rooms = relationship('Room', backref='room_managements')

    def __str__(self):
        return self.id


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
                             ForeignKey('roomBooking.id'), unique=True)

    # relationships
    # with report_bill (many - to - many)
    reports = relationship("Report",
                           lazy='subquery',
                           secondary='report_bills',
                           backref=backref('bills', lazy=True))

    # with bill_bill_detail (many - to - one)
    bill_details = relationship('Bill',
                                backref='', lazy=True)

    # with room_booking_bill (one - to - one)
    room_booking = relationship('RoomBooking', backref='bill')


class BillDetail(db.Model):
    __tablename__ = 'billDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(NVARCHAR(255), nullable=False, unique=True)
    value = Column(DECIMAL(18, 2), nullable=False, default=0.00)

    # foreign key
    # with bill_bill_detail (many - to - one)
    bill_id = Column(Integer,
                     ForeignKey("bill.id"), nullable=False)

    # relationships
    # with bill_bill_detail (many - to - one)
    bill = relationship('Bill', backref='bill_details')

    def __str__(self):
        return self.key


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
    employee = relationship("Employee", backref='reports')

    # with report_bill (many - to - many)
    bills = relationship("Bill",
                         lazy='subquery',
                         secondary='report_bills',
                         backref=backref('reports', lazy=True))

    def __str__(self):
        return self.report_month


class ReportDetail(db.Model):
    __tablename__ = 'reportDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rent_amount = Column(Integer, nullable=False)
    rent_percent = Column(DECIMAL(18, 2), nullable=False)
    rent_total = Column(DECIMAL(18, 2), nullable=False)

    # foreign key
    # with report_report_detail (one - to - one)
    report_id = Column(Integer,
                       ForeignKey('report.id'), unique=True)

    # relationships
    # with report_report_detail (one - to - one)
    report = relationship('Report', backref='detail')

    def __str__(self):
        return self.id


admin_rules = db.Table('admin_rules',
                       Column('admin_id', Integer,
                              ForeignKey(Admin.id), primary_key=True)
                       )

report_bills = db.Table('report_bills',
                        Column('report_id', Integer, ForeignKey(Report.id), primary_key=True),
                        Column('bill_id', Integer, ForeignKey(Bill.id), primary_key=True)
                        )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
