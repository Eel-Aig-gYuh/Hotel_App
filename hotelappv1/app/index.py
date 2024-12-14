import math
import json
import os
from flask import render_template, request, redirect, session, url_for, jsonify
from app import dao, login, app
from flask_login import login_user, logout_user


@app.context_processor
def common_response():
    return {
        'room': dao.load_room()
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
            return redirect(url_for('index'))

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
    if request.method == 'POST':
        # Lấy thông tin từ form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cmnd = request.form.get('cmnd')

        if dao.check_email(email) is None:
            try:
                session['user_data'] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'cmnd': cmnd,
                    'email': email,
                    'phone': phone,
                }

                return redirect(url_for('register_account'))  # Chuyển đến trang đăng ký tài khoản sau khi thêm thành công
            except Exception as e:
                err_msg = f"Đã có lỗi xảy ra: {e}"
        else:
            err_msg = "Email đã tồn tại !"

    return render_template('layout/register_user.html', err_msg=err_msg)


# Route cho trang Đăng ký tài khoản
@app.route('/register_user/register_account', methods=['get', 'post'])
def register_account():
    err_msg = None

    # lấy dữ liệu được chuyển từ trang register_user.
    user_data = session.get('user_data')

    if not user_data:
        return redirect(url_for('register_user'))

    if request.method.__eq__('POST'):
        username = request.form.get('username').strip()
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
@app.route('/rooms')
def rooms():
    kw = request.args.get('kw')
    room_id = request.args.get('id')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

    room = dao.load_room(room_id=room_id, kw=kw, page=page)

    return render_template('layout/rooms.html', rooms=room, pages=math.ceil(total / page_size),)

@app.route('/search_rooms', methods=['GET', 'POST'])
def search_rooms():
    # Lấy dữ liệu từ form
    room_style = request.args.get('room_style')  # Phòng
    check_in = request.args.get('check_in')      # Ngày đến
    check_out = request.args.get('check_out')    # Ngày đi
    adults = request.args.get('adults')          # Người lớn
    children = request.args.get('children')      # Trẻ em

    # Tạo query lọc
    # query = Room.query.options(joinedload(Room.beds), joinedload(Room.images))

    # Lọc trạng thái phòng
    # query = query.filter(Room.room_status == RoomStatus.CON_TRONG)

    # Lọc loại phòng
    # if room_style and room_style != "Phòng":
    #     query = query.filter(Room.room_style == RoomStyle[room_style])

    # Thực hiện truy vấn
    rooms = dao.load_room()

    # Kiểm tra nếu không có phòng nào thỏa mãn điều kiện
    if not rooms:
        no_rooms_message = "Không có phòng phù hợp với yêu cầu tìm kiếm của bạn."
    else:
        no_rooms_message = None

    return render_template('layout/rooms.html', rooms=rooms, no_rooms_message=no_rooms_message)


@app.route('/room_detail/<string:room_name>/<string:room_note>/<string:room_level>/<int:room_price>/<string:area>/<string:bed>/<string:people>/<string:view>')
def room_detail(room_name, room_note, room_level, room_price, area, bed, people, view):
    # Xử lý dữ liệu và trả về trang chi tiết phòng
    return render_template('layout/room_detail.html',
                           room_name=room_name,
                           room_note=room_note,
                           room_level=room_level,
                           room_price=room_price,
                           area=area,
                           bed=bed,
                           people=people,
                           view=view)

# Route xử lý đặt phòng
@app.route('/book_room/<string:room_name>')
def book_room(room_name):
    # Đọc danh sách phòng từ rooms.json
    with open('data/rooms.json', 'r', encoding='utf-8') as file:
        rooms_data = json.load(file)

    # Tìm phòng được đặt
    room_to_book = None
    for room in rooms_data:
        if room['name'] == room_name:
            room_to_book = room
            break

    if room_to_book:
        # Ghi vào booking_history.json
        try:
            with open('data/booking_history.json', 'r', encoding='utf-8') as history_file:
                booking_history = json.load(history_file)
        except FileNotFoundError:
            booking_history = []

        booking_history.append(room_to_book)

        # Xóa phòng khỏi rooms.json
        rooms_data = [room for room in rooms_data if room['name'] != room_name]


        return redirect(url_for('rooms'))
    else:
        return "Phòng không tồn tại!", 404



# Route cho trang Đã đặt
@app.route('/pay')
def pay():
    with open('data/booking_history.json', 'r', encoding='utf-8') as file:
        book_rooms_data = json.load(file)
    return render_template('layout/pay.html', booked_rooms=book_rooms_data)

# Đọc dữ liệu từ file JSON
def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

# Ghi dữ liệu vào file JSON
def write_json_file(file_path, data):
    pass


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
def hotel():
    return render_template('layout/hotel.html', rooms=rooms)

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