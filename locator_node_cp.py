from subprocess import PIPE, Popen
import json, sys
import requests
import multiprocessing, queue

family_code = 'GeekPie4'

def get_location():
    res = requests.get('https://cloud.internalpositioning.com/api/v1/location/%s/jetson' % family_code)

    locations_probs = res.json()['analysis']['guesses']

    if len(locations_probs) == 0:
        return 'None'
    elif 'probability' not in locations_probs[0]:
        return 'None'
    elif locations_probs[0]['probability'] < 0.4:
        return 'Not Sure'
    else:
        return locations_probs[0]['location']


def start_node(task_queue, results_queue):
    try:
        while True:
            task = task_queue.get()
            if task is None:
                break
            else:
                if task[0] == "location":
                    res = list(task)
                    res.append(get_location())
                    results_queue.put(tuple(res))
                    print(tuple(res))
    except KeyboardInterrupt:
        print("Shutdown locator worker ...")
    finally:
        pass



    





