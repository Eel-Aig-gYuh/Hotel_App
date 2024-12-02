from flask import Flask, render_template, request, redirect, session
from app import dao, app
from models import User, UserRole


@app.route("/")
def index():
    # đây là nơi lưu biến để gửi ra hiển thị ngoài màn hình.

    return render_template('index.html')

# Route cho trang Đăng ký thông tin người dùng
@app.route('/register_user', methods=['GET', 'POST'])
def register_view():
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
def login():
    return render_template('layout/register_account.html')


# Route cho trang Phòng nghỉ
@app.route('/rooms')
def rooms():
    return render_template('layout/rooms.html')

# Route cho trang Đã đặt
@app.route('/pay')
def pay():
    return render_template('layout/pay.html')

# # Route cho trang Khách sạn
# @app.route('/hotel')
# def hotel():
#     return render_template('layout/hotel.html')
#
# # Route cho trang Cơ sở vật chất
# @app.route('/facilities')
# def facilities():
#     return render_template('layout/facilities.html')
#
# # Route cho trang Liên hệ
# @app.route('/contact')
# def contact():
#     return render_template('layout/contact.html')

if __name__ == '__main__':
    app.run(debug=True)
