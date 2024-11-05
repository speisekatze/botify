from django.urls import path

from . import views


app_name = 'spotify'
urlpatterns = [
    path('', views.SpotifyIndex.as_view(), name='index'),
    path('callback/', views.SpotifyCallback.as_view(), name='callback'),
    path('current/', views.current, name="current"),
    path('loadplaylist/<str:uri>', views.load_playlist, name="loadpl"),
    path('delete_playlist/<str:uri>', views.delete_playlist, name="deletepl"),
    path('delete_track_from_playlist/<str:playlist>/<str:track>', views.delete_track_from_playlist, name="deletetfpl"),
]