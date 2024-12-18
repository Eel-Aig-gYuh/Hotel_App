import math
import json
import os
import stripe
from flask import render_template, request, redirect, session, url_for, jsonify
from app import dao, login, app
from flask_login import login_user, logout_user, current_user
from models import UserRole, Room, RoomStyle, RoomStatus, db
from sqlalchemy.orm import joinedload
from urllib.parse import urlencode


@app.route("/")
def index():
    # đây là nơi lưu biến để gửi ra hiển thị ngoài màn hình.

    kw = request.args.get('kw')
    room_id = request.args.get('id')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

    rooms = dao.load_room(room_id=room_id, kw=kw, page=page)

    return render_template('index.html', room=rooms, pages=math.ceil(total / page_size))


@login.user_loader
def load_account(account_id):
    return dao.get_account_by_id(int(account_id))


@app.route('/rooms')
def rooms():
    with open('data/rooms.json', 'r', encoding='utf-8') as file:
        rooms_data = json.load(file)

    # Lọc ra các phòng có is_available = True
    available_rooms = [room for room in rooms_data if room.get('is_available', True)]
    return render_template('layout/rooms.html', rooms=available_rooms)


@app.route('/search_rooms', methods=['GET', 'POST'])
def search_rooms():
    # Lấy dữ liệu từ form
    room_style = request.args.get('room_style')  # Phòng
    check_in = request.args.get('check_in')  # Ngày đến
    check_out = request.args.get('check_out')  # Ngày đi
    adults = request.args.get('adults')  # Người lớn
    children = request.args.get('children')  # Trẻ em

    # Tạo query lọc
    query = Room.query.options(joinedload(Room.beds), joinedload(Room.images))

    # Lọc trạng thái phòng
    query = query.filter(Room.room_status == RoomStatus.CON_TRONG)

    # Lọc loại phòng
    if room_style and room_style != "Phòng":
        query = query.filter(Room.room_style == RoomStyle[room_style])

    # Thực hiện truy vấn
    rooms = query.all()

    # Kiểm tra nếu không có phòng nào thỏa mãn điều kiện
    if not rooms:
        no_rooms_message = "Không có phòng phù hợp với yêu cầu tìm kiếm của bạn."
    else:
        no_rooms_message = None

    return render_template('layout/rooms.html', rooms=rooms, no_rooms_message=no_rooms_message)


@app.route('/room_detail/<int:room_id>')
def room_detail(room_id):
    # Đọc danh sách phòng từ rooms.json
    with open('data/rooms.json', 'r', encoding='utf-8') as file:
        rooms_data = json.load(file)

    # Tìm phòng được xem
    roomdetail = None
    for room in rooms_data:
        if room['room_id'] == room_id:
            roomdetail = room
            break

    # Kiểm tra nếu không tìm thấy phòng, trả về thông báo lỗi
    if roomdetail is None:
        return "Room not found", 404

    # Truy cập các giá trị từ dictionary 'roomdetail'
    room_id = roomdetail['room_id']
    room_name = roomdetail['room_name']
    room_description = roomdetail['room_description']
    room_type = roomdetail['room_type']
    price_per_night = roomdetail['price_per_night']
    capacity = roomdetail['capacity']
    image = roomdetail['image']

    # Xử lý dữ liệu và trả về trang chi tiết phòng
    return render_template('layout/room_detail.html',
                           room_id=room_id,
                           room_name=room_name,
                           room_description=room_description,
                           room_type=room_type,
                           price_per_night=price_per_night,
                           capacity=capacity,
                           image=image)


# Route xử lý đặt phòng
@app.route('/book_room/<int:room_id>')
def book_room(room_id):
    # Đọc danh sách phòng từ rooms.json
    with open('data/rooms.json', 'r', encoding='utf-8') as file:
        rooms_data = json.load(file)

    # Tìm phòng được đặt
    room_to_book = None
    for room in rooms_data:
        if room['room_id'] == room_id:
            room_to_book = room
            break

    if room_to_book:
        # Cập nhật is_available từ True thành False
        room_to_book['is_available'] = False

        # Lưu lại dữ liệu đã thay đổi vào rooms.json
        with open('data/rooms.json', 'w', encoding='utf-8') as file:
            json.dump(rooms_data, file, ensure_ascii=False, indent=4)

        return redirect(url_for('rooms'))
    else:
        return "Phòng không tồn tại!", 404


