import multiprocessing
import realsense_node
import speech2text_node
import text2speech_node

if __name__ == '__main__':
    # Establish communication queues
    objDetectionTasks = multiprocessing.Queue()
    objDetectionResults = multiprocessing.Queue()
    speechToTextTasks = multiprocessing.Queue()
    navTasks = multiprocessing.Queue()
    navResults = multiprocessing.Queue()

    workerSpeech2Txt = multiprocessing.Process(
    	name='speech to text'
    	, target=speech2text_node.start_node
    	, args=(speechToTextTasks, objDetectionTasks, objDetectionResults, navTasks, navResults)
    )
    workerSpeech2Txt.start()

    realsense_node.start_node(objDetectionTasks, objDetectionResults)