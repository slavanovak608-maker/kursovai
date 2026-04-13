from django.urls import path

from . import views

app_name = "tours"

urlpatterns = [
    path("", views.home, name="home"),
    path("putevki/", views.tour_list, name="list"),
    path("putevki/<str:slug>/", views.tour_detail, name="detail"),
    path("putevki/<str:slug>/bronirovanie/", views.tour_book, name="book"),
    path("zakaz/<int:pk>/oplata/", views.booking_pay, name="pay"),
    path("moi-zakazy/", views.my_bookings, name="my_bookings"),
    path("registracija/", views.register, name="register"),
    path("vhod/", views.SiteLoginView.as_view(), name="login"),
    path("vyhod/", views.SiteLogoutView.as_view(), name="logout"),
]
