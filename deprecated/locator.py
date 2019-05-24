from subprocess import PIPE, Popen
import json, sys


prog = 'findclient'
group = 'geekpietest'

def run_findclient():
	process = Popen(
		args=('echo y | %s -g %s -c 10' % (prog, group)),
		stdout=PIPE,
		shell=True
	)
	return process.communicate()[0]

def track_position():
	output = run_findclient()
	# output = sys.stdin.read()

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


	return max(statistics)
