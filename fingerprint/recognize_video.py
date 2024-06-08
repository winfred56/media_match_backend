from fingerprint.recognize_audio import find_matching_fingerprints, get_media_duration, identify_media_from_matches
from fingerprint.video_fingerprint import fingerprint_video_file


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

def recognize_video(uploaded_file_path):
    # Extract fingerprints from the uploaded portion
    uploaded_fingerprints = fingerprint_video_file(uploaded_file_path)

    # Find matching fingerprints in the database
    matches = find_matching_fingerprints(uploaded_fingerprints)
    print(f'Finished finding matches {matches}')

    if len(matches) > 0:
        print('About to find best match')
        # Get the duration of the uploaded video segment
        uploaded_segment_length = get_media_duration(uploaded_file_path)

        # Aggregate results and identify the media file
        identified_media = identify_media_from_matches(matches, uploaded_segment_length)
        print(f'Finished identifying media {identified_media}')
        return identified_media
    else:
        return None

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
