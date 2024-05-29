# # Constants
# CONNECTIVITY_MASK = 2
# DEFAULT_AMP_MIN = 10
# DEFAULT_FS = 44100
# DEFAULT_OVERLAP_RATIO = 0.5
# DEFAULT_WINDOW_SIZE = 4096
# DEFAULT_FAN_VALUE = 5
# PEAK_NEIGHBORHOOD_SIZE = 10
# MIN_HASH_TIME_DELTA = 0
# MAX_HASH_TIME_DELTA = 200
# PEAK_SORT = True
# FINGERPRINT_REDUCTION = 20
#
#
# @csrf_exempt
# @api_view(['POST'])
# def add_media(request):
#     if request.method == 'POST':
#         # Check for missing file
#         if 'file' not in request.FILES:
#             return JsonResponse({'error': 'No file was submitted.'}, status=400)
#
#         media_file = request.FILES['file']
#         print(media_file)
#
#         temp_file_path = None  # Initialize temp_file_path
#
#         try:
#             # Save the file to a temporary location on disk
#             with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                 for chunk in media_file.chunks():
#                     temp_file.write(chunk)
#
#             # Get the path to the temporary file
#             temp_file_path = temp_file.name
#
#             # Run ffprobe command to retrieve metadata
#             metadata_command = f'ffprobe -v quiet -print_format json -show_format -show_streams "{temp_file_path}"'
#             result = subprocess.run(metadata_command, shell=True, capture_output=True, text=True)
#
#             # Incase an error occurred trying to run subprocess
#             if result.returncode != 0:
#                 return JsonResponse({'error': 'Failed to retrieve metadata.'}, status=500)
#
#             # Parse JSON output from ffprobe
#             metadata = json.loads(result.stdout)
#             if metadata != {}:
#                 codec_type = None
#                 # Accessing codec_type of the first stream (index 0)
#                 if 'streams' in metadata and isinstance(metadata['streams'], list) and len(metadata['streams']) > 0:
#                     first_stream = metadata['streams'][0]
#                     if 'codec_type' in first_stream:
#                         codec_type = first_stream['codec_type']
#
#                 # Fingerprint the audio file
#                 fingerprint_data = fingerprint_file(temp_file_path)
#
#                 print(fingerprint_data)
#                 print(len(fingerprint_data))
#                 # Respond with extracted information and fingerprint data
#                 return JsonResponse({
#                     'media_type': codec_type,
#                     'metadata': metadata,
#                     # 'fingerprint': fingerprint_data
#                 }, status=200)
#             else:
#                 return JsonResponse({'error': 'Unsupported file format.'}, status=400)
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#         finally:
#             # Clean up: Remove the temporary file
#             os.unlink(temp_file_path)
#
#     else:
#         return JsonResponse({'error': 'Expecting a POST request.'}, status=405)
#
#
# def fingerprint_file(file_path):
#     """
#     Fingerprint the audio file and return the fingerprint data.
#
#     :param file_path: Path to the audio file.
#     :return: List of fingerprint hashes.
#     """
#     channels, Fs, _ = read(file_path)
#
#     # Measure fingerprinting time
#     t_start = time()
#     fingerprints = []
#     for channel in channels:
#         fingerprints.extend(fingerprint(channel, Fs))
#     fingerprint_time = time() - t_start
#
#     return fingerprints
#
#
# def read(file_path, limit=None):
#     """
#     Read the audio file and return channels, sample rate, and file hash.
#
#     :param file_path: Path to the audio file.
#     :param limit: Optional limit in seconds.
#     :return: channels, sample rate, file hash.
#     """
#     from pydub import AudioSegment
#     import numpy as np
#
#     audiofile = AudioSegment.from_file(file_path)
#     if limit:
#         audiofile = audiofile[:limit * 1000]
#
#     data = np.frombuffer(audiofile.raw_data, np.int16)
#     channels = [data[chn::audiofile.channels] for chn in range(audiofile.channels)]
#
#     return channels, audiofile.frame_rate, unique_hash(file_path)
#
#
# def unique_hash(file_path, block_size=2**20):
#     """
#     Generate a unique hash for the file.
#
#     :param file_path: Path to the file.
#     :param block_size: Block size for reading the file.
#     :return: Unique hash string.
#     """
#     s = hashlib.sha1()
#     with open(file_path, "rb") as f:
#         while True:
#             buf = f.read(block_size)
#             if not buf:
#                 break
#             s.update(buf)
#     return s.hexdigest().upper()
#
#
# def fingerprint(channel_samples, Fs=DEFAULT_FS, wsize=DEFAULT_WINDOW_SIZE, wratio=DEFAULT_OVERLAP_RATIO,
#                 fan_value=DEFAULT_FAN_VALUE, amp_min=DEFAULT_AMP_MIN):
#     """
#     Fingerprint the channel samples and return hashes.
#
#     :param channel_samples: Channel samples.
#     :param Fs: Sampling rate.
#     :param wsize: Window size for FFT.
#     :param wratio: Overlap ratio.
#     :param fan_value: Fan value for hashing.
#     :param amp_min: Minimum amplitude for peaks.
#     :return: List of hashes.
#     """
#     arr2D = mlab.specgram(
#         channel_samples,
#         NFFT=wsize,
#         Fs=Fs,
#         window=mlab.window_hanning,
#         noverlap=int(wsize * wratio))[0]
#
#     arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))
#     local_maxima = get_2D_peaks(arr2D, amp_min=amp_min)
#
#     return generate_hashes(local_maxima, fan_value=fan_value)
#
#
# def get_2D_peaks(arr2D, amp_min=DEFAULT_AMP_MIN):
#     """
#     Get 2D peaks from the spectrogram matrix.
#
#     :param arr2D: Spectrogram matrix.
#     :param amp_min: Minimum amplitude for peaks.
#     :return: List of peak frequencies and times.
#     """
#     struct = generate_binary_structure(2, CONNECTIVITY_MASK)
#     neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)
#
#     local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
#     background = (arr2D == 0)
#     eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)
#
#     detected_peaks = local_max != eroded_background
#     amps = arr2D[detected_peaks]
#     freqs, times = np.where(detected_peaks)
#     amps = amps.flatten()
#     filter_idxs = np.where(amps > amp_min)
#     freqs_filter = freqs[filter_idxs]
#     times_filter = times[filter_idxs]
#
#     return list(zip(freqs_filter, times_filter))
#
#
# def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
#     """
#     Generate hashes from the peaks.
#
#     :param peaks: List of peak frequencies and times.
#     :param fan_value: Fan value for hashing.
#     :return: List of hashes.
#     """
#     if PEAK_SORT:
#         peaks.sort(key=lambda x: x[1])
#
#     hashes = []
#     for i in range(len(peaks)):
#         for j in range(1, fan_value):
#             if (i + j) < len(peaks):
#                 freq1 = peaks[i][0]
#                 freq2 = peaks[i + j][0]
#                 t1 = peaks[i][1]
#                 t2 = peaks[i + j][1]
#                 t_delta = t2 - t1
#
#                 if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
#                     h = hashlib.sha1(f"{freq1}|{freq2}|{t_delta}".encode('utf-8'))
#                     hashes.append((h.hexdigest()[0:FINGERPRINT_REDUCTION], t1))
#
#     return hashes
