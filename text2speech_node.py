import pyttsx3

import multiprocessing, queue
# import azure.cognitiveservices.speech as speechsdk

# import play_audio
import snowboydecoder


def start_node(task_queue):
    engine = pyttsx3.init()

    try:
        while True:
            task = task_queue.get()
            if task is None:
                break
            else:
                message = None
                if task[0] == "overview":
                    objects = task[1]
                    if len(objects) == 0:
                        message = "Nothing is over here"
                    else:
                        names = ", ".join(obj["classname"] for obj in objects)
                        message = "There are %s around you, sir." % names
                elif task[0] == "find":
                    target = task[1]
                    objects = task[2]
                    found = False
                    for obj in objects:
                        className, rect, m = obj["classname"], obj["rect"], obj["distance"]/1000
                        if className in target:
                            direction = "left" if (rect[0] + rect[2]) / 2.0 < 320.0 else "right"
                            message = "%s is about %.1f meters in front of your %s." % (target, round(m, 1), direction)
                            found = True
                            break
                    if not found:
                        message = "I cannot find %s" % target
                elif task[0] == "location":
                    name = task[1]
                    message = "Sir, you're currently located at %s" % name
                elif task[0] == 'bing':
                    # play_audio.play('res/bing.wav')
                    snowboydecoder.play_audio_file('resources/ding.wav')
                elif task[0] == 'welcome':
                    message = "Welcome Sir"
                else:
                    message = "Sir, it seems something wrong with me!"
            if message is not None:
                engine.say(message)
                engine.runAndWait()

    except KeyboardInterrupt:
        print("Shutdown speech worker ...")
    finally:
        # Say goodbye
        engine.say("Goodbye")
        engine.runAndWait()
