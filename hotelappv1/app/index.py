import math
import json
from flask import render_template, request, redirect, session
from app import dao, login, app
from flask_login import login_user, logout_user, current_user
from models import UserRole, Room, RoomStyle, RoomStatus, db
from sqlalchemy.orm import joinedload

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
    return render_template('layout/rooms.html', rooms=rooms_data)

@app.route('/search_rooms', methods=['GET', 'POST'])
def search_rooms():
    # Lấy dữ liệu từ form
    room_style = request.args.get('room_style')  # Phòng
    check_in = request.args.get('check_in')      # Ngày đến
    check_out = request.args.get('check_out')    # Ngày đi
    adults = request.args.get('adults')          # Người lớn
    children = request.args.get('children')      # Trẻ em

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


# Route cho trang Đã đặt
@app.route('/pay')
def pay():
    return render_template('layout/pay.html')


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
