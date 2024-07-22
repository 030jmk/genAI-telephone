# genAI-telephone
A retrofitted rotary dial phone with speech-to-text, a generative pre-trained transformer and text-to-speech.


## Description

The telephone is a fun project that utilizes a retrofitted rotary telephone as a tangible, tactile interface for artificial intelligence. Built upon technologies such as OpenAI’s Whisper API, which solves speech-to-text tasks, GPT-3.5, a fined-tuned version of the GPT3 (Generative Pre-Trained Transformer) model, Azure's Text to speech REST API, and a Raspberry Pi Zero W, 3b or 4.

## Motivation

The motivation behind GenAI-Telephone stemmed from a desire to diverge from traditional, screen-based interfaces that are the most familiar of digital interfaces in our modern lives. By repurposing a nostalgic rotary telephone, my goal is to invoke the past to interact with the technology of the present, allowing users to experience the capabilities of AI magic in a differntly engaging and refreshing manner. It is supposed to be a conversations starter on the topics of user interfaces, user experiences, AI safety, chat bots and their personas, as well as circularity of prototypes and demonstrators. 

## Dependencies (hardware and services)

- OpenAI's Whisper API (alternative: ![self hosted whisper](https://github.com/openai/whisper)) and GPT-3.5 (alternative: llama2) for speech recognition and text generation
- Azure's Text-To-Speech API for clear and natural language output (alternative: ![coqui TTS](https://github.com/coqui-ai/TTS))
- Raspberry Pi Zero W or 3b and later
- a rotary telephone
- a microphone from an old headset
- 2in1 mic/audio USB adapter
- TRRS Audio Male to 4-Pin screw terminal
- soldering iron

## Installation (Hardware)

- disassemble the telephone, making sure that none of the plastics get damaged in the process.

<img src="https://user-images.githubusercontent.com/12104518/258658876-311430c0-ae15-4ffb-b96b-73c940ffb540.jpg" alt="disassembled telephone" width="350">

- take out the inner parts of the telephone. For it, we will need a screwdriver and some wiggling around of the parts.

<img src="https://user-images.githubusercontent.com/12104518/258658853-d754b0f4-fbd8-4de3-b709-d1b16471a687.jpg" alt="plastic shell" width="350">

- It can be advantageous to desolder some of the pins and electronics in order to gain room for the raspberry pi.
  
<img src="https://user-images.githubusercontent.com/12104518/258658940-dbcd8d0b-19a0-43ef-ba99-4e563478fc55.jpg" alt="desoldered" width="350">

- prepare some female-to-female GPIO cables

<img src="https://user-images.githubusercontent.com/12104518/258658950-9252fbc0-d23b-49ba-9018-1e68db8ae401.jpg" alt="pins" width="350">

- and solder them to the rotary dial (yellow and green), button (green and brown), spring mechanism of the switch hook (which ever connections act as a button)

<img src="https://user-images.githubusercontent.com/12104518/258659070-3c1d15f8-7c62-4d22-82dc-3abafd8450f2.jpg" alt="colors" width="350">


![blink](https://github.com/030jmk/genAI-telephone/assets/12104518/46dc766c-8c7d-4dc1-a9d2-a95cd705320e)

- connect the cables of the handset to the TRRS Audio Male to 4-Pin screw terminal, plug the TRRS pin into the USB adapter and connect the adapter to the USB connection of the pi.
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


While waiting for an answer from the phone, elevator music may be used. "Yesterday (Jazz Elevator)" by Monument_Music is used for the current code:
    
    https://pixabay.com/de/music/bossa-nova-yesterday-jazz-elevator-147660/

Since it is likely that you would not want to have the API Keys as a string within the script, an evironmental variable may be set. On a rasperry pi this may look like this:
1. Open the .bashrc File:
```bash
nano ~/.bashrc  
```
2. Add the Environment Variable by scrolling to the bottom of the file and adding the following line:
```
export OPENAI_API_KEY='your_api_key_here'  
```
3. Save and Close the File by pressing Ctrl + X to exit and pressing Y and ENTER to save the changes.
4. Apply the Changes:
```
source ~/.bashrc 
```



## Basic Storyline
|    	| Sound           	| Story                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            	| Activity 	|
|----	|-----------------	|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|----------	|
| 00  	|                 	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	| PICK UP  	|
| 01  	| dual_tone       	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 02  	|                 	| "Hello and thank you for giving this demo a try. My name is Whisper and i will guide you through this experience. In a moment will ask you to dial a number from the rotary in front of you. Each of the numbers correspond with a preconfigured persona and if you were to ask a different persona the same question, you should be able to hear different answers. I will give you a couple of seconds to make your selection after the audible beep sound. Please only dial one number."      	|          	|
| 03  	| beep            	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 04  	|                 	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	| USE DIAL 	|
| 05  	| beep            	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 06  	|                 	| "It would seem that you have made your decision. You have dialed {}. With the following beep I will relay your message or question according to your selection. I will again give you a couple of seconds to speak your message into the handset. Once you are done speaking, i will wait two seconds and relay your message with the second beep. If for some reason you cant hear that second beep, press the black button to the right of the dial. Get ready for the beep in 3... 2... 1..." 	|          	|
| 07  	| beep            	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 08  	|                 	| "I will relay our message. Let us wait a few seconds until we get a response. Please hold."                                                                                                                                                                                                                                                                                                                                                                                                      	| SPEAK    	|
| 09  	| elevator_music  	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 10 	|                 	| "It would seem that we have received an answer. Here it is."                                                                                                                                                                                                                                                                                                                                                                                                                                     	|          	|
| 11 	| answer          	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
| 12 	|                 	| "And that is it. Thank you for trying this short demonstration. If you like to give it another go, put down the handset back onto the switch hook and lift it up again after a few seconds. If you are done, place the handset onto the switch hook and leave the cabin once you are ready. Thank you and have a pleasant day."                                                                                                                                                                  	|          	|
| 13 	| congestion_tone 	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	|          	|
|    	|                 	|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  	| PUT DOWN 	|


## In Action
The demo was presented at [Berlin Hack & Tell #89](https://berlinhackandtell.rocks/2023-07-25-no89-camping-hacks) 2023-07-25 and can now be tested and seen at the PwC Experience Center in Berlin.

<img src="https://user-images.githubusercontent.com/12104518/258660552-dcf21ca2-a04a-49a1-97af-d41b795c0510.png" alt="colors" width="350"> <img src="https://user-images.githubusercontent.com/12104518/258660575-2870c7c1-7ac7-4cc0-963b-05ddde5aabd0.jpg" alt="colors" width="350">








