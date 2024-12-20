import datetime
import math
import stripe
import cloudinary.uploader

from flask import render_template, request, redirect, session, url_for, jsonify, flash
from app import dao, login, app, db
from flask_login import login_user, logout_user, current_user, login_required
from config import ROOM_TYPE_LABELS, BED_TYPE_LABELS, AREA_LABELS, BOOKING_STATUS_LABELS
from utils import cart_stats, format_date
from urllib.parse import urlencode
from models import Staff, Customer, User


@app.context_processor
def common_response():
    return {
        'room': dao.load_room(),
        'room_type': dao.load_room_type(),
        'cart_stats': cart_stats(session.get('cart')),
    }


@login.user_loader
def load_account(user_id):
    return dao.get_user_by_id(int(user_id))


# =================== trang chu ===================
@app.route("/")
def index():
    # đây là nơi lưu biến để gửi ra hiển thị ngoài màn hình.
    images = dao.load_img("Carousel")

    return render_template('index.html', image=images)


# =================== login/logout ===================
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect(url_for('index'))


@app.route("/login", methods=['get', 'post'])
def login_process():
    err_msg = ''

    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        account = dao.auth_user(username=username, password=password)

        if account:
            login_user(account)
            next = request.args.get('next')
            return redirect(url_for('index') if next is None else next)

        else:
            err_msg = "Thông tin tài khoản hoặc mật khẩu không chính xác."

    return render_template('layout/login.html', err_msg=err_msg)


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    account = dao.auth_user(username=username, password=password, is_admin=True)
    if account:
        login_user(user=account)

    return redirect('/admin')


@app.route('/register_user', methods=['get', 'post'])
def register_user():
    err_msg = None
    cus_phone = None
    cus_email = None
    cus_cmnd = None
    if request.method == 'POST':
        # Lấy thông tin từ form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cmnd = request.form.get('cmnd')

        if phone:
            cus_phone = Customer.query.filter_by(phone=phone).all()

        if email:
            cus_email = Customer.query.filter_by(email=email).all()

        if cmnd:
            cus_cmnd = Customer.query.filter_by(CMND=cmnd).all()

        if cus_cmnd:
            print(f"CMND/CCCD đã tồn tại!")
            flash('CMND/CCCD đã tồn tại!', 'danger')
            return render_template('layout/register_user.html', messageCmnd="CMND/CCCD đã tồn tại!")

        if cus_email:
            print(f"Email đã tồn tại!")
            flash('Email đã tồn tại!', 'danger')
            return render_template('layout/register_user.html', messageEmail="Email đã tồn tại!")

        if cus_phone:
            print(f"Số điện thoại đã tồn tại!")
            flash('Số điện thoại đã tồn tại!', 'danger')
            return render_template('layout/register_user.html', messagePhone="Số điện thoại đã tồn tại!")

        if dao.check_email(email) is None:
            try:
                session['user_data'] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'cmnd': cmnd,
                    'email': email,
                    'phone': phone,
                }

                return redirect(
                    url_for('register_account'))  # Chuyển đến trang đăng ký tài khoản sau khi thêm thành công
            except Exception as e:
                err_msg = f"Đã có lỗi xảy ra: {e}"
        else:
            err_msg = "Email đã tồn tại !"

    return render_template('layout/register_user.html', err_msg=err_msg)


# Route cho trang Đăng ký tài khoản
@app.route('/register_user/register_account', methods=['get', 'post'])
def register_account():
    err_msg = None
    cus_username = None
    # lấy dữ liệu được chuyển từ trang register_user.
    user_data = session.get('user_data')

    if not user_data:
        return redirect(url_for('register_user'))

    if request.method.__eq__('POST'):
        username = request.form.get('username').strip()
        if username:
            cus_username = User.query.filter_by(username=username).all()

        if cus_username:
            print(f"Tên truy cập đã tồn tại!")
            flash('Tên truy cập đã tồn tại!', 'danger')
            return render_template('layout/register_account.html', messageUsername="Tên truy cập đã tồn tại!")

        password = request.form.get('password').strip()
        confirm = request.form.get('confirm').strip()

        if dao.check_user(username=username) is None:
            if password.__eq__(confirm):
                data = request.form.copy()
                del data['confirm']
                dao.add_user(**user_data, **data)

                return redirect(url_for('login_process'))
            else:
                err_msg = 'Mật khẩu không khớp !'
        else:
            err_msg = "Tên tài khoản đã tồn tại !"

    return render_template('layout/register_account.html', err_msg=err_msg)


