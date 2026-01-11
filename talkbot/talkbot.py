# Imports
# make openwakeword think onnxruntime is installed (it doesn't actually need it)
import sys
from types import ModuleType
sys.modules["onnxruntime"] = ModuleType("onnxruntime")

from pynq import Overlay
from scipy import signal
from scipy.io import wavfile
from numba import jit
import numpy as np
import ctypes
import openwakeword
import multiprocessing as mp
import wave
import speech_recognition as sr
import tempfile
import logging
from os import system
from openai import OpenAI
from gtts import gTTS
openai_api_key = "your-api-key-here"

logging.basicConfig(level=logging.INFO)

overlay = Overlay('/home/xilinx/overlay/base.bit')  # or replace with your own path
audio = overlay.audio_direct_0

audio_queue = mp.Queue()
audio_lock = mp.Lock()  # used to ensure multiple processes don't try to do audio operations simultaneously
audio_lock_priority = mp.Value(ctypes.c_char, b'i')  # used to ensure playback gets the lock first before (further) recording

oww_model_name = "hey_jarvis_v0.1"
openwakeword.utils.download_models([oww_model_name])
oww_model = openwakeword.model.Model(
    wakeword_models=[oww_model_name],
    inference_framework="tflite",
)

audio_chunk_size = 1  # size of chunks used as input to openwakeword (multiples of 80ms)
detection_thresh = 0.8  # 0-1, on openwakeword output
noise_thresh = 1e6  # set arbitrarily based on a quiet office
wakeword_process_quiet_seconds = 0.4  # consecutive quiet time to detect wakewords in before stopping
listen_quiet_seconds = 1.2  # consecutive quiet time to record for STT before stopping

openai_llm = "gpt-4o-mini"


def recorder():
    logging.info("Recording...")
    while True:
        if audio_lock_priority.value != b'o' and audio_lock.acquire(block=False):
            audio.record(0.08 * audio_chunk_size)
            # we are forcing the number of samples in the normalised PCM here
            # because openwakeword is (supposed to be) more efficient if it's
            # exact multiples of 80ms, but audio.record isn't exact. This
            # probably isn't an issue... right?
            audio_queue.put(normalized_pcm(audio, samples=1280 * audio_chunk_size))
            audio_lock.release()


def normalized_pcm(audio, samples=None):
    # crudely downsample to 16kHz
    fs = 16000
    samples = samples or int(np.round(audio.sample_len * fs / audio.sample_rate))
    fractional_sample_indices = np.arange(samples) * (audio.sample_rate / fs)
    sample_indices = np.clip(np.round(fractional_sample_indices).astype(int), 0, audio.sample_len - 1)
    audio_data = audio.buffer[sample_indices].astype(np.float32)

    # Remove DC offset
    audio_data -= np.mean(audio_data)

    # Compute RMS volume for later
    volume = np.sqrt(np.var(audio_data))

    # Normalize volume. This is being done on each frame separately, rather
    # than slowly evolving a gain on the signal. Could this be an issue for
    # wakeword detection and/or speech-to-text?
    audio_data /= max(1e-7, np.max(np.abs(audio_data)))  # don't divide-by-zero
    audio_data *= 0.99 * np.iinfo(np.int16).max

    # Convert to int16
    return volume, audio_data.astype(np.int16)


def oww_predict(chunk):
    oww_model.predict(chunk)
    return list(oww_model.prediction_buffer.values())[0][-1]