@app.route('/pay')
def pay():
    with open('data/rooms.json', 'r', encoding='utf-8') as file:
        rooms_data = json.load(file)

    # Lọc ra các phòng có is_available = False
    unavailable_rooms = [room for room in rooms_data if not room.get('is_available', True)]  # Sửa điều kiện ở đây
    return render_template('layout/pay.html', booked_rooms=unavailable_rooms)


# Đọc dữ liệu từ file JSON
def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []


# Ghi dữ liệu vào file JSON
def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


@app.route('/delete-selected-rooms', methods=['POST'])
def delete_selected_rooms():
    data = request.get_json()
    print(data)  # In ra toàn bộ dữ liệu để kiểm tra
    roomss = data.get('rooms', [])  # Lấy danh sách phòng từ 'rooms'
    print(roomss)

    # Lấy danh sách room_id từ các phòng đã chọn (chuyển sang kiểu số nếu cần)
    rooms = [int(room['room_id']) for room in roomss]  # Chuyển room_id thành kiểu số nguyên
    print(rooms)  # In ra danh sách room_id

    if not rooms:
        return jsonify({"status": "error", "message": "No rooms selected"})

    try:
        # Đọc danh sách phòng từ rooms.json
        with open('data/rooms.json', 'r', encoding='utf-8') as file:
            rooms_data = json.load(file)

        rooms_updated = 0  # Biến đếm số phòng đã được cập nhật

        # Duyệt qua danh sách phòng đã chọn và cập nhật trạng thái
        for room_id in rooms:
            room_to_update = None
            for room in rooms_data:
                # Chuyển room_id trong rooms_data thành kiểu số nguyên nếu cần
                if room['room_id'] == room_id:
                    room_to_update = room
                    break

            if room_to_update:
                # Kiểm tra nếu phòng đang bị đặt (is_available == False) và cập nhật lại
                if room_to_update['is_available'] == False:
                    room_to_update['is_available'] = True
                    rooms_updated += 1  # Tăng biến đếm

        if rooms_updated > 0:
            # Lưu lại dữ liệu đã thay đổi vào rooms.json
            with open('data/rooms.json', 'w', encoding='utf-8') as file:
                json.dump(rooms_data, file, ensure_ascii=False, indent=4)

            return jsonify({
                "status": "success",
                "message": f"{rooms_updated} rooms updated successfully",
                "reload": True  # Chỉ thị yêu cầu tải lại trang
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No rooms were updated"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# @app.route('/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     try:
#         # Lấy dữ liệu phòng từ request
#         data = request.get_json()
#         selected_rooms = data.get('rooms', [])
#
#         # Đọc dữ liệu phòng từ JSON
#         with open('data/rooms.json', 'r', encoding='utf-8') as file:
#             rooms_data = json.load(file)
#
#         # Lọc phòng đã chọn
#         selected_room_details = [
#             room for room in rooms_data if str(room['room_id']) in [r['room_id'] for r in selected_rooms]
#         ]
#
#         # Tạo line_items cho Stripe
#         line_items = []
#         for room in selected_room_details:
#             line_items.append({
#                 'price_data': {
#                     'currency': 'vnd',
#                     'product_data': {
#                         'name': f"Phòng {room['room_name']}",
#                         'description': f"Loại phòng: {room['room_type']}, Giá: {room['price_per_night']} VND",
#                     },
#                     'unit_amount': int(room['price_per_night']),  # Đảm bảo là số nguyên
#                 },
#                 'quantity': 1,
#             })
#
#
#         # Tạo session thanh toán với Stripe
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=line_items,
#             mode='payment',
#             # success_url='http://localhost:5000/success',
#             # cancel_url='http://localhost:5000/cancel',
#             success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url = url_for('payment_cancel', _external=True)
#         )
#
#         return jsonify({'sessionId': session.id})
#
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'error': str(e)}), 400

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Lấy dữ liệu phòng từ request
        data = request.get_json()
        selected_rooms = data.get('rooms', [])

        # Đọc dữ liệu phòng từ JSON
        with open('data/rooms.json', 'r', encoding='utf-8') as file:
            rooms_data = json.load(file)

        # Lọc phòng đã chọn
        selected_room_details = [
            room for room in rooms_data if str(room['room_id']) in [r['room_id'] for r in selected_rooms]
        ]

        # Tạo line_items cho Stripe
        line_items = []
        for room in selected_room_details:
            line_items.append({
                'price_data': {
                    'currency': 'vnd',
                    'product_data': {
                        'name': f"Phòng {room['room_name']}",
                        'description': f"Loại phòng: {room['room_type']}, Giá: {room['price_per_night']} VND",
                    },
                    'unit_amount': int(room['price_per_night']),  # Đảm bảo là số nguyên
                },
                'quantity': 1,
            })

        # Chuẩn bị thông tin phòng cho success_url (chuyển qua query parameters)
        room_ids = [room['room_id'] for room in selected_room_details]
        room_names = [room['room_name'] for room in selected_room_details]

        # Tạo query string cho success_url
        query_params = urlencode({
            'room_ids': ','.join(map(str, room_ids)),  # Chuyển các room_id thành chuỗi
            'room_names': ','.join(room_names),  # Chuyển các room_name thành chuỗi
        })

        # Tạo session thanh toán với Stripe
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
    room_ids = request.args.get('room_ids', '')
    room_names = request.args.get('room_names', '')

    # Chuyển đổi room_ids và room_names thành danh sách
    room_ids_list = room_ids.split(',')
    room_names_list = room_names.split(',')

    # Xử lý tiếp với thông tin phòng
    return f"Thanh toán thành công cho các phòng: {', '.join(room_names_list)} (ID: {', '.join(room_ids_list)})"


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        account = dao.auth_account(username=username, password=password)
        if account:
            login_user(account)
            return redirect('/')

    return render_template('layout/login.html')


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    account = dao.auth_account(username=username, password=password, role=UserRole.ADMIN)
    if account:
        login_user(user=account)

    return redirect('/admin')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = None
    if request.method.__eq__('POST'):
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        avatar = request.files.get('avatar')
        dao.add_user(first_name=first_name, last_name=last_name, email=email, phone=phone, avatar=avatar)

        confirm = request.form.get('confirm')
        password = request.form.get('password')

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            dao.add_account(**data)

            # redirect: điều hướng qua trang khác.
            return redirect('/login')
        else:
            err_msg = 'Mật khẩu KHÔNG trùng khớp!'

    return render_template('register_account.html', err_msg=err_msg)


