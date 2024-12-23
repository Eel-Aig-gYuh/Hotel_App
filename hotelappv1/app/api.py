import smtplib
import getpass

from flask import session

print('mail is sending!')
def send_email_success_for_booking(email_customer=None, room_name=None, room_type_name=None, checkin=None):
    email = 'giahuyle1030@gmail.com'
    password = ''
    email_sent = email_customer
    session = smtplib.SMTP('smtp.gmail.com', 587)
    # sẽ bật security để mở bảo mật gmail.
    session.starttls()
    session.login(email, password)
    # noi dung
    mail_content = f'''Subject: Quý khách vừa thanh toán đặt phòng thành công bên Dream Hotel
        Kính chào quý khách,

        Cảm ơn quý khách đã sử dụng dịch vụ bên chúng tôi.
        Quý khắch đã thanh toán thành công phòng {room_name} loại phòng {room_type_name}
        
        Quý khách vui lòng đến nhận phòng vào ngày {checkin}
        Quý khách vui lòng giữ mail để tiến hành xác thực khi nhận phòng ạ!

        Dream Hotel mong rằng quý khách sẽ có trải nghiệm tuyệt vời!

        Trân trọng.
        '''.encode("utf-8")
    session.sendmail(email, email_sent, mail_content)

