import multiprocessing, queue
import azure.cognitiveservices.speech as speechsdk

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

porcupinePath = "./Porcupine"
sys.path.append(os.path.join(os.path.dirname(__file__), porcupinePath + '/binding/python'))

from porcupine import Porcupine

def _default_library_path():
    system = platform.system()
    machine = platform.machine()

    if system == 'Darwin':
        return os.path.join(os.path.dirname(__file__), porcupinePath + '/lib/mac/%s/libpv_porcupine.dylib' % machine)
    elif system == 'Linux':
        if machine == 'x86_64' or machine == 'i386':
            return os.path.join(os.path.dirname(__file__), porcupinePath + '/lib/linux/%s/libpv_porcupine.so' % machine)
        else:
            raise Exception('cannot autodetect the binary type. Please enter the path to the shared object using --library_path command line argument.')
    elif system == 'Windows':
        if platform.architecture()[0] == '32bit':
            return os.path.join(os.path.dirname(__file__), porcupinePath + '\\lib\\windows\\i686\\libpv_porcupine.dll')
        else:
            return os.path.join(os.path.dirname(__file__), porcupinePath + '\\lib\\windows\\amd64\\libpv_porcupine.dll')
    raise NotImplementedError('Porcupine is not supported on %s/%s yet!' % (system, machine))

library_path = _default_library_path()
model_file_path = porcupinePath + '/lib/common/porcupine_params.pv'
keyword_file_paths = [porcupinePath + '/resources/keyword_files/windows/hey bag_windows.ppn']
sensitivities = [0.5]
output_path = None
input_audio_device_index = None
CMD_KWS = [
	('what', 'in', 'front')  # what is in front of me
	('where', 'is')  # where is my bottle
	('where', 'am', 'i')  # where am i
]


def show_audio_devices_info():
    """ Provides information regarding different audio devices available. """

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']

    pa = pyaudio.PyAudio()

    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        print(', '.join("'%s': '%s'" % (k, str(info[k])) for k in _AUDIO_DEVICE_INFO_KEYS))

    pa.terminate()

def start_node(task_queue, objdetect_tasks, nav_tasks, text2speech_tasks):
    """
    Creates an input audio stream, initializes wake word detection (Porcupine) object, and monitors the audio
    stream for occurrences of the wake word(s). It prints the time of detection for each occurrence and index of
    wake word.
    """

    num_keywords = len(keyword_file_paths)

    keyword_names =\
        [os.path.basename(x).replace('.ppn', '').replace('_compressed', '').split('_')[0] for x in keyword_file_paths]

    print('Listening for:')
    for keyword_name, sensitivity in zip(keyword_names, sensitivities):
        print('- %s (sensitivity: %f)' % (keyword_name, sensitivity))

    porcupine = None
    pa = None
    audio_stream = None
    try:
        porcupine = Porcupine(
            library_path=library_path,
            model_file_path=model_file_path,
            keyword_file_paths=keyword_file_paths,
            sensitivities=sensitivities)

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=input_audio_device_index)

        speech_key, service_region = "b1b54e5bcd8943f0b8106e000e1298d7", "eastasia"
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # Creates a recognizer with the given settings
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        
        while True:
            
            try:
                task = task_queue.get_nowait()
                if task is None:
                    break
            except queue.Empty:
                pass

            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            recorded_frames = []
            if output_path is not None:
                recorded_frames.append(pcm)

            result = porcupine.process(pcm)
            if num_keywords == 1 and result:
                print('[%s] detected keyword' % str(datetime.now()))
                # Creates an instance of a speech config with specified subscription key and service region.
                # Replace with your own subscription key and service region (e.g., "westus").

                print("Any instruction, sir?")
                text2speech_tasks.put(('bing',))

                # Starts speech recognition, and returns after a single utterance is recognized. The end of a
                # single utterance is determined by listening for silence at the end or until a maximum of 15
                # seconds of audio is processed.  The task returns the recognition text as result. 
                # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
                # shot recognition like command or query. 
                # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
                result = speech_recognizer.recognize_once()

                # Checks result.
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    print("Recognized: {}".format(result.text))

					tokens = result.text.split()
					for i, kws in enumerate(CMD_KWS):
						matched = 0
						for token in tokens:
							if token in kws:
								matched += 1

						if matched == len(kws):
							if i == 0:
								objdetect_tasks.put(('overview',))
							else if i == 1:
								objdetect_tasks.put(('find', tokens[-1]))
							else if i == 2:
								nav_tasks.put('location',)

                elif result.reason == speechsdk.ResultReason.NoMatch:
                    print("No speech could be recognized: {}".format(result.no_match_details))
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        print("Error details: {}".format(cancellation_details.error_details))
            elif num_keywords > 1 and result >= 0:
                # Multi-keywords detected
                # Not used
                pass
    finally:
        if porcupine is not None:
            porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()

        if output_path is not None and len(recorded_frames) > 0:
            recorded_audio = np.concatenate(recorded_frames, axis=0).astype(np.int16)
            soundfile.write(output_path, recorded_audio, samplerate=porcupine.sample_rate, subtype='PCM_16')