import socket, sys

HOST = ''
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

while True:
	conn, addr = s.accept()
	msg = conn.recv(1024)
	print msg
