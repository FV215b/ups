from django.conf.urls import url
from . import views
app_name = "apps"

urlpatterns = [
    url(r'^all_list/', views.home, name='home'),
    url(r'^search/(?P<key>[0-9]+)', views.search, name='search'),
]
