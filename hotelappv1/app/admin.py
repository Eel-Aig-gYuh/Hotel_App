
from app import db, app, dao
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import User, UserRole, Account, Room, Hotel, HotelLocation, Bed, Service, Feature, Rule
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app, name='Dream Hotel', template_mode='bootstrap4')

class Authenticated(ModelView):
    page_size = 5
    can_export = True
    column_display_pk = True
    can_view_details = True

    def is_accessible(self):
        return (current_user.is_authenticated
                and dao.get_role().__eq__(UserRole.ADMIN))


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class RuleView(Authenticated):
    pass

class RoomView(Authenticated):
    column_list = ('id', 'name', 'prices', 'room_status', 'room_style')

class BedView(Authenticated):
    pass

class FeatureView(Authenticated):
    pass

class HotelView(Authenticated):
    column_list = ('id', 'name', 'locations')

class HotelLocationView(Authenticated):
    pass

class UserView(Authenticated):
    pass

class ServiceView(Authenticated):
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
admin.add_view(RuleView(Rule, db.session))
admin.add_view(HotelView(Hotel, db.session))
admin.add_view(HotelLocationView(HotelLocation, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(BedView(Bed, db.session))
admin.add_view(FeatureView(Feature, db.session))
admin.add_view(ServiceView(Service, db.session))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
