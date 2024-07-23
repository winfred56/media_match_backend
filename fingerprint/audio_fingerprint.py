from time import time
import hashlib
import numpy as np
import matplotlib.mlab as mlab
from matplotlib import pyplot as plt
from pydub import AudioSegment
from scipy.ndimage import maximum_filter, binary_erosion, generate_binary_structure, iterate_structure

# Constants
CONNECTIVITY_MASK = 2
DEFAULT_MIN_AMPLITUDE = 10
DEFAULT_SAMPLING_RATE = 44100
DEFAULT_OVERLAP_RATIO = 0.5
DEFAULT_WINDOW_SIZE = 4096
DEFAULT_FAN_VALUE = 5
PEAK_NEIGHBORHOOD_SIZE = 10
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200
SORT_PEAKS = True
FINGERPRINT_REDUCTION_SIZE = 20


def fingerprint_audio_file(file_path):
    """
    Fingerprint the audio file and return the fingerprint data.

    :param file_path: Path to the audio file.
    :return: List of fingerprint hashes.
    """
    channels, sampling_rate, _ = read_audio_file(file_path)

    # Measure fingerprinting time
    start_time = time()
    fingerprints = set()
    for channel in channels:
        fingerprints.update(generate_fingerprints(channel, sampling_rate))
    fingerprinting_duration = time() - start_time
    print("Fingerprinting duration: ", fingerprinting_duration)

    return list(fingerprints)


def read_audio_file(file_path, duration_limit=None):
    """
    Read the audio file and return channels, sample rate, and file hash.

    :param file_path: Path to the audio file.
    :param duration_limit: Optional limit in seconds.
    :return: channels, sample rate, file hash.
    """
    from pydub import AudioSegment

    audio_segment = AudioSegment.from_file(file_path)
    if duration_limit:
        audio_segment = audio_segment[:duration_limit * 1000]

    audio_data = np.frombuffer(audio_segment.raw_data, np.int16)
    channels = [audio_data[channel::audio_segment.channels] for channel in range(audio_segment.channels)]

    return channels, audio_segment.frame_rate, compute_file_hash(file_path)


def compute_file_hash(file_path, block_size=2 ** 20):
    """
    Generate a unique hash for the file.

    :param file_path: Path to the file.
    :param block_size: Block size for reading the file.
    :return: Unique hash string.
    """
    hash_sha1 = hashlib.sha1()
    with open(file_path, "rb") as file:
        while True:
            buffer = file.read(block_size)
            if not buffer:
                break
            hash_sha1.update(buffer)
    return hash_sha1.hexdigest().upper()


def generate_fingerprints(channel_samples, sampling_rate=DEFAULT_SAMPLING_RATE, window_size=DEFAULT_WINDOW_SIZE,
                          overlap_ratio=DEFAULT_OVERLAP_RATIO, fan_value=DEFAULT_FAN_VALUE,
                          min_amplitude=DEFAULT_MIN_AMPLITUDE):
    """
    Fingerprint the channel samples and return hashes.

    :param channel_samples: Channel samples.
    :param sampling_rate: Sampling rate.
    :param window_size: Window size for FFT.
    :param overlap_ratio: Overlap ratio.
    :param fan_value: Fan value for hashing.
    :param min_amplitude: Minimum amplitude for peaks.
    :return: List of hashes.
    """
    spectrogram_2D = mlab.specgram(
        channel_samples,
        NFFT=window_size,
        Fs=sampling_rate,
        window=mlab.window_hanning,
        noverlap=int(window_size * overlap_ratio)
    )[0]

    spectrogram_2D = 10 * np.log10(spectrogram_2D, out=np.zeros_like(spectrogram_2D), where=(spectrogram_2D != 0))
    # Plot the spectrogram
    plot_spectrogram(spectrogram_2D)
    peaks = find_2D_peaks(spectrogram_2D, min_amplitude=min_amplitude)

    return create_hashes_from_peaks(peaks, fan_value=fan_value)


def find_2D_peaks(spectrogram_2D, min_amplitude=DEFAULT_MIN_AMPLITUDE):
    """
    Get 2D peaks from the spectrogram matrix.

    :param spectrogram_2D: Spectrogram matrix.
    :param min_amplitude: Minimum amplitude for peaks.
    :return: List of peak frequencies and times.
    """
    structure = generate_binary_structure(2, CONNECTIVITY_MASK)
    neighborhood = iterate_structure(structure, PEAK_NEIGHBORHOOD_SIZE)

    local_maxima = maximum_filter(spectrogram_2D, footprint=neighborhood) == spectrogram_2D
    background = (spectrogram_2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    detected_peaks = local_maxima != eroded_background
    amplitudes = spectrogram_2D[detected_peaks]
    frequencies, times = np.where(detected_peaks)
    amplitudes = amplitudes.flatten()
    filtered_indices = np.where(amplitudes > min_amplitude)
    filtered_frequencies = frequencies[filtered_indices]
    filtered_times = times[filtered_indices]

    return list(zip(filtered_frequencies, filtered_times))


def create_hashes_from_peaks(peaks, fan_value=DEFAULT_FAN_VALUE):
    """
    Generate hashes from the peaks.

    :param peaks: List of peak frequencies and times.
    :param fan_value: Fan value for hashing.
    :return: List of hashes.
    """
    if SORT_PEAKS:
        peaks.sort(key=lambda x: x[1])

    hashes = []
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):
                freq1 = peaks[i][0]
                freq2 = peaks[i + j][0]
                time1 = peaks[i][1]
                time2 = peaks[i + j][1]
                time_delta = time2 - time1

                if MIN_HASH_TIME_DELTA <= time_delta <= MAX_HASH_TIME_DELTA:
                    hash_sha1 = hashlib.sha1(f"{freq1}|{freq2}|{time_delta}".encode('utf-8'))
                    hashes.append((hash_sha1.hexdigest()[:FINGERPRINT_REDUCTION_SIZE], time1))

    return hashes


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_seconds = len(audio) / 1000.0  # Duration in milliseconds, convert to seconds
    return duration_seconds


def plot_spectrogram(spectrogram):
    """
    Plot the spectrogram.

    :param spectrogram: 2D array representing the spectrogram.
    """
    plt.figure(figsize=(10, 6))
    plt.imshow(spectrogram, aspect='auto', origin='lower', cmap='jet')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.show()