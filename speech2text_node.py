import multiprocessing, queue
# import azure.cognitiveservices.speech as speechsdk

import speech_recognition as sr

import argparse
import os
import platform
import struct
import sys
from datetime import datetime
from threading import Thread

import numpy as np
import pyaudio
import soundfile
# import play_audio

import snowboydecoder

#porcupinePath = "./Porcupine"
#sys.path.append(os.path.join(os.path.dirname(__file__), porcupinePath + '/binding/python'))

#from porcupine import Porcupine

CMD_KWS = [
    ('what', 'in', 'front')  # what is in front of me
    , ('where', 'is')  # where is my bottle
    , ('where', 'am', 'i')  # where am i
]

__task_queue = None
__text2speech_tasks = None
__objdetect_tasks = None
__nav_tasks = None


BING_API_KEY = "b1b54e5bcd8943f0b8106e000e1298d7"
BING_REGION = "eastasia"

def hotword_detected_callback():
    print('[%s] detected keyword' % str(datetime.now()))
    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").

    print("Any instruction, sir?")
    __text2speech_tasks.put(('bing',))

    ##########################################################
    ### Recognition by Sphinx
    ##########################################################

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Adjusted ...")
        audio = r.listen(source, phrase_time_limit=3)
    print("Recognizing Speech ...")

    # recognize speech using Sphinx
    try:
        text = r.recognize_bing(audio, key=BING_API_KEY, region=BING_REGION).lower()
        # text = r.recognize_sphinx(audio).lower()
        # text = "what is in front of me"        
        print("Bing thinks you said " + text)

        punc = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        for c in punc: text = text.replace(c, ' ')  # Remove all punctuation
        tokens = text.split()
        for i, kws in enumerate(CMD_KWS):
            matched = 0
            for token in tokens:
                if token in kws:
                    matched += 1

            if matched == len(kws):
                if i == 0:
                    __objdetect_tasks.put(('overview',))
                elif i == 1:
                    __objdetect_tasks.put(('find', tokens[-1]))
                elif i == 2:
                    __nav_tasks.put(('location',))
    except sr.UnknownValueError:
        print("Bing could not understand audio")
    except sr.RequestError as e:
        print("Bing error; {0}".format(e))

def interrupt_callback():
    if __task_queue is None: return True
    try:
        task = __task_queue.get_nowait()
        if task is None:
            return True
            print("Hotword listening interrupted.")
    except queue.Empty:
        pass
    return False

def start_node(task_queue, objdetect_tasks, nav_tasks, text2speech_tasks):

    global __task_queue, __objdetect_tasks, __nav_tasks, __text2speech_tasks
    __task_queue = task_queue
    __objdetect_tasks = objdetect_tasks
    __nav_tasks = nav_tasks
    __text2speech_tasks = text2speech_tasks

    model_file = "resources/models/heybag.pmdl"
    detector = snowboydecoder.HotwordDetector(model_file)

    try:
        
        # play_audio.play('res/moss.wav')
        text2speech_tasks.put(('welcome',))

        while True:
            print('Listening Snowboy... Press Ctrl+C to exit')

            detector.start(detected_callback=hotword_detected_callback, interrupt_check=interrupt_callback, sleep_time=0.03)

    except KeyboardInterrupt:
        print("Shutdown nlp worker ...")
    finally:
        detector.terminate()
