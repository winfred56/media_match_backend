import gc
import json
import os
import subprocess
import tempfile
import threading

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from analytics.models import EndpointUsage
from fingerprint.audio_fingerprint import fingerprint_audio_file, get_audio_duration
from fingerprint.models import SegmentHash, AudioVideoFile
from fingerprint.recognize_audio import recognize_audio
from fingerprint.recognize_video import recognize_video
from fingerprint.serializers import AudioVideoFileSerializer
from fingerprint.unsupported_file_formats import not_allowed_extensions
from fingerprint.video_fingerprint import video_fingerprint, get_video_duration


# from fingerprint.video_fingerprint import fingerprint_video_file, get_video_duration


@csrf_exempt
@api_view(['GET'])
def welcome(request):
    try:
        return JsonResponse({'data': 'Welcome to media match'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        gc.collect()


@csrf_exempt
@api_view(['GET'])
def find(request):
    if 'file' not in request.FILES:
        log_endpoint_usage('find', 'failed', 'No file was submitted.')
        return JsonResponse({'error': 'No file was submitted.'}, status=400)

    media_file = request.FILES['file']
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in media_file.chunks():
            temp_file.write(chunk)

    temp_file_path = temp_file.name
    try:
        codec_type = None
        result_serialized = None
        metadata_command = f'ffprobe -v quiet -print_format json -show_format -show_streams "{temp_file_path}"'
        result = subprocess.run(metadata_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            log_endpoint_usage('find', 'failed', 'FFMpeg Failed to retrieve metadata.')
            return JsonResponse({'error': 'Failed to retrieve metadata.'}, status=500)

        metadata = json.loads(result.stdout)
        if metadata and 'streams' in metadata and len(metadata['streams']) > 0:
            first_stream = metadata['streams'][0]
            codec_type = first_stream.get('codec_type')
            print('codec_type: ', codec_type)

        if codec_type == 'video':
            result = recognize_video(temp_file_path)
        else:
            result = recognize_audio(temp_file_path)

        if result is not None:
            result_serialized = AudioVideoFileSerializer(result).data

        log_endpoint_usage('find', 'successful', json.dumps(result_serialized))
        return JsonResponse({
            'file': result_serialized,
        }, status=200)

    except Exception as e:
        log_endpoint_usage('find', 'failed', str(e))
        return JsonResponse({'error': str(e)}, status=500)

    finally:
        os.unlink(temp_file_path)
        gc.collect()  # Trigger garbage collection to free up memory


@csrf_exempt
@api_view(['POST'])
def add_media(request):
    if request.method == 'POST':
        # Check for missing file
        if 'file' not in request.FILES:
            log_endpoint_usage('add_media', 'failed', 'Expecting a POST request.')
            return JsonResponse({'error': 'No file was submitted.'}, status=400)

        media_file = request.FILES['file']

        temp_file_path = None  # Initialize temporary_file_path
        file_name = media_file.name
        file_extension = media_file.name.split('.')[-1].lower()
        if file_extension in not_allowed_extensions:
            print(f"Upload file as ${file_extension} file extension ")
            log_endpoint_usage('add_media', 'failed', 'No file was submitted.')
            return JsonResponse({'error': 'Unsupported file format.'}, status=400)

        try:
            # Save the file to a temporary location on disk
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in media_file.chunks():
                    temp_file.write(chunk)

            # Get the path to the temporary file
            temp_file_path = temp_file.name

            # Run ffprobe command to retrieve metadata
            metadata_command = f'ffprobe -v quiet -print_format json -show_format -show_streams "{temp_file_path}"'
            result = subprocess.run(metadata_command, shell=True, capture_output=True, text=True)

            # Incase an error occurred trying to run subprocess
            if result.returncode != 0:
                log_endpoint_usage('add_media', 'failed', 'FFMpeg Failed to retrieve metadata.')
                return JsonResponse({'error': 'Failed to retrieve metadata.'}, status=500)

            # Parse JSON output from ffprobe
            metadata = json.loads(result.stdout)
            if metadata != {}:
                codec_type = None
                # Accessing codec_type of the first stream (index 0)
                if 'streams' in metadata and isinstance(metadata['streams'], list) and len(metadata['streams']) > 0:
                    first_stream = metadata['streams'][0]
                    if 'codec_type' in first_stream:
                        codec_type = first_stream['codec_type']
                        print('uploaded file is a/an', codec_type)

                # Fingerprint the file in a separate thread
                threading.Thread(target=fingerprint_and_save, args=(temp_file_path, file_name, codec_type)).start()

                # Respond immediately
                log_endpoint_usage('add_media', 'successful', f'File name: {file_name}')
                return JsonResponse({
                    'file_name': file_name,
                }, status=200)
            else:
                log_endpoint_usage('add_media', 'failed', 'Unsupported file format.')
                return JsonResponse({'error': 'Unsupported file format.'}, status=400)

        except Exception as e:
            log_endpoint_usage('add_media', 'failed', str(e))
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            gc.collect()  # Trigger garbage collection to free up memory

    else:
        return JsonResponse({'error': 'Expecting a POST request.'}, status=405)


def fingerprint_and_save(temp_file_path, file_name, codec_type):
    try:
        # Fingerprint the file
        if codec_type == 'video':
            fingerprint_data = video_fingerprint(temp_file_path)
        else:
            fingerprint_data = fingerprint_audio_file(temp_file_path)

        # Save the audio file metadata to the database
        media_file = AudioVideoFile.objects.create(
            file_name=file_name,
            source=codec_type,
            duration_seconds=get_duration(codec_type, temp_file_path)
        )

        # Save the fingerprint hashes to the database
        save_fingerprints_to_db(fingerprint_data, media_file, codec_type == 'audio')

    except Exception as e:
        print(f"Error during fingerprinting and saving: {e}")

    finally:
        try:
            os.unlink(temp_file_path)
        except FileNotFoundError:
            pass
        gc.collect()  # Trigger garbage collection to free up memory


def get_duration(codec_type, file_path):
    # Check the file type based on its extension or other criteria
    if codec_type == 'video':
        # Video file, use OpenCV to get the duration
        return get_video_duration(file_path)
    else:
        # Audio file, use another function to get the duration
        return get_audio_duration(file_path)


def save_fingerprints_to_db(fingerprint_data, media_file, is_audio):
    try:
        segment_hashes = []
        for item in fingerprint_data:
            if is_audio:
                hash_value, start_time_seconds = item
                segment_hashes.append(SegmentHash(
                    audio_video_file=media_file,
                    hash_value=hash_value,
                ))
            else:
                features = item
                segment_hashes.append(SegmentHash(
                    audio_video_file=media_file,
                    features=','.join(map(str, features))
                ))
        SegmentHash.objects.bulk_create(segment_hashes, ignore_conflicts=True)
    except IntegrityError as e:
        print(f"Error occurred during bulk create: {e}")


def log_endpoint_usage(endpoint, status, data=None):
    EndpointUsage.objects.create(
        endpoint=endpoint,
        status=status,
        data=data,
        timestamp=timezone.now()
    )
# def save_fingerprints_to_db(fingerprint_data, audio_file):
#     try:
#         segment_hashes = []
#         for hash_value, start_time_seconds in fingerprint_data:
#             segment_hashes.append(SegmentHash.objects.create(
#                 audio_video_file=audio_file,
#                 hash_value=hash_value,
#                 start_time_seconds=start_time_seconds
#             ))
#         SegmentHash.objects.bulk_create(segment_hashes, ignore_conflicts=True)
#     except IntegrityError as e:
#         print(f"Error occurred during bulk create: {e}")
