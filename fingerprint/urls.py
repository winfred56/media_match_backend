from django.urls import path
from . import views

app_name = 'fingerprint'

urlpatterns = [
    path('add/', views.add_media, name='audio_video_create'),
    path('find/', views.AudioVideoFileDetailView.as_view(), name='audio_video_detail'),
]
