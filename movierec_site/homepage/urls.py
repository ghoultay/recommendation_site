from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/profile/", views.profile, name="profile"),
    path("films/", views.films, name="films"),
    path('films/<int:id>/', views.film_detail, name='film_detail'),
    path('search/', views.search_film),
]