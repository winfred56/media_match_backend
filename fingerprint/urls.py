from django.urls import path

from . import views

app_name = 'fingerprint'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    # Add new media files to database
    path('add/', views.add_media, name='audio_video_create'),
    # Search database to find a media that matches one from request body
    path('find/', views.find, name='audio_video_detail'),
    # Provides insight on api usage
    path('analytics/', views.analytics, name='analytics'),
]
