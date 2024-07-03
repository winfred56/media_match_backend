from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from analytics.models import EndpointUsage
from analytics.serializers import EndpointUsageSerializer
from fingerprint.models import AudioVideoFile
from fingerprint.serializers import AudioVideoFileSerializer


@csrf_exempt
@api_view(['GET'])
def requests_per_month(request):
    now = timezone.now()
    start_of_year = now.replace(month=1, day=1)

    # Query the database for requests per month
    requests = EndpointUsage.objects.filter(timestamp__gte=start_of_year)
    requests_per_month = requests.annotate(month=TruncMonth('timestamp')).values('month').annotate(count=Count('id')).order_by('month')

    # Initialize the response data with all months set to zero
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    response_data = {month: 0 for month in months}

    # Update the response data with actual counts from the database
    for month in requests_per_month:
        month_name = month['month'].strftime('%B')
        response_data[month_name] = month['count']

    return JsonResponse(response_data, status=200)


@csrf_exempt
@api_view(['GET'])
def total_requests_current_year(request):
    now = timezone.now()
    start_of_year = now.replace(month=1, day=1)

    total_requests = EndpointUsage.objects.filter(timestamp__gte=start_of_year).count()
    return JsonResponse({'total_requests': total_requests}, status=200)


@csrf_exempt
@api_view(['GET'])
def find_requests_today(request):
    now = timezone.now()
    today = now.date()

    find_requests = EndpointUsage.objects.filter(endpoint='find', timestamp__date=today)
    serialized_requests = EndpointUsageSerializer(find_requests, many=True).data

    return JsonResponse({'find_requests_today': serialized_requests}, status=200)


@csrf_exempt
@api_view(['GET'])
def find_requests_last_week(request):
    now = timezone.now()
    last_week = now - timedelta(days=7)

    find_requests = EndpointUsage.objects.filter(endpoint='find', timestamp__gte=last_week)
    serialized_requests = EndpointUsageSerializer(find_requests, many=True).data

    return JsonResponse({'find_requests_last_week': serialized_requests}, status=200)


@csrf_exempt
@api_view(['GET'])
def add_requests_this_week(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())

    add_requests = EndpointUsage.objects.filter(endpoint='add_media', timestamp__gte=start_of_week)
    serialized_requests = EndpointUsageSerializer(add_requests, many=True).data

    return JsonResponse({'add_requests_this_week': serialized_requests}, status=200)


@csrf_exempt
@api_view(['GET'])
def failed_requests(request):
    failed_requests = EndpointUsage.objects.filter(status='failed')
    serialized_requests = EndpointUsageSerializer(failed_requests, many=True).data

    return JsonResponse({'failed_requests': serialized_requests}, status=200)


@csrf_exempt
@api_view(['GET'])
def average_requests_per_week(request):
    now = timezone.now()
    start_of_year = now.replace(month=1, day=1)
    num_weeks = (now - start_of_year).days // 7

    total_requests = EndpointUsage.objects.filter(timestamp__gte=start_of_year).count()
    average_requests_per_week = total_requests / num_weeks if num_weeks else 0

    return JsonResponse({'average_requests_per_week': average_requests_per_week}, status=200)


@csrf_exempt
@api_view(['GET'])
def top_matched_audios(request):
    top_audios = AudioVideoFile.objects.filter(source='audio').annotate(
        match_count=Count('segmenthash__hash_value')).order_by('-match_count')[:3]
    serialized_audios = AudioVideoFileSerializer(top_audios, many=True).data

    return JsonResponse({'top_matched_audios': serialized_audios}, status=200)


@csrf_exempt
@api_view(['GET'])
def top_matched_videos(request):
    top_videos = AudioVideoFile.objects.filter(source='video').annotate(
        match_count=Count('segmenthash__hash_value')).order_by('-match_count')[:3]
    serialized_videos = AudioVideoFileSerializer(top_videos, many=True).data

    return JsonResponse({'top_matched_videos': serialized_videos}, status=200)
