# PYNQ Chatbot

## Introduction

This repository contains the new labs for the 2025-2026 Imperial EIE Information Processing module. These labs focuses on introducing the Vivado toolchain and PYNQ ecosystem.

The core idea of this module is to:
Understand the choices and tradeoffs of placing information processing nodes on the edge (e.g. local FPGA) and remote cloud environments (e.g. AWS).

Tested software versions:
- Vivado 2020.2, PYNQ v2.7, Windows 10
- We recommend you use the tested software to avoid unexpected behaviors
- Mac users can consider virtual machine options

## Schedule

There will be 4 lab weeks (2 hours of lab per week). The labs are designed to be completable within the given lab times, though students are expected to spend more time debugging and exploring the module by completing the challenges.

| Week | Lab | Description |
| --- | --- | --- |
| 1 | Lab 1 | Introduction to PYNQ and Vivado |
| 2 | Lab 2 | Audio Processing |
| 3 | Lab 3 | Building the chatbot |
| 4 | Lab 4 | AWS |
| Optional | Lab 5 | Extensions |

## Goal

The goal of these labs is to create an interactive chat bot which uses the power of Whisper and OpenAI system to understand your speech and communicate with you on an SoC platform.

Whisper is a robust automatic speech recognition (ASR) model developed by OpenAI that can transcribe and translate speech across multiple languages with high accuracy.

A general idea of the steps you will take:
1. Setup the PYNQ board and go through a simple FIR filter tutorial to understand the PYNQ-Vivado ecosystem.
2. Learn to utilise the audio modules on the PYNQ board.
3. Create a hardware design in Vivado which converts the PDM formatted audio into PCM format, and compare and contrast the speed with a software implementation.
4. Process the audio file with a chain of API calls to Whisper (ASR), OpenAI, and a cloud/local TTS service, then output the audio through the PYNQ board's audio jack.
5. Connect the talkbot to AWS services by utilising AWS's provided databases, such as DynamoDB.

Note: The lab is designed for Zynq-based boards with onboard MEMS microphones, such as the PYNQ-Z1, which record input in PDM format. For digital processing, the audio has to be converted into PCM before wrapping into a standardised format, such as a .wav file.

> Explanations for specific terminology: [Terminologies](notes.md#terminology)

## Labs
### Lab 1

[Lab 1 - Introduction to PYNQ and Vivado](labs/lab1/lab1.md)

In this lab, you will setup the PYNQ board and Xilinx toolchain, and familiarise yourself with the tools by generting a simple Vivado block design for an FIR filter, and implement it as an overlay in the Jupyter Notebook to witness the power of hardware acceleration.

### Lab 2

[Lab 2 - Audio Processing](labs/lab2/lab2.md)

In this lab, you will explore the audio processing capabilities of the PYNQ board, and implement a software PDM-PCM conversion in Python. You will also design a hardware PDM-PCM conversion in Vivado, and understand how to do basic embedded development with memory-mapped register control and driver development.

### Lab 3

[Lab 3 - Building the chatbot](labs/lab3/lab3.md)

In this lab, you will combine the processing powers of PYNQ, Whisper and AWS, to create a chatbot that can understand your speech and communicate with you. You will also connect the chatbot to AWS services by utilising AWS's provided databases, such as DynamoDB. Lastly, you will design and 3D print your chatbot by CAD scripting.

### Lab 4

[Lab 4 - AWS](labs/lab4/lab4.md)

<!-- In this lab, you will learn how to connect the PYNQ board to AWS services, and use AWS's provided databases, such as DynamoDB. You will also learn how to make API calls to AWS services, and store the data in the cloud. -->


### Lab 5 (optional)

[Lab 5 - Extensions](labs/lab5-optional/lab5.md)

Optional extensions for the labs, where you can explore different parts of the lab and improve on the current design. Note that these extensions are open-ended and are not restricted to the suggestions provided. While "optional", bonus marks will be awarded to your lab oral grades if you are able to complete the labs and demonstrate a nice challenging extension.

## Coursework

The coursework is open-ended, but must include the use of the PYNQ board and AWS.

It should be noted that while you have been taught to use PYNQ's Jupyter Notebook infrastructure to communicate and send commands to the programmable logic, it is always possible to build application / memory controllers in BareMetal or PetaLinux. 
You may choose to do so for your project is you find it suitable.
You will also be awarded additional marks for close-to-metal implementations.


--- 

Created by:
[Kevin Lau](https://uk.linkedin.com/in/kevinlau01),
[Cheng Zhang](https://chengzhang-98.github.io/blog/),
[Eleanor Clifford](https://eleanor.clifford.lol/),
[Sarim Baig]() and 
[Aaron Zhao](https://aaron-zhao123.github.io/)