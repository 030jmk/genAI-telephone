#! /usr/bin/python3

import subprocess
import requests
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
from flask import Flask, render_template, stream_with_context, request, Response
import threading
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def event_stream():
    with open('log.txt', 'r') as f:
        # Move to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                sleep(1)
                continue
            yield f"data: {line}\n\n"

@app.route('/events')
def sse():
    return Response(event_stream(), mimetype='text/event-stream')



# Pin definitions
pulse_input_pin = 2
reset_button_pin = 3
switch_hook_pin = 26

# Some Constants
api_key = os.environ.get('OPENAI_API_KEY')
filename = "audiocapture.wav"

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

def append_to_log(text,filename="log.txt"):
    #current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a') as file:
        text = text.replace("\n", "")
        file.write(f"{text}\n")


def reset_pulse_helper():
    global pulse_count
    sleep(5)  # Replace with the number of seconds you want to count pulses for
    print(f"Number dialed: {pulse_count}")
    append_to_log(f"Number dialed: {pulse_count}")

    return pulse_count

def generate_text_to_speech(text, api_key=api_key, voice='alloy'):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "curl"
    }
    data = {
        'model': 'tts-1',
        'input': text,
        'voice': voice}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open("generated_answer.mp3", "wb") as file:
            file.write(response.content)
    else:
        print("Error:", response.status_code)
        append_to_log(response.status_code)


def reset_callback(channel):
    if not GPIO.input(reset_button_pin):
        raise ResetPressedException("reset is pressed")

def reset_button_callback(channel):
    global reset_button_pressed
    reset_button_pressed = True


def text_response_gpt(preprompt):
    url="https://api.openai.com/v1/chat/completions"
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    data={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": preprompt}, {"role": "user", "content": "State a fact."}],
        "temperature": 1,
        "max_tokens": 400,
        "frequency_penalty": 0,
        "presence_penalty": 0}
    response = requests.post(url, headers=headers, json=data)
    output = response.json()["choices"][0]["message"]["content"]  #response.json()["choices"][0]["text"]
    return(output)

def save_to_log(preprompt, answer=''):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save prompt and answer to CSV file
    with open('log.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow([current_time, pulse_count, preprompt, answer])



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
    global process
    global exp_started
    global pulse_count

    if channel == switch_hook_pin and not exp_started:
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return

        subprocess.run(["play", "-q", "dual_tone.wav","-t","alsa"])
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return

        generate_text_to_speech("Hello! If you would like to listen to a random fact, stay tuned.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return
        preprompt = "You are a insightful fact bot. you state a random fact or insightful piece of information that happened on this day. The current date is:{}. please state an interesting fact from  the depths of wikipedia and pick a random artice. The more random the the average person, the better. In your response, stay on point, have a conversational tone, be percise and only give a maximum two sentence answer. Add a fitting comment or  retort, joke or dad-joke. Directly state the fact. Do not mention that you understand the request.".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        sleep(0.5)
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return
        player = subprocess.Popen(["play","-q", "yesterday-jazz-elevator-147660.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return

        append_to_log("Sending prompt: State a random fact or insightful piece of information")
        sleep(0.7)
        append_to_log("Requesting response")
        sleep(0.7)
        generated_text = text_response_gpt(preprompt)
        print(generated_text)
        append_to_log(f"Response: {generated_text}")

        save_to_log(generated_text)
        append_to_log("Requesting text to natural speech conversion")
        generate_text_to_speech(generated_text)
        sleep(0.7)
        append_to_log("Speech-to-Text playback")
        player.terminate()
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return

        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
#        sleep(0.8)
#        generate_text_to_speech("I hope the fact you got was satisfactory. Please put down the handset back onto the switch hook. Thank you.")
#        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return
        sleep(1)
        subprocess.run(["play", "-q", "Gassenbesetztton.wav","-t", "alsa"])
        if GPIO.input(channel) == 0:
            append_to_log("Call terminated")
            return
        sleep(1)

        append_to_log("Call terminated")
        while GPIO.input(channel) == 1:
            sleep(2)
            continue


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
            # If button is pressed
            if GPIO.input(switch_hook_pin) == False and exp_started == False:
                sleep(2)
            else:
                print("switch hook un-pressed")
                append_to_log("Call initiated")
                exp_start(switch_hook_pin)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        generate_text_to_speech("I am sorry to inform you that something did not work quite right. I will have to restart the experience.")
        subprocess.run(["play", "-q", "generated_answer.mp3","-t", "alsa"])
        print("Restarting...")
        append_to_log("Restarting ...")
        # Testing setting the vars
        process = None
        exp_started = False
        pulse_count = 0
        reset_button_pressed = False
        # If the process is running when the error occurred, stop it
        if process is not None:
            exp_stop(switch_hook_pin)
            print("experience stopped..")
        print("starting main_loop again.")
        # Call the function again to restart the loop
        main_loop()


if __name__ == '__main__':
    flask_thread = threading.Thread(target=app.run, kwargs={'debug': False, 'host': '0.0.0.0', 'port': 5000})
    flask_thread.start()
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        append_to_log("Exiting gracefully")
        GPIO.cleanup() # cleanup all GPIO
    except Exception as e:
        print(f"Error in main loop: {e}")
        append_to_log(f"Error in main loop: {e}")
