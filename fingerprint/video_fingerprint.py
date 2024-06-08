# import io
# import hashlib
# from time import time
#
# import cv2
# from PIL import Image
#
# from fingerprint.audio_fingerprint import read_audio_file, generate_fingerprints
#
#
# def fingerprint_video_file(file_path):
#     """
#     Fingerprint the video file and return the fingerprint data.
#
#     :param file_path: Path to the video file.
#     :return: List of fingerprint hashes.
#     """
#     audio_channels, audio_fs, _ = read_audio_file(file_path)
#     video_frames = read_video_frames(file_path, audio_fs)
#
#     # Measure fingerprinting time
#     t_start = time()
#     fingerprints = set()  # Used a set to avoid duplicates
#     for channel in audio_channels:
#         audio_hashes = generate_fingerprints(channel, audio_fs)
#         combined_hashes = combine_hashes(audio_hashes, video_frames)
#         fingerprints.update(combined_hashes)  # Use update to add elements to the set
#     fingerprint_time = time() - t_start
#     print("fingerprint_time: ", fingerprint_time)
#
#     return list(fingerprints)  # Convert the set back to a list before returning
#
#
# # def read_video_frames(file_path, frame_rate, target_resolution=(128, 72)):
# #     """
# #     Read video frames, resize, and return a list of hashed frames.
# #
# #     :param file_path: Path to the video file.
# #     :param frame_rate: Frame rate to extract frames.
# #     :param target_resolution: Target resolution for resizing.
# #     :return: List of frame hashes.
# #     """
# #     cap = cv2.VideoCapture(file_path)
# #     frame_hashes = []
# #
# #     while cap.isOpened():
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
# #
# #         # Resize frame to target resolution
# #         resized_frame = cv2.resize(frame, target_resolution)
# #
# #         # Convert frame to grayscale
# #         gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
# #
# #         # Calculate hash for the frame
# #         frame_hash = hash_frame(gray_frame)
# #         frame_hashes.append(frame_hash)
# #
# #     cap.release()
# #     cv2.destroyAllWindows()
# #     return frame_hashes
#
# def read_video_frames(file_path, frame_rate, target_resolution=(128, 72)):
#     """
#     Read video frames, resize, and return a list of hashed frames.
#
#     :param file_path: Path to the video file.
#     :param frame_rate: Frame rate to extract frames.
#     :param target_resolution: Target resolution for resizing.
#     :return: List of frame hashes.
#     """
#     cap = cv2.VideoCapture(file_path)
#     frame_hashes = []
#     frame_interval = int(cap.get(cv2.CAP_PROP_FPS))  # Extract one frame per second
#
#     frame_count = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         # Extract frame at intervals
#         if frame_count % frame_interval == 0:
#             # Resize frame to target resolution
#             resized_frame = cv2.resize(frame, target_resolution)
#             # Convert frame to grayscale
#             gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
#             # Calculate hash for the frame
#             frame_hash = hash_frame(gray_frame)
#             frame_hashes.append(frame_hash)
#
#         frame_count += 1
#
#     cap.release()
#     cv2.destroyAllWindows()
#     return frame_hashes
#
#
# def hash_frame(frame):
#     """
#     Generate a unique hash for a video frame.
#
#     :param frame: Frame as a numpy array.
#     :return: Unique hash string.
#     """
#     img = Image.fromarray(frame)
#     buffer = io.BytesIO()
#     img.save(buffer, format="JPEG")
#     frame_bytes = buffer.getvalue()
#     return hashlib.sha1(frame_bytes).hexdigest()
#
#
# # def combine_hashes(audio_hashes, video_frames):
# #     """
# #     Combine audio hashes with corresponding video frame hashes.
# #
# #     :param audio_hashes: List of audio hashes.
# #     :param video_frames: List of video frame hashes.
# #     :return: List of combined hashes.
# #     """
# #     combined_hashes = []
# #     # print(f"Inside combine_hashes function: {len(audio_hashes)} audio hashes and {len(video_frames)} video frames")
# #
# #     # Determine the minimum length to prevent out of index errors
# #     min_length = min(len(audio_hashes), len(video_frames))
# #     # print(f"Min length for combining: {min_length}")
# #
# #     for i in range(min_length):
# #         audio_hash, timestamp = audio_hashes[i]
# #         video_frame_hash = video_frames[i % len(video_frames)]
# #         combined_hash = hashlib.sha1(f"{audio_hash}|{video_frame_hash}".encode('utf-8')).hexdigest()
# #         combined_hashes.append((combined_hash, timestamp))
# #
# #     return combined_hashes
# def combine_hashes(audio_hashes, video_frames):
#     """
#     Combine audio hashes with corresponding video frame hashes.
#
#     :param audio_hashes: List of audio hashes.
#     :param video_frames: List of video frame hashes.
#     :return: List of combined hashes.
#     """
#     combined_hashes = []
#     min_length = min(len(audio_hashes), len(video_frames))
#
#     for i in range(min_length):
#         audio_hash, timestamp = audio_hashes[i]
#         video_frame_hash = video_frames[i % len(video_frames)]
#         combined_hash = hashlib.sha1(f"{audio_hash}|{video_frame_hash}".encode('utf-8')).hexdigest()
#         combined_hashes.append((combined_hash, timestamp))
#
#     return combined_hashes
#
#
# def get_video_duration(file_path):
#     cap = cv2.VideoCapture(file_path)
#     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     duration_seconds = frame_count / fps
#     cap.release()
#     return duration_seconds
#


