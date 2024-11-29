
from app import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import User, UserRole, Account, Room, Hotel, HotelLocation
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app, name='Dream Hotel', template_mode='bootstrap4')

def get_role():
    account = db.session.query(Account).filter_by(username=current_user.username).first()

    if account:
        return account.account_user.user_role

class Authenticated(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated
                and get_role().__eq__(UserRole.ADMIN))


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class RoomView(Authenticated):
    can_export = True


class HotelView(Authenticated):
    pass


class UserView(Authenticated):
    pass


class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(MyView):
    @expose("/")
    def __index__(self):

        return self.render('admin/stats.html')


admin.add_view(UserView(User, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(HotelView(Hotel, db.session))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
