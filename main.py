import multiprocessing
import realsense_node
import speech2text_node
import text2speech_node
import time

if __name__ == '__main__':
    # Establish communication queues
    objDetectionTasks = multiprocessing.Queue()
    objDetectionResults = multiprocessing.Queue()
    speechToTextTasks = multiprocessing.Queue()
    textSpeechTasks = multiprocessing.Queue()
    navTasks = multiprocessing.Queue()
    navResults = multiprocessing.Queue()

    workerSpeech2Txt = multiprocessing.Process(
    	name='speech to text'
    	, target=speech2text_node.start_node
    	, args=(speechToTextTasks, objDetectionTasks, navTasks)
    )
    workerTxt2Speech = multiprocessing.Process(
    	name='text to speech'
    	, target=text2speech_node.start_node
    	, args=(textSpeechTasks, objDetectionResults, navResults)
    )

    try:
        workerSpeech2Txt.start()
        workerTxt2Speech.start()

        realsense_node.start_node(objDetectionTasks, objDetectionResults)
    finally:
        objDetectionTasks.put(None)
        speechToTextTasks.put(None)
        textSpeechTasks.put(None)
        navTasks.put(None)
        
        workerSpeech2Txt.join()
        workerTxt2Speech.join()