import subprocess
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist

from fingerprint.models import SegmentHash, AudioVideoFile
from fingerprint.video_fingerprint import video_fingerprint


def recognize_video(query_video_path):
    # Step 0: Get the duration of the uploaded video
    uploaded_segment_length = get_media_duration(query_video_path)
    # Step 1: Extract fingerprints from the query video
    print('## Step 1: Extract fingerprints from the query video')
    query_fingerprints = video_fingerprint(query_video_path)
    print('Query Fingerprints:', query_fingerprints)  # Print query fingerprints
    query_hashes = [hash_value for hash_value, _ in query_fingerprints]

    # Step 2: Find matching fingerprints in the database
    matches = find_matching_fingerprints(query_fingerprints)

    if matches:
        # Step 3: Identify the best match
        identified_media = identify_video_from_matches(matches, uploaded_segment_length)
        return identified_media
    else:
        return None


def find_matching_fingerprints(uploaded_fingerprints):
    print('find_matching_fingerprints  ==>')
    matches = []
    max_matches = 20  # maximum number of matches to retrieve

    for hash_value, _ in uploaded_fingerprints:
        print(f"Looking for hash value: {hash_value}")
        if len(matches) >= max_matches:
            break

        # Query the database for this hash value and limit to the first remaining matches needed
        remaining_matches = max_matches - len(matches)
        matched_segments = SegmentHash.objects.filter(hash_value=hash_value)[:remaining_matches]

        if matched_segments.exists():
            matched_values = list(matched_segments.values('hash_value', 'audio_video_file_id'))
            print(f"Matched segments for hash {hash_value}: {matched_values}")
            matches.extend(matched_values)

    print(f'Final matches: {matches}')
    return matches


def get_media_duration(file_path):
    print('get_media_duration ==>')
    duration_command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    result = subprocess.run(duration_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return float(result.stdout.strip())
    else:
        raise Exception('Failed to retrieve media duration.')


def identify_video_from_matches(matches, uploaded_segment_length):
    """
    Identify the media file from the list of matches.

    Parameters:
        matches (list): List of matched dictionaries with 'hash_value' and 'audio_video_file_id'.
        uploaded_segment_length (float): Length of the uploaded segment in seconds.

    Returns:
        AudioVideoFile: The identified media file.
    """
    media_file_count = defaultdict(int)
    for match in matches:
        print(f"Match: {match}")
        audio_video_file_id = match['audio_video_file_id']

        try:
            media_file = AudioVideoFile.objects.get(id=audio_video_file_id)
            media_file_count[media_file] += 1
        except ObjectDoesNotExist:
            print(f"Media file with ID {audio_video_file_id} does not exist.")
            continue

    if not media_file_count:
        print("No valid media files found in matches.")
        return None

    # Calculate match score based on the proportion of the matched segments
    media_file_scores = {
        media_file: count / uploaded_segment_length for media_file, count in media_file_count.items()
    }

    identified_media = max(media_file_scores, key=media_file_scores.get)
    print(f"Identified media: {identified_media}")
    return identified_media
