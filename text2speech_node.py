import pyttsx3

import multiprocessing, queue
import azure.cognitiveservices.speech as speechsdk

import pyaudio  
import wave  

def play_audio(path):
    #define stream chunk   
    chunk = 1024  

    #open a wav format music  
    f = wave.open(path,"rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  

    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  

    #stop stream  
    stream.stop_stream()  
    stream.close()  

    #close PyAudio  
    p.terminate()


def start_node(task_queue, objdetect_results, nav_results):
    engine = pyttsx3.init()

    try:
        while True:
            task = task_queue.get()
            if task is None:
                break
            else:
                if task[0] == "overview":
                    objects = task[1]
                    if len(objects) == 0:
                        message = "Nothing is here"
                    else:
                        names = ", ".join(obj["classname"] for obj in objects)
                        message = "There are %s around you, sir." % names
                elif task[0] == "find":
                    target = task[1]
                    objects = task[2]
                    found = False
                    for obj in objects:
                        className, rect, m = obj["classname"], obj["rect"], int(obj["distance"]/1000)
                        if className in target:
                            direction = "left" if (rect[0] + rect[2]) / 2.0 < 320.0 else "right"
                            message = "%s is about %.2f meters in front of your %s." % (target, round(m, 1), direction)
                            found = True
                            break
                    if not found:
                        message = "I cannot find %s" % target
                elif task[0] == "location":
                    name = task[1]
                    message = "Sir, you're currently located at %s" % name
                else:
                    message = "Sir, it seems something wrong with me!"
            if message:
                engine.say(message)
                engine.runAndWait()
            if not message and task[0] == 'bing':
                play_audio('res/bing.wav')
    except KeyboardInterrupt:
        print("Shutdown speech worker ...")
    finally:
        # Say goodbye
        engine.say("Goodbye")
        engine.runAndWait()