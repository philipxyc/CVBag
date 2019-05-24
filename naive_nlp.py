CMD_KWS = [
	('what', 'in', 'front')  # what is in front of me
	('where', 'am', 'i')  # where am i
]

def naive_nlp(mq, text):
	tokens = text.split()

	for i, kws in enumerate(CMD_KWS):
		matched = 0
		for token in tokens:
			if token in kws:
				matched += 1

		if matched == len(kws):
			mq.put({ 'cmd_id': 0 })

