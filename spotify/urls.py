from django.urls import path

from . import views


app_name = 'spotify'
urlpatterns = [
    path('', views.SpotifyIndex.as_view(), name='index'),
    path('callback/', views.SpotifyCallback.as_view(), name='callback'),
    path('current/', views.current, name="current"),
    path('loadplaylist/<str:uri>', views.load_playlist, name="loadpl"),
]