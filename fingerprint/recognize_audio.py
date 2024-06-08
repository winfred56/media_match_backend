import subprocess

from fingerprint.audio_fingerprint import fingerprint_audio_file
from fingerprint.models import SegmentHash


def recognize_audio(uploaded_file_path):
    # Extract fingerprints from the uploaded portion
    uploaded_fingerprints = fingerprint_audio_file(uploaded_file_path)
    print('finished hashing file')

    # Find matching fingerprints in the database
    matches = find_matching_fingerprints(uploaded_fingerprints)

    if matches:
        # Get the duration of the uploaded audio segment
        uploaded_segment_length = get_media_duration(uploaded_file_path)

        # Aggregate results and identify the media file
        identified_media = identify_media_from_matches(matches, uploaded_segment_length)
        return identified_media
    else:
        return None


def find_matching_fingerprints(uploaded_fingerprints):
    matches = []
    for hash_value, _ in uploaded_fingerprints:
        # Query the database for this hash value
        matched_segments = SegmentHash.objects.filter(hash_value=hash_value)
        if matched_segments.exists():
            matches.extend(matched_segments)
    print(matches)
    return matches


def identify_media_from_matches(matches, uploaded_segment_length):
    """
    Identify the media file from the list of matches.

    Parameters:
        matches (list): List of matched SegmentHash instances.
        uploaded_segment_length (float): Length of the uploaded segment in seconds.

    Returns:
        AudioVideoFile: The identified media file.
    """
    media_file_count = {}
    for match in matches:
        media_file = match.audio_video_file
        if media_file not in media_file_count:
            media_file_count[media_file] = 0
        media_file_count[media_file] += 1

    # Calculate match score based on the proportion of the matched segments
    media_file_scores = {
        media_file: count / uploaded_segment_length for media_file, count in media_file_count.items()
    }

    identified_media = max(media_file_scores, key=media_file_scores.get)
    return identified_media


def get_media_duration(file_path):
    """
    Get the duration of a media file using ffprobe.

    Parameters:
        file_path (str): Path to the media file.

    Returns:
        float: Duration of the media file in seconds.
    """
    duration_command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    result = subprocess.run(duration_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return float(result.stdout.strip())
    else:
        raise Exception('Failed to retrieve media duration.')
