# Lab 3: Building the chatbot

Sections 3.1 and 3.2 should be easy. If you run into errors in them and get
stuck, please don't waste too much time, ask Ellie what to do
(e.clifford23@imperial.ac.uk).

## 3.1 Setting up an internet connection

PYNQ has a nice and easy Python API for getting it to connect to ordinary
(WPA2-PSK) WiFi, but it won't work for WPA2-Enterprise networks like eduroam.
Fortunately for you, this module is not about reverse engineering various WiFi
details that Imperial could have just put on their ICT website, so that has
been done for you already.

Load [wifi.py](/wifi.py) onto the PYNQ board and run it, e.g. by clicking
"Import" from the Jupyter Notebook web interface to load it, and then opening a
new notebook to type `%run wifi.py`. Follow the instructions and be sure to
read the security warning.

## 3.2 Installing the dependencies

Now that you have an internet connection, you can install all the software
libraries required for the chatbot onto the PYNQ board. Fortunately for you
again, this module is not about dealing with so-called "dependency hell". Use
[jupyter_notebook/lab3/dependencies.ipynb](/jupyter_notebook/lab3/dependencies.ipynb)
to install the dependencies.

## 3.3 Converting recorded audio to text

In order for the LLM to respond to the recorded audio, it first needs to be
converted to text. We can use the `speech_recognition` library for this. This
example uses Google's API, but the library supports many, use whichever you
find works best.

```python
import speech_recognition as sr
recognizer = sr.Recognizer()
audio.record(10)
text = recognizer.recognize_google(sr.AudioData(audio.buffer, audio.sample_rate, 2))

print(f"You said: {response}")
```

## 3.4 Getting a response from an LLM

To get a response from the LLM, we can use the OpenAI API:

```python
from openai import OpenAI

response = OpenAI(api_key=YOUR_OPENAI_API_KEY).chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": text}],
    max_tokens=300,
    temperature=0.7,
).choices[0].message.content.strip()

print(f"LLM responded: {response}")
```

## 3.5 Converting the text response to audio

We then want the LLMs response to be spoken back. We can use the `gTTS` library
for this. gTTS responds in MP3 format, so we will first use `ffmpeg` to convert
this into PCM format, before using the PCM to PDM converter from lab 2 and then
playing back the audio.

```python
from gtts import gTTS
import tempfile

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

    # playback
    audio.load(pdm.name)
    audio.play()
```

## 3.6 Detecting a wake word

We're almost finished with the software side of the chatbot, but we want the
chatbot to be interactive, meaning that it understands when you are speaking to
it. We will use `openwakeword` to do wakeword detection.

`openwakeword` requires 16kHz 16-bit PCM data, so we will do some simple
processing of the data we get from the audio overlay:

```python
import numpy as np

def normalized_pcm(audio):
    # crudely downsample to 16kHz
    fs = 16000
    samples = int(np.round(audio.sample_len * fs / audio.sample_rate))
    fractional_sample_indices = np.arange(samples) * (audio.sample_rate / fs)
    sample_indices = np.clip(np.round(fractional_sample_indices).astype(int), 0, audio.sample_len - 1)
    audio_data = audio.buffer[sample_indices].astype(np.float32)

    # Remove DC offset
    audio_data -= np.mean(audio_data)

    # Compute RMS volume for later
    volume = np.sqrt(np.var(audio_data))

    # Normalize volume
    audio_data /= max(1e-7, np.max(np.abs(audio_data)))  # don't divide-by-zero
    audio_data *= 0.99 * np.iinfo(np.int16).max

    # Convert to int16
    return volume, audio_data.astype(np.int16)
```

We can then process the data using openwakeword (in chunks), looking for the
phrase "Hey Jarvis" (you can also try other openwakeword models, which have
different phrases):

