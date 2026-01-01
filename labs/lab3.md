# Lab 3: Building the chatbot

## 3.1 Setting up an internet connection

PYNQ has a nice and easy Python API for getting it to connect to ordinary (WPA2-PSK) WiFi, but it won't work for WPA2-Enterprise networks like eduroam. Fortunately for you, this module is not about reverse engineering various WiFi details that Imperial could have just put on their ICT website, so that has been done for you already.

Load [wifi.py](/wifi.py) onto the PYNQ board and run it, e.g. by clicking "Import" from the Jupyter Notebook web interface to load it, and then opening a new notebook to type `%run wifi.py`. Follow the instructions and be sure to read the security warning.

## 3.2 Using Whisper

https://pynq.readthedocs.io/en/v3.0.0/getting_started/network_connection.html#:~:text=With%20a%20direct%20connection%2C%20you,new%20packages%20without%20Internet%20access.

## 3.3 OpenAI API

## 3.4 gTTS

## 3.5 Wake word detection

We're almost finished with the software side of the chatbot, but we want the chatbot to be interactive, meaning that it understands when you are speaking to it. We will do a simple wake word detection using Porcupine.

## 3.6 CAD scripting

Congrats, you've made it to the last part of the labs. Unfortunately, this section is not an easy one. You will have to design and 3D print your chatbot!
