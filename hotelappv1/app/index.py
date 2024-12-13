import math
from flask import render_template, request, redirect, session
from app import dao, login, app
from flask_login import login_user, logout_user
from models import Room
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
    return dao.get_user_by_id(int(account_id))


# Route cho trang Phòng nghỉ
@app.route('/rooms', methods=['get', 'post'])
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
    # query = query.filter(Room.room_status == RoomStatus.CON_TRONG)
    #
    # # Lọc loại phòng
    # if room_style and (room_style in RoomStyle.__members__):
    #     query = query.filter(Room.room_style == RoomStyle[room_style])

    # Thực hiện truy vấn
    room = query.all()

    # Kiểm tra nếu không có phòng nào thỏa mãn điều kiện
    no_rooms_message = None
    if not room:
        no_rooms_message = "Không có phòng phù hợp với yêu cầu tìm kiếm của bạn."

    return render_template('layout/rooms.html', rooms=room, no_rooms_message=no_rooms_message)


# Route cho trang Chi tiết phòng
@app.route('/room_detail')
def room_detail():
    return render_template('layout/room_detail.html')

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

        account = dao.auth_user(username=username, password=password)
        if account:
            login_user(account)
            return redirect('/')

    return render_template('layout/login.html')


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    account = dao.auth_user(username=username, password=password, is_admin=True)

    if account:
        login_user(account)

    return redirect('/admin')


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
        # avatar = request.files.get('avatar')
        avatar = request.form.get('avatar')
        
        try:
            session['user_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'avatar': avatar
            }

            return redirect('/register_account')  # Chuyển đến trang đăng ký tài khoản sau khi thêm thành công
            
        except Exception as e:
            err_msg = f"Đã có lỗi xảy ra: {e}"

    return render_template('layout/register_user.html', err_msg=err_msg)


# Route cho trang Đăng ký tài khoản
@app.route('/register_account', methods=['get', 'post'])
def register_account():
    err_msg = None

    # lấy dữ liệu được chuyển từ trang register_user.
    user_data = session.get('user_data')

    if not user_data:
        return redirect('/register_user')

    if request.method.__eq__('POST'):
        print(user_data)
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']
            print(data)
            dao.add_user(**user_data, **data)


            return redirect('login')

        else:
            err_msg = 'Mật khẩu không khớp'

    return render_template('layout/register_account.html', err_msg=err_msg)


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


@app.context_processor
def common_response():
    return {
        'categories': dao.load_room()
    }


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
