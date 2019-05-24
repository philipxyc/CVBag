import pyttsx3

import multiprocessing, queue
import azure.cognitiveservices.speech as speechsdk

def start_node(task_queue):
    engine = pyttsx3.init()

    try:
        while True:
            task = task_queue.get_wait()
            if task is None:
                break
            else:
                if task[0] == "overview":
                    objects = task[1]
                    names = ", ".join(obj["classname"] for obj in objects)
                    message = "There are %s around you, sir." % names
                elif task[0] == "find":
                    target = task[1]
                    objects = task[2]
                    for obj in objects:
                        className, rect, m = obj["classname"], obj["rect"], int(obj["distance"]/1000)
                        if className == target:
                            direction = "left" if (rect[0] + rect[2]) / 2.0 < 320.0 else "right"
                            message = "%s is about %d meters in front of your %s." % (target, m, direction)
                elif task[0] == "location":
                    name = task[1]
                    message = "Sir, you're currently located at %s" % name
                else:
                    message = "Sir, it seems something wrong with me!"
            if message:
                engine.say(message)
                engine.runAndWait()
    finally:
        # Say goodbye
        engine.say("Goodbye")
        engine.runAndWait()