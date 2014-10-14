import socket
import sys
import json
import os
import time
import sys

# remove multiple files
def removefiles(path, filelist):
	for _file in filelist:
		# remove file
		try:
			os.remove(os.path.join(path, _file))
		except OSError:
			pass

# remove mutiple directories and it's path
def removedirs(path, dirs):
	for _dir in dirs:

		# remove separator
		if _dir[-1] == os.path.sep: 
			_dir = _dir[:-1]

		# nuke the files!
		try:
			files = os.listdir(os.path.join(path, _dir))
			for _file in files:
				if _file == '.' or _file == '..': continue
				filepath = os.path.join(_dir, _file)
				if os.path.isdir(os.path.join(path, filepath)):
					removedirs(path, filepath)
				else:
					os.unlink(os.path.join(path, filepath))
		except:
			pass
			
		#remove dir
		os.rmdir(os.path.join(path, _dir))

# create directory if isn't exist
def createdir(path, directory):
	if not os.path.exists(os.path.join(path, directory)):
		os.makedirs(os.path.join(path, directory))

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
			try: 
				subdirs.append(os.path.relpath(os.path.join(root, subdir), path))
			except OSError:
				pass
		for f in filenames:
			try:
				files.append(os.path.relpath(os.path.join(root, f), path))
			except OSError:
				pass    
	index = {}
	for f in files:
		try:
			index[f] = os.path.getsize(os.path.join(path, f))
		except OSError:
				pass

	return dict(files=files, subdirs=subdirs, index=index)

def diff(dir_base, dir_cmp):
	data = {}
	data['deleted'] = list(set(dir_cmp['files']) - set(dir_base['files']))
	data['created'] = list(set(dir_base['files']) - set(dir_cmp['files']))
	data['updated'] = []
	data['deleted_dirs'] = list(set(dir_cmp['subdirs']) - set(dir_base['subdirs']))
	for f in set(dir_cmp['files']).intersection(set(dir_base['files'])):
		try:
			if dir_base['index'][f] != dir_cmp['index'][f]:
				data['updated'].append(f)
		except:
			pass
	return data

# if sys.platform.lower().startswith('linux') :
# 	import fcntl
# 	import struct

# 	def get_ip_address(ifname):
# 	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 	    return socket.inet_ntoa(fcntl.ioctl(
# 	        s.fileno(),
# 	        0x8915,  # SIOCGIFADDR
# 	        struct.pack('256s', ifname[:15])
# 	    )[20:24])
