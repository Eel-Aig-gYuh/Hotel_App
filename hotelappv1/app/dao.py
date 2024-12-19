import hashlib

from django.utils.datetime_safe import datetime

from models import Room, User, Staff, Hotel, Customer, RoomType, Rule, Image, Service, Bill, BillDetail, Booking
from app import db, app
from flask_login import current_user


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


def add_booking_and_bill(cart):
    if not cart:
        raise ValueError("The cart is empty. Cannot proceed with booking and billing.")

    user_id = current_user.id  # Assume current_user is authenticated and provides ID
    customer = User.query.get(user_id)

    if not customer:
        raise ValueError(f"Customer with ID {user_id} not found.")

    try:
        for room_id, room_data in cart.items():
            room_id = int(room_data['room_id'])
            room_name = room_data['room_name']
            room_type_name = room_data['room_type_name']
            room_type_price_per_night = float(room_data['room_type_price_per_night'])
            checkin_date = room_data['checkin_date']
            checkout_date = room_data['checkout_date']
            is_foreign = room_data.get('is_foreign', 1)
            quantity = room_data.get('quantity', 1)

            # Validate room and dates
            room = Room.query.get(room_id)
            if not room:
                raise ValueError(f"Room with ID {room_id} not found.")

            stay_duration = calculate_stay_duration(room_data['checkin_date'], room_data['checkout_date'])
            if stay_duration <= 0:
                raise ValueError(f"Invalid check-in and check-out dates for room ID {room_id}.")

            # Calculate the total amount
            total_amount = room_type_price_per_night * quantity * stay_duration

            # Create a Booking object
            booking = Booking(
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                total=total_amount,
                customer_id=user_id,
                room_id=room_id
            )
            db.session.add(booking)
            db.session.flush()  # Ensure booking ID is generated

            # Create a Bill object
            bill = Bill(
                id=booking.id,  # Use the booking ID as the primary key for the Bill
                customer_id=user_id,
                payment_method="CHUYEN_KHOAN",  # Default payment method
                active=True
            )
            db.session.add(bill)
            db.session.flush()  # Ensure bill ID is generated

            # Create a BillDetail object
            bill_detail = BillDetail(
                bill_id=bill.id,
                room_id=room_id,
                amount=quantity,
                unit_price=room_type_price_per_night
            )
            db.session.add(bill_detail)

        # Commit all transactions to the database
        db.session.commit()
        print("Bookings and bills have been successfully created.")

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
        raise ValueError("An error occurred while processing bookings and bills.")


def load_room(kw=None, room_id=None, room_style=None, check_in=None, check_out=None, adult=None, children=None, room_in_cart=None, page=1):
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
        available_room = available_room.filter(RoomType.capacity>=(int(adult)+int(children)//2))

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
                                           .filter(RoomType.capacity>=(int(adult)+int(children)/2)))

    return room_types_with_available_rooms.all()

def load_hotel():
    return Hotel.query.order_by('id').all()

def load_img(type_img):
    img = Image.query.filter(Image.uri.contains(type_img)).all()
    return img

def load_service():
    service = db.session.query(Service).filter(Service.active==True).all()

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

def calculate_stay_duration(checkin_date_str, checkout_date_str):
    """
    Calculate the duration of stay in days.
    """
    try:
        # Try parsing with time and microseconds
        checkin_date = datetime.strptime(checkin_date_str, '%Y-%m-%d %H:%M:%S.%f')
        checkout_date = datetime.strptime(checkout_date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            # Fallback to just the date
            checkin_date = datetime.strptime(checkin_date_str, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout_date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")

    stay_duration = (checkout_date - checkin_date).days
    if stay_duration <= 0:
        raise ValueError("Invalid check-in and check-out dates. Checkout must be after check-in.")
    return stay_duration
