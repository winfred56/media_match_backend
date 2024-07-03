from django.urls import path
from .views import (
    requests_per_month,
    total_requests_current_year,
    find_requests_today,
    find_requests_last_week,
    add_requests_this_week,
    failed_requests,
    average_requests_per_week,
    top_matched_audios,
    top_matched_videos
)

app_name = 'analytics'

urlpatterns = [
    path('requests-per-month/', requests_per_month, name='requests_per_month'),
    path('total-requests-current-year/', total_requests_current_year, name='total_requests_current_year'),
    path('find-requests-today/', find_requests_today, name='find_requests_today'),
    path('find-requests-last-week/', find_requests_last_week, name='find_requests_last_week'),
    path('add-requests-this-week/', add_requests_this_week, name='add_requests_this_week'),
    path('failed-requests/', failed_requests, name='failed_requests'),
    path('average-requests-per-week/', average_requests_per_week, name='average_requests_per_week'),
    path('top-matched-audios/', top_matched_audios, name='top_matched_audios'),
    path('top-matched-videos/', top_matched_videos, name='top_matched_videos'),
]