def get_llm_response(text):
    resp = OpenAI(api_key=openai_api_key).chat.completions.create(
        model=openai_llm,
        messages=[{"role": "user", "content": text}],
        max_tokens=300,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


@jit(nopython=True)
def delta_sigma_numba(upsampled):
    """Fast delta-sigma modulation with Numba."""
    pdm = np.zeros(len(upsampled), dtype=np.uint8)
    error = 0.0
    for i in range(len(upsampled)):
        if upsampled[i] > error:
            pdm[i] = 1
            error = error + 1.0 - upsampled[i]
        else:
            error = error - upsampled[i]
    return pdm


def pcm_to_pdm(pcm_samples, pcm_rate, pdm_rate=3072000):
    """Convert PCM audio to PDM format for PYNQ playback."""
    pcm = pcm_samples.astype(np.float64)
    if pcm_samples.dtype == np.int16:
        pcm = pcm / 32768.0
    pcm = (pcm - pcm.min()) / (pcm.max() - pcm.min() + 1e-10)

    ratio = pdm_rate // pcm_rate
    upsampled = signal.resample_poly(pcm, ratio, 1)

    pdm = delta_sigma_numba(upsampled)

    return pdm


def save_pdm(pdm_bits, filepath, pdm_rate=3072000):
    """Save PDM as WAV file (PYNQ .pdm format)."""
    pad = (16 - len(pdm_bits) % 16) % 16
    if pad:
        pdm_bits = np.concatenate([pdm_bits, np.zeros(pad, dtype=np.uint8)])

    reshaped = pdm_bits.reshape(-1, 16)
    packed = np.zeros(len(reshaped), dtype=np.uint16)
    for i in range(16):
        packed |= reshaped[:, i].astype(np.uint16) << i

    with wave.open(filepath, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(pdm_rate // 16)
        wav.writeframes(packed.tobytes())

    logging.info(f"Saved: {filepath}")


def say(text):
    tts = gTTS(text)

    # set up temporary files for conversion
    mp3 = tempfile.NamedTemporaryFile(suffix=".mp3")
    wav = tempfile.NamedTemporaryFile(suffix=".wav")
    pdm = tempfile.NamedTemporaryFile(suffix=".pdm")

    tts.write_to_fp(mp3)

    # convert MP3 to PCM
    system(f"ffmpeg -loglevel error -y -i {mp3.name} -c:a pcm_s16le -ac 1 {wav.name}")

    # convert PCM to PDM
    rate, pcm = wavfile.read(wav.name)
    pdm_data = pcm_to_pdm(pcm, rate)
    save_pdm(pdm_data, pdm.name)

    # acquire audio lock with priority and play response
    audio_lock_priority.value = b'o'
    audio_lock.acquire()
    audio_lock_priority.value = b'i'
    audio.load(pdm.name)
    audio.play()
    audio_lock.release()


def respond_to_audio(audio):
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(sr.AudioData(audio, 16000, 2))
        response = get_llm_response(text)
        logging.info(f"You said: {text}")
    except sr.UnknownValueError:
        response = "Sorry, I could not understand the audio."

    logging.info(f"Response: {response}")
    say(response)


if __name__ == "__main__":
    mp.Process(target=recorder, daemon=True).start()
    quiet_frames = int(1e10)  # assume it was silent before we started listening

    state = "waiting"  # this state handling is a bit ugly
    command_audio = None

    while True:
        volume, audio_frame = audio_queue.get()
        if volume < noise_thresh:
            quiet_frames += 1
        else:
            quiet_frames = 0

        if (behind := audio_queue.qsize() * audio_chunk_size * 0.08) > 5:
            logging.warning(f"Warning: {behind} seconds behind. Try reducing the noise threshold (volume: {volume})")

        if state == "waiting":
            if quiet_frames < int(wakeword_process_quiet_seconds / (audio_chunk_size * 0.08)):
                if (p := oww_predict(audio_frame)) > detection_thresh:
                    state = "listening"
                    logging.info("Got wakeword")
                    command_audio = []

        elif state == "listening":
            if quiet_frames < int(listen_quiet_seconds / (audio_chunk_size * 0.08)):
                command_audio.append(audio_frame)
            else:
                logging.info("Done listening")
                state = "waiting"
                respond_to_audio(np.concatenate(command_audio))
                while audio_queue.qsize() > 0:
                    audio_queue.get()  # ignore frames that were recorded while we were responding