import io
import hashlib
from time import time
import cv2
from PIL import Image

from fingerprint.audio_fingerprint import read_audio_file, generate_fingerprints


def fingerprint_video_file(file_path, segment_length=1.0, overlap=0.5):
    """
    Fingerprint the video file and return the fingerprint data.

    :param file_path: Path to the video file.
    :param segment_length: Length of each segment in seconds.
    :param overlap: Overlap between segments in seconds.
    :return: List of fingerprint hashes.
    """
    audio_channels, audio_fs, _ = read_audio_file(file_path)
    video_frames = read_video_frames(file_path, audio_fs, segment_length, overlap)

    # Measure fingerprinting time
    t_start = time()
    fingerprints = set()  # Used a set to avoid duplicates
    for channel in audio_channels:
        audio_hashes = generate_fingerprints(channel, audio_fs)
        combined_hashes = combine_hashes(audio_hashes, video_frames)
        fingerprints.update(combined_hashes)  # Use update to add elements to the set
    fingerprint_time = time() - t_start
    print("fingerprint_time: ", fingerprint_time)

    print(fingerprints)
    return list(fingerprints)  # Convert the set back to a list before returning

def read_video_frames(file_path, frame_rate, segment_length=1.0, overlap=0.5, target_resolution=(128, 72)):
    """
    Read video frames, resize, and return a list of hashed frames.

    :param file_path: Path to the video file.
    :param frame_rate: Frame rate to extract frames.
    :param segment_length: Length of each segment in seconds.
    :param overlap: Overlap between segments in seconds.
    :param target_resolution: Target resolution for resizing.
    :return: List of frame hashes.
    """
    cap = cv2.VideoCapture(file_path)
    frame_hashes = []
    frame_interval = int(frame_rate * segment_length)
    overlap_interval = int(frame_rate * overlap)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Extract frame at intervals
        if frame_count % frame_interval < overlap_interval:
            # Resize frame to target resolution
            resized_frame = cv2.resize(frame, target_resolution)
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
            # Calculate hash for the frame
            frame_hash = hash_frame(gray_frame)
            frame_hashes.append(frame_hash)

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    return frame_hashes

def hash_frame(frame):
    """
    Generate a unique hash for a video frame.

    :param frame: Frame as a numpy array.
    :return: Unique hash string.
    """
    img = Image.fromarray(frame)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    frame_bytes = buffer.getvalue()
    return hashlib.sha1(frame_bytes).hexdigest()

def combine_hashes(audio_hashes, video_frames):
    """
    Combine audio hashes with corresponding video frame hashes.

    :param audio_hashes: List of audio hashes.
    :param video_frames: List of video frame hashes.
    :return: List of combined hashes.
    """
    combined_hashes = []
    min_length = min(len(audio_hashes), len(video_frames))

    for i in range(min_length):
        audio_hash, timestamp = audio_hashes[i]
        video_frame_hash = video_frames[i % len(video_frames)]
        combined_hash = hashlib.sha1(f"{audio_hash}|{video_frame_hash}".encode('utf-8')).hexdigest()
        combined_hashes.append((combined_hash, timestamp))

    return combined_hashes

def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration_seconds = frame_count / fps
    cap.release()
    return duration_seconds
