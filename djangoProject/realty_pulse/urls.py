from django.urls import path

from . import views
from .views import HomePageView, CityListView, CityDetailView

app_name = "realty_pulse"
urlpatterns = [

    path('login', views.LoginFormView.as_view(), name='login'),
    path('register', views.RegisterFormView.as_view(), name='register'),
    path('home/', HomePageView.as_view(), name='home'),
    path('cities/', CityListView.as_view(), name='city_list'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city_detail')

]