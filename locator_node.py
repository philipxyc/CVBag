from subprocess import PIPE, Popen
import json, sys

import multiprocessing, queue

prog = 'findclient.exe'
group = 'geekpietest'

def run_findclient():
    process = Popen(
        args=('echo y | %s -g %s -c 3' % (prog, group)),
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    _, err = process.communicate(input='y\n')
    return err.decode('utf-8')

def track_position():
    output = run_findclient()

    lines = output.split('\n')

    statistics = {}

    for ln in lines:
        if ln.find('sendFingerprint - INFO') < 0:
            continue

        bra_begin = ln.find('{')

        rf_d = json.loads(ln[bra_begin:])['rf']
        for k in rf_d:
            if k not in statistics:				
                statistics[k] = 0

            statistics[k] += rf_d[k]

    print(statistics)
    return max(statistics)

def start_node(task_queue, results_queue):
    try:
        while True:
            task = task_queue.get()
            if task is None:
                break
            else:
                if task[0] == "location":
                    res = list(task)
                    res.append(track_position())
                    results_queue.put(tuple(res))
    except KeyboardInterrupt:
        print("Shutdown locator worker ...")
    finally:
        pass