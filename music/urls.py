from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("webcam/", views.webcam_page, name="webcam"),
    path("detect-emotion", views.detect_emotion, name="detect-emotion"),
    path("playlist/<str:mood>/", views.playlist, name="playlist"),
    path("api/songs/<str:mood>/", views.MoodSongListView.as_view(), name="song-list"),
]
