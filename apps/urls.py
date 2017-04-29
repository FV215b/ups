from django.conf.urls import url
from . import views
app_name = "apps"

urlpatterns = [
    url(r'^all_list/', views.home, name='home'),
    url(r'^tracking_detail/(?P<key>[0-9]+)', views.tracking_detail, name='tracking_detail'),
    url(r'^user_info/', views.user_info, name='user_info'),
    url(r'^change_destination/(?P<id>[0-9]+)', views.change_destination, name='change_destination'),
    url(r'^add_prime/(?P<id>[0-9]+)', views.add_prime, name='add_prime'),

    #connect to deamon
    url(r'^request_pickup', views.request_pickup, name='request_pickup'),
    url(r'^arrive_warehouse', views.arrive_warehouse, name='arrive_warehouse'),
    url(r'^request_load', views.request_load, name='request_load'),
]