# trong trang chu
@app.route('/register_user', methods=['get', 'post'])
def register_user():
    err_msg = ''
    if request.method == 'POST':
        # Lấy thông tin từ form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Xử lý ảnh đại diện (avatar)
        avatar = request.files.get('avatar')

        try:
            # Gọi hàm add_user để thêm thông tin người dùng vào cơ sở dữ liệu
            dao.add_user(first_name=first_name, last_name=last_name,
                         email=email, phone=phone, avatar=avatar)

            return redirect('/register_account')  # Chuyển đến trang đăng ký tài khoản sau khi thêm thành công
        except Exception as e:
            err_msg = f"Đã có lỗi xảy ra: {e}"

    return render_template('layout/register_user.html', err_msg=err_msg)


# Route cho trang Đăng ký tài khoản
@app.route('/register_account', methods=['get', 'post'])
def register_account():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        user_id = 2

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']
            print(data)
            dao.add_account(**data, user_id=user_id)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp'

    return render_template('layout/register_account.html', err_msg=err_msg)


@app.context_processor
def common_response():
    return {
        'categories': dao.load_room()
    }


# Route cho trang Khách sạn
@app.route('/hotel')
def hotel():
    return render_template('layout/hotel.html')


# Route cho trang Cơ sở vật chất
@app.route('/facilities')
def facilities():
    return render_template('layout/facilities.html')


# Route cho trang Liên hệ
@app.route('/contact')
def contact():
    return render_template('layout/contact.html')


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
