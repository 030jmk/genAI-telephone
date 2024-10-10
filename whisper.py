import RPi.GPIO as GPIO  
import subprocess  
import requests  
import os  
from time import sleep  
from datetime import datetime
from flask import Flask, render_template, stream_with_context, request, Response

switch_hook_pin = 26  
process = None
exp_started = False
api_key = os.environ.get('OPENAI_API_KEY')  

def setup_gpio(pin):
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
def current_datetime():
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return current_time

def play_interruptible(audio_file, switch_hook_pin):  
    process = subprocess.Popen(["play", "-q", audio_file, "-t", "alsa"])  
    while process.poll() is None:  
        if GPIO.input(switch_hook_pin) == 1:  
            process.terminate()  
            process.wait()  
            return False  
        sleep(0.1)  
    return True  
  
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
        'voice': voice  
    }  
    response = requests.post(url, headers=headers, json=data)  
    if response.status_code == 200:  
        with open("generated_answer.mp3", "wb") as file:  
            file.write(response.content)  
    else:  
        print("Error:", response.status_code)  
        append_to_log(response.status_code)  
  
def text_response_gpt(preprompt):  
    url = "https://api.openai.com/v1/chat/completions"  
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}  
    data = {  
        "model": "gpt-3.5-turbo",  
        "messages": [{"role": "system", "content": preprompt}, {"role": "user", "content": "State a fact."}],  
        "temperature": 1,  
        "max_tokens": 400,  
        "frequency_penalty": 0,  
        "presence_penalty": 0  
    }  
    response = requests.post(url, headers=headers, json=data)  
    output = response.json()["choices"][0]["message"]["content"]  
    return output  


def exp():
    global process, exp_started
    print("exp start")
    if GPIO.input(switch_hook_pin) == 0:
        play_interruptible("dual_tone.wav",switch_hook_pin)
        play_interruptible("fact_of_the_day.mp3",switch_hook_pin)
        player = subprocess.Popen(["play", "-q", "yesterday-jazz-elevator-147660.mp3", "-t", "alsa"])
        fact = text_response_gpt("Today is {}. Give me a wikipedia fact of the day that happened today and add a comment. Do not mention that you are adding a comment".format(current_datetime()))  
        print(fact)
        print("creating audio")
        generate_text_to_speech(fact)
        player.terminate()
        print("playback")
        play_interruptible("generated_answer.mp3",switch_hook_pin)
        sleep(1)
        play_interruptible("fact_or_fiction.mp3",switch_hook_pin)
        play_interruptible("Gassenbesetztton.wav",switch_hook_pin)

if __name__ == "__main__":  
    setup_gpio(switch_hook_pin)  
    try:  
        previous_state = GPIO.input(switch_hook_pin)  
        initial_execution = True  
  
        while True:  
            sleep(1)  
            current_state = GPIO.input(switch_hook_pin)  
            if current_state != previous_state:  
                if current_state == GPIO.LOW and initial_execution:  
                    print("Switch hook up")  
                    exp()  
                    initial_execution = False  
                elif current_state == GPIO.HIGH:  
                    print("Switch hook down")  
                    initial_execution = True  
  
                previous_state = current_state  
    except KeyboardInterrupt:  
        GPIO.cleanup()  
