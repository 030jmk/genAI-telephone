#! /usr/bin/python3

import subprocess
import requests
import sounddevice as sd
from scipy.io.wavfile import write
import RPi.GPIO as GPIO
import threading
import numpy as np
import time as tm
from time import sleep
from unidecode import unidecode
import csv
import datetime
import signal

# Pin definitions
pulse_input_pin = 2
reset_button_pin = 3
switch_hook_pin = 26

# Some Constants
api_key = "sk-..."
filename = "audiocapture.wav"
speech_key = "01...."
service_region = "germanywestcentral"

# Initialize process variable
process = None
exp_started = False
pulse_count = 0
reset_button_pressed = False

class ResetPressedException(Exception):
    print("Starting")
    sleep(1)
    pass

def pulse_detected(channel):
    global pulse_count
    pulse_count += 1

def reset_pulse_helper():
    global pulse_count
    sleep(5)  # Replace with the number of seconds you want to count pulses for
    print(f"Number dialed: {pulse_count}")
    return pulse_count

def dial_helper(pulse_count):
    if pulse_count == 1:
        return "Act like an absolute answer bot. Answer only in absolute Yes or No. If there are moral concerenes, still answer in absolutes. Respond in English even though the question that follows is not in english."
    elif pulse_count == 2:
        return "You are a helpful explainer bot. You use Simple English Language. Answer me as if I were a literal 5 year old. Give a 1 sentence maximum answer. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 3:
        return "You are a ELI5 bot that give a one sentence answer. You respond only in English even if the sentence that follows is not English."
    elif pulse_count == 4:
        return "You are David Attenborough narrating a BBC documentary. Describe the answer to the following question as if you were exploring it for the first time, highlighting its unique features, behaviors, and significance. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 5:
        return "You are a Technobabble bot. You provide a detailed explanation or description using abundant technobabble related to the answer of the following question. Use complex scientific terminology, elaborate on technical details, and emphasize the intricacies of the subject matter. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 6:
        return "You are a Valley Girl and respond in the typical style associated with it. Like, oh my God, okay, so like, you are a Valley girl. It's, like, totally, like, characterized by, like, a particular accent and, like, a set of, like, phrases and, like, mannerisms. Totally respond in the style of a valley girl. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 7:
        return "You are John, a 28-year-old software engineer and technology consultant in Silicon Valley. John epitomizes the stereotypical tech bro persona with his confident swagger, extensive knowledge of tech jargon and frameworks, and a competitive drive to stay ahead in the ever-evolving world of technology. John exudes an air of superiority while passionately discussing disruptive technologies in the industry. Respond only in English even if the sentence that follows is not English.Respond to the following prompt as John."
    elif pulse_count == 8:
        return "You are a poetry bot. Answer in a poetic form, using rhymes throughout. Respond to the following question in verse, with each line maintaining a consistent rhyme scheme. Use a maximum of three verses. Alternatively, you may use rap instead. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 9 or pulse_count >= 10:
        return "You are an expert bot. Use professional terminology to answer my request. Give a 5 sentence maximum answer. Respond only in English even if the sentence that follows is not English."
    elif pulse_count == 0:
        return "You are a bot that is very direct and gives a one sentence answer. you use simple english. maximum 12 words. answer only in english."

def voice_helper(pulse_count,generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None):
    if pulse_count == 1:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 2:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 3:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 4:
        generate_text_to_answer(generated_text, lang='en-US', gender='Male', name='en-GB-AlfieNeural', style=None)
    elif pulse_count == 5:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 6:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style='cheerful')
    elif pulse_count == 7:
        generate_text_to_answer(generated_text, lang='en-US', gender='Male', name='en-US-JasonNeural', style='excited')
    elif pulse_count == 8:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 9 or pulse_count >= 10:
        generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None)
    elif pulse_count == 0:
        generate_text_to_answer(generated_text, lang='en-AU', gender='Female', name='en-AU-KimNeural', style=None)

def generate_text_to_speech(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None):
    url = "https://germanywestcentral.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": "01ff10d899f5494abc7b0a114256b849",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-64kbitrate-mono-mp3",
        "User-Agent": "curl"
    }

    data = f'''
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">
    <voice name="{name}">
        <mstts:express-as style="{style}" styledegree="1">
            {generated_text}
        </mstts:express-as>
    </voice>
    </speak>
    '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open("generated_answer.mp3", "wb") as file:
            file.write(response.content)
    else:
        print("Error:", response.status_code)

def generate_text_to_answer(generated_text, lang='en-US', gender='Female', name='en-US-JennyNeural', style=None):
    url = "https://germanywestcentral.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": "01ff10d899f5494abc7b0a114256b849",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-64kbitrate-mono-mp3",
        "User-Agent": "curl"
    }

    data = f'''
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">
    <voice name="{name}">
        <mstts:express-as style="{style}" styledegree="1">
            {generated_text}
        </mstts:express-as>
    </voice>
    </speak>
    '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open("answer.mp3", "wb") as file:
            file.write(response.content)
    else:
        print("Error:", response.status_code)

