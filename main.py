import multiprocessing
import realsense_node
import speech2text_node
import text2speech_node
import time

if __name__ == '__main__':
    # Establish communication queues
    objDetectionTasks = multiprocessing.Queue()
    speechToTextTasks = multiprocessing.Queue()
    textToSpeechTasks = multiprocessing.Queue()
    navTasks = multiprocessing.Queue()
    workerSpeech2Txt = multiprocessing.Process(
    	name='speech to text'
    	, target=speech2text_node.start_node
    	, args=(speechToTextTasks, objDetectionTasks, navTasks)
    )
    workerTxt2Speech = multiprocessing.Process(
    	name='text to speech'
    	, target=text2speech_node.start_node
    	, args=(textToSpeechTasks)
    )

    try:
        workerSpeech2Txt.start()
        workerTxt2Speech.start()

        realsense_node.start_node(objDetectionTasks, textToSpeechTasks)
    finally:
        objDetectionTasks.put(None)
        speechToTextTasks.put(None)
        textToSpeechTasks.put(None)
        navTasks.put(None)

        workerSpeech2Txt.join()
        workerTxt2Speech.join()