import os

# remove multiple files
def removefiles(path, filelist):
	for _file in filelist:
		# remove file
		os.remove(os.path.join(path, _file))

# remove mutiple directories and it's path
def removedirs(path, dirs):
	for _dir in dirs:

		# remove separator
		if _dir[-1] == os.path.sep: 
			_dir = _dir[:-1]

		# nuke the files!
		files = os.listdir(path + _dir)
		for _file in files:
			if _file == '.' or _file == '..': continue
			filepath = os.path.join(_dir, os.sep, _file)
			if os.path.isdir(os.path.join(path, filepath)):
				removedirs(path, filepath)
			else:
				os.unlink(os.path.join(path, filepath))

		#remove dir
		os.rmdir(path + _dir)

# create directory if isn't exist
def createdir(path, directory):
	if not os.path.exists(os.path.join(path, directory)):
	    os.makedirs(os.path.join(path, directory))