def reset_callback(channel):
    if not GPIO.input(reset_button_pin):
        raise ResetPressedException("reset is pressed")

def reset_button_callback(channel):
    global reset_button_pressed
    reset_button_pressed = True

def record_audio(filename):
    # Constants
    MIN_RECORD_SECONDS = 5
    MAX_RECORD_SECONDS = 30
    SAMPLE_RATE = 22050
    BIT_DEPTH = 'int32'
    BLOCKSIZE= 4096*4 #2048
    CHANNELS = 1
    PAUSE_THRESHOLD = 1
    VOLUME_THRESHOLD = 20


    # Create a buffer to hold audio data
    buffer = []

    # Flag variables for recording control
    recording_started = False
    recording_stopped = False

    # Variables for timing and pause detection
    start_time = 0
    low_volume_start_time = 0


    # Define callback function for the stream
    def callback(indata, frames, time, status):
        nonlocal buffer, recording_started, recording_stopped, start_time, low_volume_start_time

        # Calculate the volume
        volume = np.linalg.norm(indata) // 100000000
        print(volume)

        # Check if recording should start
        if not recording_started:
            recording_started = True
            start_time = tm.time()

        # Check if recording is in progress
        if recording_started and not recording_stopped:
            # Check if maximum record time has been exceeded
            if tm.time() - start_time > MAX_RECORD_SECONDS:
                recording_stopped = True
            else:
                # Check if volume is above the threshold
                if volume > VOLUME_THRESHOLD:
                    buffer.append(indata.copy())
                    print("Data added to buffer")
                    low_volume_start_time = 0
                else:
                    # Check if it's the start of low volume
                    if low_volume_start_time == 0:
                        low_volume_start_time = tm.time()
                    elif tm.time() - low_volume_start_time > PAUSE_THRESHOLD:
                        # Check if minimum record time has been reached
                        if tm.time() - start_time > MIN_RECORD_SECONDS:
                            recording_stopped = True

        # Check if recording should stop
        if recording_stopped:
            pass
            
    print("starting recording ...")
    # Create an input stream with adjusted sample rate and bit depth
    with sd.InputStream(samplerate=SAMPLE_RATE, dtype=BIT_DEPTH, channels=CHANNELS, callback=callback, blocksize=BLOCKSIZE):
        try:
            while True:
                # Check if reset button is pressed
                if reset_button_pressed or recording_stopped:
                    print("reset_button_pressed: {}".format(reset_button_pressed))
                    print("recording_stopped: {}".format(recording_stopped))
                    raise ResetPressedException
                tm.sleep(0.1)  # Sleep to reduce CPU usage
        except (sd.CallbackStop, ResetPressedException):
            print("Caught exception.")
            #GPIO.remove_event_detect(reset_button_pin)
            #GPIO.add_event_detect(reset_button_pin, GPIO.FALLING, callback=reset_button_callback, bouncetime=300)
            pass
        except ValueError as ve:
            print(ve)
            pass

    # Convert the buffer list to a numpy array
    print("convert buffer to numpy array")
    audio_data = np.concatenate(buffer)

    print("converting audio")
    # Save the audio data to a WAV file
    write(filename, SAMPLE_RATE, audio_data)

def text_response_gpt(transcription,preprompt):
    url="https://api.openai.com/v1/chat/completions"
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    data={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": preprompt}, {"role": "user", "content": transcription}],
        "temperature": 0.7,
        "max_tokens": 300,
        "frequency_penalty": 0,
        "presence_penalty": 0}
    response = requests.post(url, headers=headers, json=data)
    output = response.json()["choices"][0]["message"]["content"]  #response.json()["choices"][0]["text"]
    return(output)

