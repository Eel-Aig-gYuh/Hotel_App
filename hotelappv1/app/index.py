import math
from flask import render_template, request, redirect, session
from app import dao, login, app
from flask_login import login_user, logout_user, current_user
from models import UserRole


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


# Route cho trang Phòng nghỉ
@app.route('/rooms')
def rooms():
    kw = request.args.get('kw')
    room_id = request.args.get('id')
    page = request.args.get('page', 1)
    page_size = app.config.get('PAGE_SIZE', app.config['PAGE_SIZE'])
    total = dao.count_rooms()

    rooms = dao.load_room(room_id=room_id, kw=kw, page=page)

    return render_template('layout/rooms.html', rooms=rooms, pages=math.ceil(total / page_size))


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

            return redirect('layout/login.html')
        else:
            err_msg = 'Mật khẩu không khớp'

    return render_template('layout/register_account.html', err_msg=err_msg)


@app.context_processor
def common_response():
    return {
        'categories': dao.load_room()
    }


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
