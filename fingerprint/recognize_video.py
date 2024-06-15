from fingerprint.models import SegmentHash, AudioVideoFile
from fingerprint.recognize_audio import find_matching_fingerprints, get_media_duration, identify_media_from_matches
from fingerprint.video_fingerprint import video_fingerprint


# def recognize_video(uploaded_file_path):
#     # Extract fingerprints from the uploaded portion
#     uploaded_fingerprints = fingerprint_video_file(uploaded_file_path)
#     print('Finished hashing file')
#
#     # Find matching fingerprints in the database
#     matches = find_matching_fingerprints(uploaded_fingerprints)
#     print('Finished finding matches')
#
#     if matches:
#         # Aggregate results and identify the media file
#         identified_media = identify_media_from_matches(matches)
#         print(f'Finished identifying media {identified_media}')
#         return identified_media
#     else:
#         return None

# def recognize_video(uploaded_file_path):
#     # Extract fingerprints from the uploaded portion
#     uploaded_fingerprints = fingerprint_video_file(uploaded_file_path)
#
#     # Find matching fingerprints in the database
#     matches = find_matching_fingerprints(uploaded_fingerprints)
#     print(f'Finished finding matches {matches}')
#
#     if len(matches) > 0:
#         print('About to find best match')
#         # Get the duration of the uploaded video segment
#         uploaded_segment_length = get_media_duration(uploaded_file_path)
#
#         # Aggregate results and identify the media file
#         identified_media = identify_media_from_matches(matches, uploaded_segment_length)
#         print(f'Finished identifying media {identified_media}')
#         return identified_media
#     else:
#         return None

# def identify_media_from_matches(matches):
#     media_file_count = {}
#     for match in matches:
#         media_file = match.audio_video_file
#         if media_file in media_file_count:
#             media_file_count[media_file] += 1
#         else:
#             media_file_count[media_file] = 1
#     identified_media = max(media_file_count, key=media_file_count.get)
#     return identified_media

def recognize_video(query_video_path):
    query_fingerprints = video_fingerprint(query_video_path)
    query_hashes = [hash_value for hash_value, _ in query_fingerprints]

    # Fetch all fingerprints from the database that match any of the query hashes
    db_fingerprints = SegmentHash.objects.filter(hash_value__in=query_hashes)

    # Debug: Print the fetched db_fingerprints
    for db_fingerprint in db_fingerprints:
        print(f"DB Fingerprint: {db_fingerprint.hash_value}, File: {db_fingerprint.audio_video_file.file_name}")

    # Organize the database fingerprints by audio_video_file
    db_fingerprints_by_file = {}
    for db_fingerprint in db_fingerprints:
        file_id = db_fingerprint.audio_video_file_id
        if file_id not in db_fingerprints_by_file:
            db_fingerprints_by_file[file_id] = set()
        db_fingerprints_by_file[file_id].add(db_fingerprint.hash_value)

    best_match = None
    best_match_ratio = 0
    query_hash_set = set(query_hashes)
    for audio_video_file_id, db_hash_set in db_fingerprints_by_file.items():
        intersection = query_hash_set.intersection(db_hash_set)
        match_ratio = len(intersection) / min(len(query_hash_set), len(db_hash_set))

        if match_ratio > best_match_ratio:  # Find the best match
            best_match_ratio = match_ratio
            best_match = AudioVideoFile.objects.get(pk=audio_video_file_id)

    return best_match