def save_to_log(prompt, answer=''):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save prompt and answer to CSV file
    with open('log.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow([current_time, pulse_count, prompt, answer])

# Suppress warnings
GPIO.setwarnings(False)
# Use "GPIO" pin numbering
GPIO.setmode(GPIO.BCM)
# Set switch_hook_pin as input
GPIO.setup(reset_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pulse_input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Add event detection to the pins
GPIO.add_event_detect(reset_button_pin, GPIO.FALLING, callback=reset_button_callback, bouncetime=300)
GPIO.add_event_detect(pulse_input_pin, GPIO.FALLING, callback=pulse_detected, bouncetime=100)
#GPIO.add_event_detect(switch_hook_pin, GPIO.BOTH, callback=lambda _: exp_start() if GPIO.input(switch_hook_pin) else exp_stop(), bouncetime=200)
GPIO.add_event_detect(switch_hook_pin, GPIO.BOTH, 
                      callback=lambda _: None, 
                      bouncetime=200)


def exp_start(channel):
    print("startig the exp. A")
    global process
    global exp_started
    global pulse_count

    if channel == switch_hook_pin and not exp_started:
        if GPIO.input(channel) == 0:
            return

        subprocess.run(["play", "-q", "dual_tone.wav","-t","alsa"])
        generate_text_to_speech("Hello and thank you for giving this demo a try. My name is Whisper and i will guide you through this experience.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        generate_text_to_speech("In a moment will ask you to dial a number from the rotary in front of you.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        generate_text_to_speech("Each of the numbers correspond with a preconfigured persona and if you were to ask a different persona the same question, you should be able to hear different answers.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        generate_text_to_speech("I will give you a couple of seconds to make your selection after the audible beep sound. Please only dial one number.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return

        print("Requesting a dial.")
        pulse_count=0
        subprocess.run(["play", "-q", "AfterTheBeep.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        
        reset_thread = threading.Thread(target=reset_pulse_helper)
        reset_thread.start()
        sleep(5)
        preprompt = "{}".format(dial_helper(pulse_count))
        subprocess.run(["play", "-q", "AfterTheBeep.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        sleep(1)

        generate_text_to_speech("It would seem that you have made your decision. You have dialed {}.".format(pulse_count))
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        sleep(1)
        generate_text_to_speech("With the following beep I will relay your message or question according to your selection. ")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        generate_text_to_speech("I will again give you a couple of seconds to speak your message into the handset. Once you are done speaking, i will wait two seconds and relay your message with the second beep. ")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        generate_text_to_speech("If for some reason you cant hear that second beep, press the black button to the right of the dial. Get ready for the beep in 3... 2... 1...")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return

        subprocess.run(["play", "-q", "AfterTheBeep.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        record_audio("audiocapture.wav")
        subprocess.run(["play", "-q", "AfterTheBeep.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return

        sleep(0.5)

        generate_text_to_speech("I will relay our message. Let us wait a few seconds until we get a response. Please hold.")
        sleep(0.5)
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        player = subprocess.Popen(["play","-q", "yesterday-jazz-elevator-147660.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        print("Relaying Message")
        with open(filename, 'rb') as f:
            response_whisper = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": "Bearer " + api_key},
                files={"file": f},
                data={"model": "whisper-1"}).json()

        transcription = response_whisper["text"]
        print("\n\n{}\n\n".format(transcription))
        print("Receiving a response.")
        sleep(0.5)
        generated_text = text_response_gpt(transcription,preprompt)
        print(generated_text)
        save_to_log(transcription,generated_text)
        
        #generate_text_to_speech(unidecode(generated_text))
        voice_helper(pulse_count,unidecode(generated_text))
        sleep(0.5)
        player.terminate()
        if GPIO.input(channel) == 0:
            return
        sleep(0.5)
        generate_text_to_speech("It would seem that we have received an answer. Here it is.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        sleep(0.5)
        subprocess.run(["play", "-q", "answer.mp3","-t", "alsa"])
        sleep(1)
        generate_text_to_speech("And that is it. Thank you for trying this short demonstration. If you like to give it another go, put down the handset back onto the switch hook and lift it up again after a few seconds. If you are done, place the handset onto the switch hook and leave the cabin once you are ready. Thank you and have a pleasant day.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        sleep(1)
        subprocess.run(["play", "-q", "Gassenbesetztton.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            return
        sleep(1)


def exp_stop(channel):
    global process
    global exp_started
    if channel == switch_hook_pin:
        process = None
        exp_started = False


def main_loop():
    global process
    global exp_started
    try:
        while True:
            if GPIO.input(switch_hook_pin) == False and exp_started == False:
                print(".")
                sleep(2)
            else:
                print("switch hook un-pressed")
                exp_start(switch_hook_pin)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        generate_text_to_speech("I am sorry to inform you that something did not work quite right. I will have to restart the experience.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        print("Restarting...")
        if process is not None:
            exp_stop(switch_hook_pin)
            print("experience stopped..")
        print("starting main_loop again.")
        main_loop()
try:
    main_loop()
except KeyboardInterrupt:
    print("Exiting gracefully")
    GPIO.cleanup() 
