import socket
import sys

# lots of inspiration from https://docs.python.org/3/howto/sockets.html
if len(sys.argv) > 1:
	PORT = sys.argv[1]
	if PORT < 1024 | PORT > 
else:
	PORT = 6969
HOST = ''
# code from https://docs.python.org/3/library/socket.html creates nonblocking tcp socket
serversocket = socket.socket(
	socket.AF_INET,
	socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
serversocket.bind((HOST, PORT))
server.sock.listen(5)

while true:
	(clientsocket, address) = serversocket.accept()

	