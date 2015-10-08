import socket
import sys
import json
import os
import thread
import time

import osutil

HOST = ''
PORT = 8888
PATH = '/tmp/test_trackin/'

def sendupdate(filelist, conn):

	# send update message to client
	msg                 = {}
	msg['type']         = 'NEEDUPDATE'
	msg['content']      = filelist
	conn.send(json.dumps(msg))

	# waiting response from client
	while True:
		responses_str   = conn.recv(1024)
		# print responses_str
		responses       = json.loads(responses_str)

		# handle file request from client
		if responses['type'] == 'REQFILES':
			_file = open (os.path.join(PATH, responses['content']), "rb")

			# send in packet of 1024 bytes each, with first packet
			# contains file size
			_data = os.path.getsize(os.path.join(PATH, responses['content']))
			while _data != '':
				print 'SENDING DATA :', str(_data)
				conn.send(str(_data))
				_data = _file.read(1024)

			_file.close()

		# when client done, end waiting
		if responses['type'] == 'DONE':
			break

# client thread function
def clientthread(conn):

	while True:
		msg_str = conn.recv(1024)

		try:
			msg             = json.loads(msg_str)
		except:
			msg             = {}
			msg['type']     = "DONE"
			msg['content']  = ''

		# respond based on type
		# receive update from client
		if (msg['type'] == 'SENDUPDATE'):
			update = msg['content']
			# update the folder based on client update
			# some functions are from osutil.py

			# delete
			if update['deleted']:
				osutil.removefiles(PATH, update['deleted'])
				print '- DELETED :' + str(update['deleted'])

			# update and create basicly same
			if update['created']:
				for _file in update['created']:

					# request the file
					reqmsg              = {}
					reqmsg['type']      = 'REQFILES'
					reqmsg['content']   = _file

					conn.send(json.dumps(reqmsg))

					# create subdirectory if needed
					_dir = os.path.dirname(_file)
					if _dir:
						osutil.createdir(PATH, _dir)

					# write the file for each packet sent (1024 bytes each)
					_f          = open(os.path.join(PATH, _file), 'w+b')
					_datasize   = int(conn.recv(1024))                      # get data size
					_dataget    = 0
					while _dataget < _datasize:                             # there is data left to get
						_data = conn.recv(1024)                             # acquire next packet
						print "DATA RECEIVED :", _data
						_f.write(_data)                                     # write in binaries

						_dataget += 1024

					 # end writing file
					_f.close()

				print '- CREATED :' + str(update['created'])

			# update and create basicly same
			if update['updated']:
				for _file in update['updated']:
					# request the file
					reqmsg              = {}
					reqmsg['type']      = 'REQFILES'
					reqmsg['content']   = _file

					conn.send(json.dumps(reqmsg))

					# create subdirectory if needed
					_dir = os.path.dirname(_file)
					if _dir:
						osutil.createdir(PATH, _dir)

					# write the file for each packet sent (1024 bytes each)
					_f          = open(os.path.join(PATH, _file), 'w+b')
					_datasize   = int(conn.recv(1024))                      # get data size
					_dataget    = 0
					while _dataget < _datasize:                             # there is data left to get
						_data = conn.recv(1024)                             # acquire next packet
						_f.write(_data)                                     # write in binaries

						_dataget += 1024

					 # end writing file
					_f.close()

				print '- UPDATED :' + str(update['updated'])

			# delete directories
			if update['deleted_dirs']:
				print '- DELETED DIRS :' + str(update['deleted_dirs'])
				osutil.removedirs(PATH, update['deleted_dirs'])

			# send DONE respond to inform client
			msg             = {}
			msg['type']     = 'DONE'
			msg['content']  = ''

			conn.send(json.dumps(msg))

		# receive update from client
		elif (msg['type'] == 'CHECKUPDATE'):
			servercontent = osutil.index(PATH)
			difference = osutil.diff(servercontent, msg['content'])

			for x in difference:
				if difference[x]:
					print 'Update on server detected!'
					sendupdate(difference, conn)
					break
			msg             = {}
			msg['type']     = 'DONE'
			msg['content']  = ''

			conn.send(json.dumps(msg))

# main program starts here
if __name__ == "__main__":

	try:

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

		PATH = directory

		# create socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		youstupid = True
		while youstupid:
			try:
				print "Please insert host number:",
				HOST = raw_input()
				print "Please insert port number:",
				PORT = int(raw_input())
				# bind
				s.bind((HOST, PORT))
				youstupid = False
			except socket.error, msg:
				if msg[0] == 13:
					print "Error: Port is unusable.\n"
				elif msg[0] == 99:
					print "Error: Cannot assign requested host.\n"
			except ValueError:
				print "Error: Port must be a number.\n"

		# listen
		s.listen(10)
		print 'Server opened on on host', HOST, 'port ' + str(PORT)
		print 'Server ready, now listening ...'

		# response request
		while True:
			conn, addr = s.accept()
			print 'Connection from ' + addr[0] + ':' + str(addr[1])

			# create thread
			thread.start_new_thread(clientthread, (conn,))
	except KeyboardInterrupt:
		print('\nKeyboard interrupt detected. Exiting gracefully...\n')
		quit()
