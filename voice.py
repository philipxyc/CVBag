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

'''
# recognize speech using Sphinx  
try:  
	print("Sphinx thinks you said '" + r.recognize_sphinx(audio) + "'")  
except sr.UnknownValueError:  
	print("Sphinx could not understand audio")  
except sr.RequestError as e:  
	print("Sphinx error; {0}".format(e))
'''

# recognize speech using Microsoft Bing Voice Recognition
AZURE_SPEECH_KEY = "b1b54e5bcd8943f0b8106e000e1298d7"  # Microsoft Speech API keys 32-character lowercase hexadecimal strings
try:
    print("Microsoft Azure Speech thinks you said " + r.recognize_azure(audio, key=AZURE_SPEECH_KEY))
except sr.UnknownValueError:
    print("Microsoft Azure Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Microsoft Azure Speech service; {0}".format(e))
