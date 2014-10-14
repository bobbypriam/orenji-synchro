import socket
import sys
import json
import os
import time

import osutil

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

def sendupdate(filelist):
	# open connection to server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))

	# send update message to server
	msg 				= {}
	msg['type'] 		= 'SENDUPDATE'
	msg['content'] 		= filelist
	s.send(json.dumps(msg))

	# waiting response from server
	while True:
		responses_str 	= s.recv(1024)
		print responses_str
		responses 		= json.loads(responses_str)

		# handle file request from server
		if responses['type'] == 'REQFILES':
			_file = open (os.path.join(PATH, responses['content']), "rb") 

			# send in packet of 1024 bytes each, with first packet 
			# contains file size
			_data = os.path.getsize(os.path.join(PATH, responses['content'])) - 1
			while _data:
				print 'SENDING DATA :', str(_data)
				s.send(str(_data))
				_data = _file.read(1024)

			_file.close()

		# when server done, end waiting
		if responses['type'] == 'DONE':
			break

	# conection done
	s.close()

def checkupdate(filelist):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	# s.send(json.dumps(list))
	# to do

	s.close()

HOST = ''
PORT = 8888
PATH = ''

# main program starts here
if __name__ == "__main__":

	# check program arguments
	if len(sys.argv) != 3:
		print "Usage: python client.py <host> <port>"
		quit()
	
	# monitoring directory
	err = 'File config.txt does not exist. Create a new one.';
	
	if not os.path.isfile('config.txt'):
		print err
	else:
		with open('config.txt') as f:
			directory = f.read();
			print 'Monitoring directory ', directory
			# apakah ada sejumlah n+1 config.txt jika ada n client dan 1 server? kemudian client mengirimkan config.txt ke server dan dicocokkan apakah sama?
			# isi config selain direktori, termasuk file-filenya nggak? soalnya aku mikirnya file-file sudah di-handle di difference...?
			# masih bingung >_<
			
			# get server address
			HOST = sys.argv[1]
			PORT = int(sys.argv[2])
			
			PATH = directory
			#PATH = 'C:\Users\Lenovo Z480\Documents\UI Semester 5\Jaringan Komputer\Temp'
			old = index(PATH)

			while True:
				new = index(PATH)
				difference = diff(new, old)

				for x in difference:
					if difference[x]:
						old = new
						print 'Update detected!'
						sendupdate(difference)
						break

				# check_for_update(difference)

				time.sleep(0.1)
