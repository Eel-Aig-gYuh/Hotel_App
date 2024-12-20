import hashlib

from models import Room, User, Staff, Hotel, Customer, RoomType, Rule, Image, Service, Bill, BillDetail, Booking
from app import db, app
from flask_login import current_user
from sqlalchemy import func
from flask import jsonify, request


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
    customer = Customer(id=get_user_by_username(username), first_name=first_name, last_name=last_name, email=email,
                        phone=phone, CMND=cmnd)
    db.session.add(customer)
    db.session.commit()


def add_bill(cart):
    if cart:
        bill = Bill(cus_bill=current_user)

        db.session.add(bill)

        for c in cart.value():
            detail = BillDetail(amount=c['quantity'], unit_price=c['room_type_price_per_night'],
                                booking_id=c['room_id'], bill_bill_detail=bill)
            db.session.add(detail)

        db.session.commit()


def load_room(kw=None, room_id=None, room_style=None, check_in=None, check_out=None, adult=None, children=None,
              room_in_cart=None, page=1):
    available_room = db.session.query(Room, RoomType).join(RoomType).filter(Room.is_available == True)

    if kw:
        available_room = available_room.filter(RoomType.name.contains(kw))

    if room_id:
        available_room = available_room.filter(Room.id.__eq__(room_id))

    if room_style:
        available_room = available_room.filter(RoomType.name.__eq__(room_style))

    if check_in:
        pass
    if check_out:
        pass

    if adult:
        available_room = available_room.filter(RoomType.capacity >= (int(adult) + int(children) // 2))

    if room_in_cart:
        available_room = available_room.filter(~Room.id.in_(room_in_cart))

    return available_room.all()


# khong xai
def load_categories():
    return RoomType.query.order_by('id').all()


# khong xai
def load_room_type(room_id=None, room_style=None, check_in=None, check_out=None, adult=None, children=None, page=1):
    room_types_with_available_rooms = (
        db.session.query(RoomType).order_by('id')
        .filter(RoomType.rooms.any(Room.is_available == True))  # Use backref to filter rooms
    )

    if room_id:
        room_types_with_available_rooms = room_types_with_available_rooms.filter(RoomType.id.__eq__(room_id))

    if room_style:
        room_types_with_available_rooms = room_types_with_available_rooms.filter(RoomType.name.__eq__(room_style))

    if check_in:
        pass

    if check_out:
        pass

    if adult:
        room_types_with_available_rooms = (room_types_with_available_rooms
                                           .filter(RoomType.capacity >= (int(adult) + int(children) / 2)))

    return room_types_with_available_rooms.all()


def load_hotel():
    return Hotel.query.order_by('id').all()


def load_img(type_img):
    img = Image.query.filter(Image.uri.contains(type_img)).all()
    return img


def load_service():
    service = db.session.query(Service).filter(Service.active == True).all()

    return service


def get_user_by_id(ids):
    return User.query.get(ids)


def get_user_by_username(username):
    return User.query.filter(User.username.__eq__(username)).first().id


def get_room_type_by_id(room_type_id):
    return RoomType.query.get(room_type_id)


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def get_hotel_by_id(hotel_id):
    return Hotel.query.get(hotel_id)


def pagination(page=1):
    query = Room.query.order_by('id')
    page_size = app.config['PAGE_SIZE']
    start = (int(page) - 1) * page_size

    return query.slice(start, start + page_size)


def count_rooms():
    return Room.query.count()


@app.route('/api/reports/revenue', methods=['GET'])
def report_revenue():
    try:
        month = int(request.args.get('month'))
        year = int(request.args.get('year'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid month or year"}), 400

    revenue_stats = db.session.query(
        RoomType.name.label('room_type'),
        func.sum(BillDetail.amount * BillDetail.unit_price).label('revenue'),
        func.count(BillDetail.booking_id).label('booking_count')
    ).join(Room, RoomType.id == Room.room_type_id) \
        .join(Booking, Room.id == Booking.room_id) \
        .join(BillDetail, Booking.id == BillDetail.booking_id) \
        .filter(func.month(Booking.checkin_date) == month, func.year(Booking.checkin_date) == year) \
        .group_by(RoomType.name).all()

    total_revenue = sum(row.revenue for row in revenue_stats)

    data = {
        "month": month,
        "year": year,
        "revenue_stats": [
            {
                "room_type": row.room_type,
                "revenue": row.revenue,
                "booking_count": row.booking_count,
                "percentage": round(row.revenue / total_revenue * 100, 2) if total_revenue > 0 else 0
            }
            for row in revenue_stats
        ],
        "total_revenue": total_revenue
    }
    print(data)
    return jsonify(data)


@app.route('/api/reports/usage', methods=['GET'])
def report_usage():
    try:
        month = int(request.args.get('month'))
        year = int(request.args.get('year'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid month or year"}), 400

    usage_stats = db.session.query(
        Room.name.label('room_name'),
        func.sum(func.datediff(Booking.checkout_date, Booking.checkin_date)).label('days_used')
    ).join(Booking, Room.id == Booking.room_id) \
        .filter(func.month(Booking.checkin_date) == month, func.year(Booking.checkin_date) == year) \
        .group_by(Room.name).all()

    total_days_used = sum(row.days_used for row in usage_stats)

    data = {
        "month": month,
        "year": year,
        "usage_stats": [
            {
                "room_name": row.room_name,
                "days_used": row.days_used,
                "percentage": round(row.days_used / total_days_used * 100, 2) if total_days_used > 0 else 0
            }
            for row in usage_stats
        ]
    }
    print(data)
    return jsonify(data)
