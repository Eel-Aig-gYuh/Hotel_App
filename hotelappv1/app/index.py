import datetime
import math
import json
import cloudinary
import cloudinary.uploader
import os

from flask import render_template, request, redirect, session, url_for, jsonify, flash
from app import dao, login, app
from flask_login import login_user, logout_user, current_user
from config import ROOM_TYPE_LABELS, BED_TYPE_LABELS, AREA_LABELS
from utils import cart_stats, format_date
from app import db, app
from models import User, Staff, Customer
from sqlalchemy import text
from datetime import timedelta


@app.context_processor
def common_response():
    return {
        'room': dao.load_room(),
        'room_type': dao.load_room_type(),
        'cart_stats': cart_stats(session.get('cart'))
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
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        account = dao.auth_user(username=username, password=password)

        if account:
            login_user(account)
            next = request.args.get('next')
            return redirect(url_for('index') if next is None else next)

    return render_template('layout/login.html')


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


# =============== phong nghi ===============
@app.route('/rooms/search_room', methods=['get', 'post'])
def search_process():
    kw = request.args.get('kw')
    room_id = request.args.get('room_type')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

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
                         check_out=checkout_date, page=page)

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
    room = dao.load_room(kw=kw, room_id=room_id, room_in_cart=cart, page=1)

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
    return render_template('layout/pay.html', ROOM_TYPE_LABELS=ROOM_TYPE_LABELS)


@app.route('/api/carts/<room_id>', methods=['delete'])
def delete_cart(room_id):
    cart = session.get('cart')
    if cart and room_id in cart:
        # muốn thay đổi gì ở đây cũng được, trong session.
        del cart[room_id]

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


@app.route('/delete-selected-rooms', methods=['POST'])
def delete_selected_rooms():
    data = request.get_json()
    rooms = data.get('rooms', [])

    if not rooms:
        return jsonify({"status": "error", "message": "No rooms selected"})

    try:
        # Đọc dữ liệu từ booking_history.json
        with open('data/booking_history.json', 'r', encoding='utf-8') as file:
            history_data = json.load(file)

        # Đọc dữ liệu từ rooms.json
        with open('data/rooms.json', 'r', encoding='utf-8') as rooms_file:
            room_data = json.load(rooms_file)

        # Các bước xử lý phòng cần xóa
        deleted_rooms = []
        for room in rooms:
            room_name = room.get('name')

            # Tìm phòng trong lịch sử booking
            delete_room = next((r for r in history_data if r['name'] == room_name), None)

            if delete_room:
                # Thêm phòng vào danh sách đã xóa
                deleted_rooms.append(delete_room)
                # Xóa phòng khỏi booking_history.json
                history_data = [r for r in history_data if r['name'] != room_name]

        # Nếu có phòng bị xóa, cập nhật file
        if deleted_rooms:
            # Cập nhật file rooms.json
            room_data.extend(deleted_rooms)

        return jsonify({
            "status": "success",
            "message": "Rooms deleted successfully",
            "reload": True  # Chỉ thị yêu cầu tải lại trang
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


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

    print(profile.first_name)

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



if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
