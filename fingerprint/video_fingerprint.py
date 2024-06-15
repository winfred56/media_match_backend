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


# def video_fingerprint(video_path):
#     video = VideoFileClip(video_path)
#     fingerprints = set()
#
#     for i, frame in enumerate(video.iter_frames(fps=1)):  # Adjust fps as needed
#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         resized_frame = cv2.resize(gray_frame, (32, 32))  # Resize for faster processing
#         hash_value = sha256(resized_frame.tobytes()).hexdigest()
#         fingerprints.add((hash_value, i))  # Include the timestamp (frame number / fps)
#
#     return list(fingerprints)
#
#



import cv2
import numpy as np
from keras import Model
from keras.src.applications.vgg16 import preprocess_input, VGG16
from moviepy.editor import VideoFileClip


# from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
# from tensorflow.keras.models import Model


def extract_features_from_frame(frame, model):
    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Resize frame to the input size of the model
    resized_frame = cv2.resize(rgb_frame, (224, 224))
    # Preprocess the frame
    preprocessed_frame = preprocess_input(np.expand_dims(resized_frame, axis=0))
    # Extract features
    features = model.predict(preprocessed_frame)
    return features.flatten()


def video_fingerprint(video_path, fps=1):
    # Load pre-trained VGG16 model + higher level layers
    base_model = VGG16(weights='imagenet')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

    video = VideoFileClip(video_path)
    fingerprints = []

    for frame in video.iter_frames(fps=fps):
        features = extract_features_from_frame(frame, model)
        fingerprints.append(features)

    return np.array(fingerprints)


def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration_seconds = frame_count / fps
    cap.release()
    return duration_seconds