# =============== profile ===============
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user
    profile = None
    staff_phone = None
    staff_email = None
    cus_phone = None
    cus_email = None

    # Kiểm tra loại người dùng
    if hasattr(user, 'cus_user'):
        profile = user.cus_user
    elif hasattr(user, 'staff_user'):
        profile = user.staff_user

    if not profile:
        flash('Không tìm thấy thông tin người dùng!', 'danger')
        return redirect(url_for('index'))

    profile = profile[0]

    print(current_user.cus_user[0].first_name)

    if request.method == 'POST':
        # Cập nhật thông tin từ form
        first_name = request.form.get('first_name', profile.first_name)
        last_name = request.form.get('last_name', profile.last_name)
        phone = request.form.get('phone', profile.phone)
        email = request.form.get('email', profile.email)
        avatar = request.files.get('avatar')

        if phone:
            staff_phone = Staff.query.filter_by(phone=phone).all()
            cus_phone = Customer.query.filter_by(phone=phone).all()

        if email:
            staff_email = Staff.query.filter_by(email=email).all()
            cus_email = Customer.query.filter_by(email=email).all()

        # Gán giá trị mới cho profile
        if profile.first_name.__eq__(first_name):
            pass
        else:
            profile.first_name = first_name

        if profile.last_name.__eq__(last_name):
            pass
        else:
            profile.last_name = last_name

        if profile.phone.__eq__(phone):
            pass
        else:
            if staff_phone or cus_phone:
                print(f"Số điện thoại bị trùng!")
                flash('Số điện thoại bị trùng!', 'danger')
                return render_template('layout/profile.html', user=user, profile=profile,
                                       messagePhone="Số điện thoại bị trùng!")
            else:
                profile.phone = phone

        if profile.email.__eq__(email):
            pass
        else:
            if staff_email or cus_email:
                print(f"Email bị trùng!")
                flash('Email bị trùng!', 'danger')
                return render_template('layout/profile.html', user=user, profile=profile,
                                       messageEmail="Email bị trùng!")
            else:
                profile.email = email

        # Upload avatar nếu có
        if avatar:
            upload_result = cloudinary.uploader.upload(avatar)
            profile.avatar = upload_result['secure_url']

        try:
            db.session.commit()
            flash('Thông tin cá nhân đã được cập nhật!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi: {e}")
            flash('Cập nhật thông tin thất bại!', 'danger')

        return redirect(url_for('profile'))

    return render_template('layout/profile.html', user=user, profile=profile)


# =============== phong nghi ===============
@app.route('/rooms/search_room', methods=['get', 'post'])
def search_process():
    kw = request.args.get('kw')
    room_id = request.args.get('room_type')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

    cart = session.get('cart')
    room_style = request.args.get('room_style')  # Phòng
    check_in = request.args.get('check_in')  # Ngày đến
    check_out = request.args.get('check_out')  # Ngày đi
    adults = request.args.get('adults')  # Người lớn
    children = request.args.get('children')  # Trẻ em

    if not check_in or not check_out:
        flash("Please provide both check-in and check-out dates.", "warning")
        return redirect(url_for('room_process'))

    checkin_date = format_date(check_in)
    checkout_date = format_date(check_out)

    if check_in >= check_out:
        flash("Check-out date must be after check-in date.", "warning")
        return redirect(url_for('room_process'))

    room = dao.load_room(room_id=room_id,
                         room_style=room_style, adult=adults, children=children, check_in=checkin_date,
                         check_out=checkout_date, page=page, room_in_cart=cart)

    # Kiểm tra nếu không có phòng nào thỏa mãn điều kiện
    if room:
        no_rooms_message = None
        try:
            session['search_state'] = {
                'room_style': room_style,
                'check_in': check_in,
                'check_out': check_out,
                'adults': adults,
                'children': children,
            }
        except Exception as e:
            err_msg = f"Đã có lỗi xảy ra: {e}"
    else:
        no_rooms_message = "Không có phòng phù hợp với yêu cầu tìm kiếm của bạn."

    return render_template('layout/rooms.html',
                           rooms=room, pages=math.ceil(total / page_size),
                           checkin=checkin_date, checkout=checkout_date,
                           ROOM_TYPE_LABELS=ROOM_TYPE_LABELS,
                           BED_TYPE_LABELS=BED_TYPE_LABELS,
                           no_rooms_message=no_rooms_message)


@app.route('/rooms', methods=['get', 'post'])
def room_process():
    kw = request.args.get('kw')
    room_id = request.args.get('room_type')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

    check_in = request.form.get('check_in', datetime.datetime.now())
    check_out = request.form.get('check_out', (datetime.datetime.now() + datetime.timedelta(days=1)))

    cart = session.get('cart')
    print(cart)

    # room = dao.load_room_type(room_id=room_id, check_in=check_in, check_out=check_out, page=page)
    room = dao.load_room(kw=kw, room_id=room_id, room_in_cart=cart, check_in=check_in, check_out=check_out, page=1)

    # Kiểm tra nếu không có phòng nào thỏa mãn điều kiện
    if room:
        no_rooms_message = None
    else:
        no_rooms_message = "Không có phòng phù hợp với yêu cầu tìm kiếm của bạn."

    return render_template('layout/rooms.html',
                           rooms=room, pages=math.ceil(total / page_size),
                           checkin=check_in if check_in else "checkin",
                           checkout=check_out if check_out else "checkout",
                           ROOM_TYPE_LABELS=ROOM_TYPE_LABELS,
                           BED_TYPE_LABELS=BED_TYPE_LABELS,
                           no_rooms_message=no_rooms_message)


@app.route(
    '/rooms/room_detail/<int:room_id>/<string:room_name>/<string:room_style>/<int:room_price>/<int:room_capacity>/<checkin>/<checkout>',
    methods=['get'])
def room_detail(room_id, room_name, room_style, room_price, room_capacity, checkin, checkout):
    # Xử lý dữ liệu và trả về trang chi tiết phòng
    room = dao.get_room_by_id(room_id)

    room_available = dao.load_room(room_id=room.id)

    _, room_type = room_available[0]

    # book_rooms = dao.load_is_book_of_user()
    # booking_data = []
    # for bill_book, bill_room, bill_room_type in book_rooms:
    #     booking_data.append({
    #         'booking_id': bill_book.id,
    #         'room_id': bill_room.id,
    #         'room_name': bill_room.name,
    #         'room_type': bill_room_type.name,
    #         'checkin_date': bill_book.checkin_date.strftime('%d-%m-%Y'),
    #         'checkout_date': bill_book.checkout_date.strftime('%d-%m-%Y'),
    #         'price_per_night': bill_room_type.price_per_night,
    #         'status': bill_book.status
    #     })


    # print(booking_data)


    comments = dao.load_comment(room_type.id)
    # print(room.id)
    # print(room_available)
    # print(room_type.name)

    return render_template('layout/room_detail.html',
                           room_id=room.id,
                           room_name=room.name,
                           room_style=room_type.name,
                           room_available=room_available,
                           room_price=room_type.price_per_night,
                           room_capacity=room_type.capacity,
                           checkin=checkin,
                           checkout=checkout,
                           images=room_type.images,
                           comments=comments,
                           room_type_id=room_type.id,
                           ROOM_TYPE_LABELS=ROOM_TYPE_LABELS,
                           BED_TYPE_LABELS=BED_TYPE_LABELS,
                           AREA_LABELS=AREA_LABELS)


# Route xử lý đặt phòng
@app.route('/book_room/<string:room_name>')
def book_room(room_name):
    return redirect(url_for('room_process'))


# Route cho trang Đã đặt
@app.route('/api/carts', methods=['post'])
def add_to_cart():
    # lấy giỏ trong session.
    cart = session.get('cart')

    if not cart:
        cart = {}

    room_id = str(request.json.get('room_id'))
    room_name = request.json.get('room_name')
    room_type_name = request.json.get('room_type_name')
    room_type_price_per_night = request.json.get('room_type_price_per_night')
    room_type_capacity = request.json.get('room_type_capacity')
    checkin_date = request.json.get('checkin_date')
    checkout_date = request.json.get('checkout_date')
    is_foreign = request.json.get('is_foreign')

    if room_id in cart:
        cart[room_id]['quantity'] = int(cart[room_id]['quantity']) + 1
    else:
        cart[room_id] = {
            "room_id": room_id,
            "room_name": room_name,
            "room_type_name": room_type_name,
            "room_type_price_per_night": room_type_price_per_night,
            "room_type_capacity": room_type_capacity,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "is_foreign": 1,
            "quantity": 1
        }

    session['cart'] = cart

    return jsonify(
        cart_stats(cart)
    )


@app.route('/pay')
def pay_process():
    book_room_is_paid = dao.load_is_book_of_user()

    booking_data = []
    for booking, room, room_type in book_room_is_paid:
        booking_data.append({
            'room_name': room.name,
            'room_type': room_type.name,
            'checkin_date': booking.checkin_date.strftime('%d-%m-%Y'),
            'checkout_date': booking.checkout_date.strftime('%d-%m-%Y'),
            'price': room_type.price_per_night,
            'status': booking.status
        })

    return render_template('layout/pay.html',
                           ROOM_TYPE_LABELS=ROOM_TYPE_LABELS, BOOKING_STATUS_LABELS=BOOKING_STATUS_LABELS,
                           book_rooms=booking_data)


@app.route('/api/carts/<room_id>', methods=['delete'])
def delete_cart(room_id):
    cart = session.get('cart')
    if cart and room_id in cart:
        # muốn thay đổi gì ở đây cũng được, trong session.
        del cart[str(room_id)]

        session.modified = True

    session['cart'] = cart

    return jsonify(cart_stats(cart))

@app.route('/api/carts/<room_id>', methods=['put'])
def update_cart(room_id):
    quantity = request.json.get('quantity', 0)

    cart = session.get('cart')
    if cart and room_id in cart:
        # muốn thay đổi gì ở đây cũng được, trong session.
        cart[room_id]['quantity'] = int(quantity)

    session['cart'] = cart

    return jsonify(cart_stats(cart))

@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    data = request.json
    selected_room_ids = data.get('selected_room_ids', [])

    if not selected_room_ids:
        return jsonify({'status': 400, 'err_msg': 'Vui lòng chọn ít nhất một phòng để thanh toán.'})

    cart = session.get('cart', {})
    selected_rooms = {room_id: room for room_id, room in cart.items() if str(room_id) in selected_room_ids}

    if not selected_rooms:
        return jsonify({'status': 400, 'err_msg': 'Không có phòng hợp lệ được chọn.'})

    try:
        # Process selected rooms for booking and bill generation
        dao.add_booking_and_bill(selected_rooms)

        # Remove selected rooms from the cart
        for room_id in selected_room_ids:
            cart.pop(room_id, None)

        session['cart'] = cart
        return jsonify({'status': 200, 'msg': 'Thanh toán thành công!'})
    except Exception as ex:
        print(str(ex))
        room_names = ', '.join([room.get('name', f'Room ID {room['room_name']}') for room_id, room in selected_rooms.items()])
        return jsonify({'status': 500, 'err_msg': f'Phòng hiện tại {room_names} không có sẵn, vui lòng chọn phòng khác !'})


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Get cart data
        cart = request.get_json()
        print(f"Received cart: {cart} (Type: {type(cart)})")

        # Handle improperly sent JSON string
        if isinstance(cart, str):
            import json
            cart = json.loads(cart)

        # Validate cart format
        if not isinstance(cart, list) or not all(isinstance(room, dict) for room in cart):
            raise ValueError("Invalid cart format. Expected a list of dictionaries.")

        # Create line_items for Stripe
        line_items = []
        for room in cart:
            print(f"Processing room: {room}")
            line_items.append({
                'price_data': {
                    'currency': 'vnd',
                    'product_data': {
                        'name': f"Phòng {room['room_name']}",
                        'description': f"Loại phòng: {room['room_type_name']}, Giá: {room['room_type_price_per_night']} VND",
                    },
                    'unit_amount': int(room['room_type_price_per_night']),
                },
                'quantity': 1,
            })

        # Prepare room details for success_url
        room_ids = [room['room_id'] for room in cart]
        room_names = [room['room_name'] for room in cart]

        # Create query string for success_url
        query_params = urlencode({
            'room_ids': ','.join(map(str, room_ids)),
            'room_names': ','.join(room_names),
        })

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', _external=True) + '?' + query_params,
            cancel_url=url_for('pay', _external=True)
        )

        return jsonify({'sessionId': session.id})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/payment-success')
