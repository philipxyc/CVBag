import pyttsx3

import multiprocessing, queue
import azure.cognitiveservices.speech as speechsdk

def start_node(task_queue, objdetect_results, nav_results):
    engine = pyttsx3.init()

    try:
        while True:
            try:
                task = task_queue.get_nowait()
                if task is None:
                    break
                for obj in objects:
                    className, confidence, rect, m = obj["classname"], obj["confidence"], obj["rect"], obj["distance"]
            except queue.Empty:
                pass

            message = None
            if not message:
                try:
                    task, objects = objdetect_results.get_nowait()
                    if task[0] == "overview":
                        names = ", ".join(obj["classname"] for obj in objects)
                        message = "There are %s around you, sir." % names
                    elif task[0] == "find":
                        target = task[1]
                        for obj in objects:
                            className, rect, m = obj["classname"], obj["rect"], int(obj["distance"]/1000)
                            if classname == target:
                                direction = "left" if (rect[0] + rect[2]) / 2.0 < 320.0 else "right"
                                message = "%s is about %d meters in front of your %s." % (target, m, direction)
                except queue.Empty:
                    pass

            if not message:
                try:
                    task = nav_results.get_nowait()
                    if task[0] == "where":
                        name = "Geekpie"
                        message = "Sir, you're currently located at %s" % name
                except queue.Empty:
                    pass

            if message:
                engine.say(message)
                engine.runAndWait()
    finally:
        # Say goodbye
        engine.say("Goodbye")
        engine.runAndWait()