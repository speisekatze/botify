from django.urls import path

from . import views


app_name = 'spotify'
urlpatterns = [
    path('', views.SpotifyIndex.as_view(), name='index'),
    path('callback/', views.SpotifyCallback.as_view(), name='callback'),
]