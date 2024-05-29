import json
import os
import subprocess
import tempfile
from time import time


from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.generics import *
from scipy.ndimage import iterate_structure, generate_binary_structure, maximum_filter, binary_erosion

from fingerprint.models import AudioVideoFile
from fingerprint.serializers import AudioVideoFileSerializer

from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import binary_erosion, generate_binary_structure, iterate_structure
import matplotlib.mlab as mlab
import numpy as np
import hashlib

from fingerprint.unsupported_file_formats import not_allowed_extensions


# Create your views here.
class AudioVideoFileDetailView(RetrieveAPIView):
    queryset = AudioVideoFile.objects.all()
    serializer_class = AudioVideoFileSerializer
    pass


@csrf_exempt
@api_view(['POST'])
def add_media(request):
    if request.method == 'POST':
        # Check for missing file
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file was submitted.'}, status=400)

        media_file = request.FILES['file']
        print(media_file)
        file_name = media_file.name
        file_extension = media_file.name.split('.')[-1].lower()
        if file_extension in not_allowed_extensions:
            print(file_extension)
            return JsonResponse({'error': 'Unsupported file format.'}, status=400)

        temp_file_path = None  # Initialize temp_file_path

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

                # Respond with extracted information
                return JsonResponse({'file_name': file_name, 'media_type': codec_type, 'metadata': metadata}, status=200)

            else:
                return JsonResponse({'error': 'Unsupported file format.'}, status=400)

        except Exception as e:
            print(str(e))
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            # Clean up: Remove the temporary file
            os.unlink(temp_file_path)

    else:
        return JsonResponse({'error': 'Expecting a POST request.'}, status=405)

