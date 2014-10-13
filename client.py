import os, socket, sys, time, json

def index(path):
	""" Return a tuple containing:
	- list of files (relative to path)
	- list of subdirs (relative to path)
	- a dict: filepath => last modified
	"""
	files = []
	subdirs = []
	for root, dirs, filenames in os.walk(path):
		for subdir in dirs:
			subdirs.append(os.path.relpath(os.path.join(root, subdir), path))
		for f in filenames:
			files.append(os.path.relpath(os.path.join(root, f), path))
	index = {}
	for f in files:
		index[f] = os.path.getmtime(os.path.join(path, f))
	
	return dict(files=files, subdirs=subdirs, index=index)

def diff(dir_base, dir_cmp):
	data = {}
	data['deleted'] = list(set(dir_cmp['files']) - set(dir_base['files']))
	data['created'] = list(set(dir_base['files']) - set(dir_cmp['files']))
	data['updated'] = []
	data['deleted_dirs'] = list(set(dir_cmp['subdirs']) - set(dir_base['subdirs']))
	for f in set(dir_cmp['files']).intersection(set(dir_base['files'])):
		if dir_base['index'][f] != dir_cmp['index'][f]:
			data['updated'].append(f)
	return data

def send_update(list):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send(json.dumps(list))
	# responses_str = s.recv(1024)
	# responses = json.loads(responses_str)
	# for response in responses:
	# 	command = response['command']
	# 	if command == 'delete':
	# 		continue
	# 	else:
	# 		filenames = response['filename']
			# ngirim file
	s.close()

def check_for_update(list):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	# s.send(json.dumps(list))
	# to do

	s.close()

HOST = ''
PORT = 8888

# main program starts here
if __name__ == "__main__":

	# check program arguments
	if len(sys.argv) != 3:
		print "Usage: python client.py <host> <port>"
		sys.exit

	# get server address
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	PATH = '/tmp/test_tracking'
	
	old = index(PATH)

	while True:
		new = index(PATH)
		difference = diff(new, old)

		for x in difference:
			if difference[x]:
				old = new
				print 'Update detected!'
				send_update(difference)
				break

		# check_for_update(difference)

		time.sleep(0.1)
