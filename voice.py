'''
import speech_recognition as sr  
   
# obtain audio from the microphone  
r = sr.Recognizer()  
with sr.Microphone() as source:  
	print("Please wait. Calibrating microphone...")  
	# listen for 5 seconds and create the ambient noise energy level  
	r.adjust_for_ambient_noise(source, duration=5)  
	print("Say something!")  
	audio = r.listen(source)  
   
print("Now recognizing ...")

# recognize speech using Sphinx  
try:  
	print("Sphinx thinks you said '" + r.recognize_sphinx(audio) + "'")  
except sr.UnknownValueError:  
	print("Sphinx could not understand audio")  
except sr.RequestError as e:  
	print("Sphinx error; {0}".format(e))

# recognize speech using Microsoft Bing Voice Recognition
# AZURE_SPEECH_KEY = "b1b54e5bcd8943f0b8106e000e1298d7"  # Microsoft Speech API keys 32-character lowercase hexadecimal strings
# try:
#     print("Microsoft Azure Speech thinks you said " + r.recognize_azure(audio, key=AZURE_SPEECH_KEY))
# except sr.UnknownValueError:
#     print("Microsoft Azure Speech could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Microsoft Azure Speech service; {0}".format(e))
'''

import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "b1b54e5bcd8943f0b8106e000e1298d7", "eastasia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Say something...")


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
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
