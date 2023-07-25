# genAI-telephone
A retrofitted rotary dial phone with speech-to-text, a generative pre-trained transformer and text-to-speech.


## Description

The telephone is a fun project that utilizes a retrofitted rotary telephone as a tangible, tactile interface for artificial intelligence. Built upon  technologies such as OpenAI’s Whisper API, which solves speech-to-text tasks, GPT-3.5, a fined-tuned version of the GPT3 (Generative Pre-Trained Transformer) model, Azure's Text to speech REST API, and a Raspberry Pi Zero W or 3b.

## Motivation

The motivation behind GenAI-Telephone stemmed from a desire to diverge from traditional, screen-based interfaces that are the most familiar of digital interfaces in our modern lives. By repurposing a nostalgic rotary telephone, my goal is to invoke the past to interact with the technology of the present, allowing users to experience the capabilities of AI magic in a differntly engaging and refreshingly manner. It is supposed to be a conversations starter on the topics of user interfaces, user experiences, AI safety, chat bots and their personas, as well as circularity of prototypes and demonstrators.

## Dependencies (hardware and services)

- OpenAI's Whisper API and GPT-3.5 for speech recognition and text generation
- Azure's Text-To-Speech API for clear and natural language output
- Raspberry Pi Zero W or 3b and later
- a rotary telephone
- a microphone from an old headset
- 2in1 mic/audio USB adapter
- TRRS Audio Male to 4-Pin screw terminal
- soldering iron

## Installation (Hardware)
### Telephone
- disassemble the telephone, making sure that none of the plastics get damaged in the process. ![Gen AI phone](https://github.com/030jmk/genAI-telephone/assets/12104518/fac9759b-9a14-4b8e-bb69-40cd93190d02)
- take out the inner parts of the telephone. For it, we will need a screwdriver and some wiggling around of the parts. ![Gen AI phone](https://github.com/030jmk/genAI-telephone/assets/12104518/a9971768-f7bf-4330-8856-841b252af074)
- Though it is not a necessity, it could be preferential to desolder some of the pins etc in order to gain some space. ![Gen AI phone](https://github.com/030jmk/genAI-telephone/assets/12104518/394a40c5-ee7e-48f8-a2a4-47476f8cab7c)
- prepare some female-to-female GPIO cables ![Gen AI phone](https://github.com/030jmk/genAI-telephone/assets/12104518/c6558dbe-d92f-498c-aa46-c02d2cf5fb0b)
- and solder them to the rotary dial (yellow and green), button (green and brown), spring mechanism of the switch hook (which ever connections act as a button) ![Gen AI phone](https://github.com/030jmk/genAI-telephone/assets/12104518/9df8d39a-2e33-4763-8073-d863b3467d32) ![blink](https://github.com/030jmk/genAI-telephone/assets/12104518/46dc766c-8c7d-4dc1-a9d2-a95cd705320e)
- connect the cables of the handset to the TRRS Audio Male to 4-Pin screw terminal, plug in into the adapter and the adapter into the pi.
- find the ground pins for the raspberry pi.
- the rotary dial should be connected to GPIO pin 2
- the black button should be connected to GPIO pin 3
- the switch hook spring/button should be GPIO pin 26

## Dependencies (OS, Python)
Once Raspian and the usual updates are installed using 

    sudo apt update && sudo apt -y upgrade
the following dependencies should be installed:

    sudo apt install -y python3-pip python3-scipy python3-rpi.gpio sox gnuplot libsox-fmt-all ffmpeg libasound-dev libportaudio2 && pip install requests playsound numpy sounddevice Unidecode 

test the mic set up once everything is connected:

    arecord -f cd -c 1 -r 44100 | sox -t raw -r 44100 -e signed -b 16 -c 1 -V - -t raw - | gnuplot -persist -e "set xlabel 'Time'; set ylabel 'Amplitude'; plot '-' with lines"


While the waiting for an answer from the phone, elevator music may be used. I used Yesterday (Jazz Elevator) from Monument_Music:
    
    https://pixabay.com/de/music/bossa-nova-yesterday-jazz-elevator-147660/












