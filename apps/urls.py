from django.conf.urls import url
from . import views
app_name = "apps"

urlpatterns = [
    url(r'^all_list/', views.home, name='home'),
    url(r'^tracking_detail/(?P<key>[0-9]+)', views.tracking_detail, name='tracking_detail'),
    url(r'^user_info/', views.user_info, name='user_info'),
    url(r'^change_destination/(?P<id>[0-9]+)', views.change_destination, name='change_destination'),
]
