import socket
import sys
import json
import os
import time

import osutil

HOST = ''
PORT = 8888
PATH = '/tmp/test_tracking/'

def sendupdate(filelist):
	# open connection to server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))

	# send update message to server
	msg                 = {}
	msg['type']         = 'SENDUPDATE'
	msg['content']         = filelist
	s.send(json.dumps(msg))

	# waiting response from server
	while True:
		responses_str     = s.recv(1024)
		print responses_str
		responses         = json.loads(responses_str)

		# handle file request from server
		if responses['type'] == 'REQFILES':
			_file = open (os.path.join(PATH, responses['content']), "rb")

			# send in packet of 1024 bytes each, with first packet
			# contains file size
			_data = os.path.getsize(os.path.join(PATH, responses['content']))
			while _data != "":
				time.sleep(0.1)
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

	# send update message to server
	msg                 = {}
	msg['type']         = 'CHECKUPDATE'
	msg['content']         = filelist
	s.send(json.dumps(msg))

	# waiting response from server
	while True:
		responses_str     = s.recv(1024)
		try:
			msg             = json.loads(responses_str)
		except:
			msg             = {}
			msg['type']     = "DONE"
			msg['content']  = ''

		if (msg['type'] == "DONE"):
			break

		elif (msg['type'] == 'NEEDUPDATE'):
			update = msg['content']
			# delete
			if update['deleted']:
				osutil.removefiles(PATH, update['deleted'])
				print '- SYNC DELETED :' + str(update['deleted'])

			# update and create basicly same
			if update['created']:
				for _file in update['created']:

					# request the file
					reqmsg              = {}
					reqmsg['type']      = 'REQFILES'
					reqmsg['content']   = _file

					s.send(json.dumps(reqmsg))

					# create subdirectory if needed
					_dir = os.path.dirname(_file)
					if _dir:
						osutil.createdir(PATH, _dir)

					# write the file for each packet sent (1024 bytes each)
					_f          = open(os.path.join(PATH, _file), 'w+b')
					_datasize   = int(s.recv(1024))                      # get data size
					_dataget    = 0
					while _dataget < _datasize:                             # there is data left to get
						_data = s.recv(1024)                             # acquire next packet
						print "SYNC DATA RECEIVED :", _data
						_f.write(_data)                                     # write in binaries

						_dataget += 1024

					 # end writing file
					_f.close()

				print '- SYNC CREATED :' + str(update['created'])

			# update and create basicly same
			if update['updated']:
				for _file in update['updated']:
					# request the file
					reqmsg              = {}
					reqmsg['type']      = 'REQFILES'
					reqmsg['content']   = _file

					s.send(json.dumps(reqmsg))

					# create subdirectory if needed
					_dir = os.path.dirname(_file)
					if _dir:
						osutil.createdir(PATH, _dir)

					# write the file for each packet sent (1024 bytes each)
					_f          = open(os.path.join(PATH, _file), 'w+b')
					_datasize   = int(s.recv(1024))                      # get data size
					_dataget    = 0
					while _dataget < _datasize:                             # there is data left to get
						_data = s.recv(1024)                             # acquire next packet
						_f.write(_data)                                     # write in binaries

						_dataget += 1024

					 # end writing file
					_f.close()

				print '- SYNC UPDATED :' + str(update['updated'])

			# delete directories
			if update['deleted_dirs']:
				print '- SYNC DELETED DIRS :' + str(update['deleted_dirs'])
				osutil.removedirs(PATH, update['deleted_dirs'])

			# send DONE respond to inform client
			msg             = {}
			msg['type']     = 'DONE'
			msg['content']  = ''
			s.send(json.dumps(msg))


	s.close()

# main program starts here
if __name__ == "__main__":
	try:
		# check program arguments
		if len(sys.argv) != 3:
			print "Usage: python client.py <host> <port>"
			quit()

		# monitoring directory
		directory = ''
		if not os.path.isfile('.config'):
			print 'File .config does not exist. Create a new one'
			directory = raw_input('Please write the directory: ')
			config = open('.config', 'w')
			config.write(directory)
			config.close()
			print '.config is successfully created. Your shared directory is', directory

		with open('.config') as f:
			directory = f.read();
			print 'Monitoring directory ', directory

			# get server address
			HOST = sys.argv[1]
			PORT = int(sys.argv[2])

			PATH = directory
			old = osutil.index(PATH)

			while True:
				new = osutil.index(PATH)
				difference = osutil.diff(new, old)

				for x in difference:
					if difference[x]:
						old = new
						print 'Update detected!'
						sendupdate(difference)
						break

				checkupdate(new)

				time.sleep(0.1)
	except KeyboardInterrupt:
		print('\nKeyboard interrupt detected. Exiting gracefully...\n')
		quit()
