
from app import db, app, dao
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import Room, RoomType, Service, Rule, Image, Hotel
from flask_login import current_user, logout_user
from flask import redirect


class Authenticated(ModelView):
    can_edit = True
    can_create = True
    can_delete = True
    page_size = 5
    can_export = True
    can_view_details = True

    def is_accessible(self):
        return (current_user.is_authenticated
                and (current_user.is_admin.__eq__(True)))


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class RuleView(Authenticated):
    column_list = ['id', 'name', 'value', 'staffs']

class RoomView(Authenticated):
    column_list = ['id', 'name', 'is_available', 'active', 'room_type_id', 'hotel_id']

class HotelView(Authenticated):
    column_list = ['id', 'name', 'address', 'phone', 'email', 'checkin_time', 'checkout_time', 'images', 'active']

class ImageView(Authenticated):
    column_list = ['id', 'uri']

class RoomTypeView(Authenticated):
    column_list = ['id', 'name', 'description', 'price_per_night', 'capacity', 'active', 'services', 'images']

class ServiceView(Authenticated):
    column_list = ['id', 'name', 'floor', 'start_time', 'end_time', 'description', 'active', 'images']

class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')

class StatsView(MyView):
    @expose("/")
    def __index__(self):

        return self.render('admin/stats.html')


admin = Admin(app, name='Dream Hotel', template_mode='bootstrap4')
admin.add_view(RoomTypeView(RoomType, db.session))
admin.add_views(ImageView(Image, db.session))
admin.add_view(ServiceView(Service, db.session))
admin.add_views(HotelView(Hotel, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(RuleView(Rule, db.session))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