def payment_success():
    # Lấy thông tin phòng từ query parameters
    room_id = request.args.get('room_id', '')
    room_name = request.args.get('room_name', '')

    # Chuyển đổi room_ids và room_names thành danh sách
    room_id_list = room_id.split(',')
    room_name_list = room_name.split(',')

    # Xử lý tiếp với thông tin phòng
    return f"Thanh toán thành công cho các phòng: {', '.join(room_name_list)} (ID: {', '.join(room_id_list)})"

@app.route(
    '/rooms/room_detail/<int:room_id>/<string:room_name>/<string:room_style>/<int:room_price>/<int:room_capacity>/<checkin>/<checkout>/comments',
    methods=['post']
)
@login_required
def add_comment(room_id, room_name, room_style, room_price, room_capacity, checkin, checkout):
    room_type = dao.get_room_by_id(room_id)

    comment = dao.add_comment(content=request.json.get('content'), room_type_id=room_type.room_type_id)

    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at,
        "user": {
            "avatar": comment.cus_cmt.avatar
        }
    })

# Route cho trang Khách sạn
@app.route('/hotel')
def hotel_process():
    hotel = dao.load_hotel()

    return render_template('layout/hotel.html', hotels=hotel)


# Route cho trang Cơ sở vật chất
@app.route('/facilities')
def facilities():
    service = dao.load_service()
    img_service = dao.load_img("CoSoVatChat")

    return render_template('layout/facilities.html', services=service, images=img_service)


# Route cho trang Liên hệ
@app.route('/contact')
def contact():
    return render_template('layout/contact.html')


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
