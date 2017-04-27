from django.conf.urls import url
from . import views
app_name = "accounts"
urlpatterns = [
    url(r'^signup/', views.signup, name='SignUp'),
    url(r'^login/', views.Login, name='Login'),
    url(r'^logout/', views.Logout, name='Logout'),
    url(r'^account_detail/', views.account_detail, name='account_detail'),
    url(r'^charge_account/', views.charge_account, name='charge_account'),
]