```python
# make openwakeword think onnxruntime is installed (it doesn't actually need it)
import sys
from types import ModuleType
sys.modules["onnxruntime"] = ModuleType("onnxruntime")

import openwakeword

oww_model_name = "hey_jarvis_v0.1"
openwakeword.utils.download_models([oww_model_name])
oww_model = openwakeword.model.Model(
    wakeword_models=[oww_model_name],
    inference_framework="tflite",
)

audio_chunk_size = 1  # size of chunks used as input to openwakeword (multiples of 80ms)
detection_thresh = 0.8  # 0-1

audio.record(10)
recording = normalized_pcm(audio)


def oww_predict(chunk):
    oww_model.predict(chunk)
    return list(oww_model.prediction_buffer.values())[0][-1]


# Why 1280?
for chunk in np.split(recording, np.arange(audio_chunk_size * 1280, len(recording), audio_chunk_size * 1280)):
    if oww_predict(chunk) > detection_thresh:
        print("Wakeword detected!")
```

This works fine, but we want the chatbot to listen for wakewords in realtime
without missing anything, so we need to extend this to record and process at
the same time. We can try to do this using multiple processes:

```python
import multiprocessing as mp

audio_queue = mp.Queue() # concurrency-safe queue to pass frames of audio through

def recorder():
    logging.info("Recording...")
    while True:
        audio.record(0.08 * audio_chunk_size)
        audio_queue.put(normalized_pcm(audio))
        audio_lock.release()

# start the recorder in a separate process
mp.Process(target=recorder, daemon=True).start()

while True:
    volume, audio_frame = audio_queue.get()

    if (p := oww_predict(audio_frame)) > detection_thresh:
        print("Got wakeword")
```

However, the wakeword detection model takes longer to process audio than the
duration of the audio, so this approach as-is will slowly fall behind.

To fix this, we can ignore any quiet audio which probably doesn't have any
words in it:

```python
noise_thresh = 1e6
wakeword_process_quiet_seconds = 0.4  # consecutive quiet time to detect wakewords in before stopping
quiet_frames = int(1e10)  # assume silence before the recording
while True:
    if (behind := audio_queue.qsize() * audio_chunk_size * 0.08) > 5:
        logging.warning(f"Warning: {behind} seconds behind. Try reducing the noise threshold")

    volume, audio_frame = audio_queue.get()
    if volume < noise_thresh:
        quiet_frames += 1
    else:
        quiet_frames = 0

    if quiet_frames < int(wakeword_process_quiet_seconds / (audio_chunk_size * 0.08)):
        if (p := oww_predict(audio_frame)) > detection_thresh:
            print("Got wakeword")
```

## 3.7 Putting it all together

An example chatbot program that combines all of the above (plus a few minor
extra things to glue it all together) has been provided for you at
[talkbot/talkbot.py](/talkbot/talkbot.py). This example program "works", but it
has a number of non-trivial problems. What are they? Which of them are best
solved by improving or adding features in hardware, and which are best solved
in software? Your task is to use everything you have learnt to make the best
chatbot you can.

## 3.8 Putting it all together in the real world

Congrats, you've made it to the last part of the labs. Now it's time to make it
look good in real life, by designing and 3D printing a case for the chatbot
hardware!

A basic example to work from has been created for you using
[OpenSCAD](https://openscad.org/). This should save you the pain of measuring
the size of the PYNQ board and exactly where all the ports are.

OpenSCAD models are designed by writing code, and based on logical operations
between "primitive" shapes (like cubes, spheres, and so on). For instance, a
hollow cube with an open top would be a subtraction between two cubes:

```scad
difference() {
    cube([1, 1, 1], center=true);
    translate([0, 0, 0.11]) cube([0.9, 0.9, 0.9], center=true);
}
```

![OpenSCAD example: hollow cube with open top](/images/lab3-openscad-example.jpg)

A good place to start with understanding SCAD syntax is the [OpenSCAD
cheatsheet](https://openscad.org/cheatsheet/). This links to the OpenSCAD wiki,
which has further information.

The example case can be found in [case/](case/), in two parts, `top.scad` and
`bottom.scad`. An assembly of how these are supposed to fit together (including
the PYNQ board) can be seen in `assembly.scad`. Start from this base, and make
it your own! If you want to design parts of the case in something more familiar
to you than OpenSCAD, some formats (e.g. SVG) can be imported directly into
OpenSCAD, others can be converted to or from OpenSCAD. You can also design the
case entirely in another program if you with, the only requirement is that the
final 3D model for printing is in STL format.
