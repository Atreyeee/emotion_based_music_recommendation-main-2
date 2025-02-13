from django.urls import path
from . import views
from django.views.generic import RedirectView
from .views import *

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('webcam/',views.webcam_page,name='webcam'),
    path('neutral_playlist/',views.neutral_playlist, name='neutral_playlist'),
    path("detect-emotion", views.detect_emotion, name="detect-emotion"),
    path('upload-image/', views.upload_image, name='upload-image'),
    path('video_stream/', views.video_stream, name='video_stream'),
    path('happy_playlist/',views.happy_playlist, name='happy_playlist'),
    path('sad_playlist/',views.sad_playlist, name='sad_playlist'),
    path('fear_playlist/',views.fear_playlist, name='fear_playlist'),
    path('angry_playlist/',views.angry_playlist, name='angry_playlist'),
    path('surprise_playlist/',views.surprise_playlist, name='surprise_playlist'),
    path('api/songs/', NeutralSongListView.as_view(), name='song-list'),
    path('api/songs/', HappySongListView.as_view(), name='song-list'),
    path('api/songs/', AngrySongListView.as_view(), name='song-list'),
    path('api/songs/', FearSongListView.as_view(), name='song-list'),
    path('api/songs/', SadSongListView.as_view(), name='song-list'),
    path('api/songs/', SurpriseSongListView.as_view(), name='song-list'),
]

