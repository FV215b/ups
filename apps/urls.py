from django.conf.urls import url
from . import views
app_name = "apps"

urlpatterns = [
    url(r'^all_list/', views.show_all_list, name='all_list'),
    url(r'^search/', views.search, name='search'),
]
