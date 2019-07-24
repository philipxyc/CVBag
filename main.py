import multiprocessing
import realsense_node
import speech2text_node
import text2speech_node
import locator_node
import locator_node_cp
import time

if __name__ == '__main__':
    # Establish communication queues
    # ('overview', ) or ('find', '{item name}') ('location', )
    objDetectionTasks = multiprocessing.Queue()
    speechToTextTasks = multiprocessing.Queue()
    textToSpeechTasks = multiprocessing.Queue()
    locatorTasks = multiprocessing.Queue()
    workerSpeech2Txt = multiprocessing.Process(
    	name='speech to text'
    	, target=speech2text_node.start_node
    	, args=(speechToTextTasks, objDetectionTasks, locatorTasks, textToSpeechTasks)
    )
    workerTxt2Speech = multiprocessing.Process(
    	name='text to speech'
    	, target=text2speech_node.start_node
    	, args=(textToSpeechTasks,)
    )
    workerLocator = multiprocessing.Process(
    	name='locator'
    	, target=locator_node_cp.start_node
    	, args=(locatorTasks, textToSpeechTasks)
    )

    try:
        workerSpeech2Txt.start()
        workerTxt2Speech.start()
        workerLocator.start()

        realsense_node.start_node(objDetectionTasks, textToSpeechTasks)
    finally:
        objDetectionTasks.put(None)
        speechToTextTasks.put(None)
        textToSpeechTasks.put(None)
        locatorTasks.put(None)

        workerSpeech2Txt.join()
        workerTxt2Speech.join()
        # workerLocator.join()
