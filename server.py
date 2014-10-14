import socket
import sys
import json
import os
import thread

import osutil

# configuration
HOST = ''
PORT = 8888
PATH = '/tmp/test_trackin/'

# main program starts here
if __name__ == "__main__":

	# create socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# bind
	s.bind((HOST, PORT))

	# listen
	s.listen(10)
	print 'Server opened on port ' + str(PORT)
	print 'Server ready, now listening ...'

	# client thread function
	def clientthread(conn):

		while True:
			msg_str = conn.recv(1024)

			try:
				msg 			= json.loads(msg_str)
			except:
				msg 			= {}
				msg['type'] 	= "DONE"
				msg['content'] 	= ''

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
						reqmsg 				= {}
						reqmsg['type'] 		= 'REQFILES'
						reqmsg['content'] 	= _file

						conn.send(json.dumps(reqmsg))

						# create subdirectory if needed
						_dir = os.path.dirname(_file)
						if _dir:
							osutil.createdir(PATH, _dir)

						# write the file for each packet sent (1024 bytes each)
						_f 			= open(os.path.join(PATH, _file), 'wb')
						_datasize 	= int(conn.recv(1024))						# get data size
						_dataget 	= 0
						while _dataget < _datasize:								# there is data left to get
							_data = conn.recv(1024)								# acquire next packet
							print "DATA RECEIVED :", _data
							_f.write(_data)										# write in binaries

							_dataget += 1024 

						 # end writing file
						_f.close()

					print '- CREATED :' + str(update['created'])

				# update and create basicly same
				if update['updated']:
					for _file in update['updated']:
						# request the file
						reqmsg 				= {}
						reqmsg['type'] 		= 'REQFILES'
						reqmsg['content'] 	= _file

						conn.send(json.dumps(reqmsg))

						# create subdirectory if needed
						_dir = os.path.dirname(_file)
						if _dir:
							osutil.createdir(PATH, _dir)

						# write the file for each packet sent (1024 bytes each)
						_f 			= open(os.path.join(PATH, _file), 'wb')
						_datasize 	= int(conn.recv(1024))						# get data size
						_dataget 	= 0
						while _dataget < _datasize:								# there is data left to get
							_data = conn.recv(1024)								# acquire next packet
							_f.write(_data)										# write in binaries

							_dataget += 1024

						 # end writing file
						_f.close()

					print '- UPDATED :' + str(update['updated'])

				# delete directories
				if update['deleted_dirs']:
					print '- DELETED DIRS :' + str(update['deleted_dirs'])
					osutil.removedirs(PATH, update['deleted_dirs'])

				# send DONE respond to inform client 
				msg 			= {}
				msg['type'] 	= 'DONE'
				msg['content'] 	= ''

				conn.send(json.dumps(msg))

			# other type msg HERE

	# response request
	while True:
		conn, addr = s.accept()
		print 'Connection from ' + addr[0] + ':' + str(addr[1])

		# create thread 
		thread.start_new_thread(clientthread, (conn,))

	


