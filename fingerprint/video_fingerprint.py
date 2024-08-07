import hashlib
import io

import cv2
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip


def read_video_frames(file_path, frame_rate, target_resolution=(128, 72)):
    """
    Read video frames, resize, and return a list of hashed frames.

    :param file_path: Path to the video file.
    :param frame_rate: Frame rate to extract frames.
    :param target_resolution: Target resolution for resizing.
    :return: List of frame hashes.
    """
    cap = cv2.VideoCapture(file_path)
    frame_hashes = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to target resolution
        resized_frame = cv2.resize(frame, target_resolution)

        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Calculate hash for the frame
        frame_hash = hash_frame(gray_frame)
        frame_hashes.append(frame_hash)

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


def video_fingerprint(video_path):
    video = VideoFileClip(video_path)
    fingerprints = set()

    for i, frame in enumerate(video.iter_frames(fps=1)):  # Adjust fps as needed
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized_frame = cv2.resize(gray_frame, (32, 32))  # Resize for faster processing
        hash_value = hashlib.sha256(resized_frame.tobytes()).hexdigest()
        fingerprints.add((hash_value, i))  # Include the timestamp (frame number / fps)

    return list(fingerprints)


def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration_seconds = frame_count / fps
    cap.release()
    return duration_seconds
