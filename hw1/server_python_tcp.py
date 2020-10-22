import select
import socket
import sys
import subprocess
import time

# general inspiration from https://docs.python.org/3/howto/sockets.html, Author: Gordon McMillan
# specific usage of select from https://pymotw.com/2/select/, Author: Doug Hellmann
# formatting of filename from https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
# https://docs.python.org/3/library/random.html
# https://docs.python.org/3/library/subprocess.html
# https://docs.python.org/3/library/socket.html

PORT = 3300
if len(sys.argv) > 1:
	try:
		PORT = int(sys.argv[1], 10)
	except ValueError as e:
		print('Invalid port number.')
		exit(0)
	if (PORT < 1024) | (PORT > 65353):
		print('Invalid port number.')
		exit(0)
HOST = ''

serversocket = socket.socket(
	socket.AF_INET,
	socket.SOCK_STREAM)
serversocket.settimeout(500)

serversocket.bind((HOST, PORT))

serversocket.listen(5)
print('socket listening on %s port %s' % (HOST, PORT))

inputs = [serversocket]
outputs = []

cmd = {} # socket to string


while inputs:
	print('%s current connections' % (len(inputs)-1))

	readable, writeable, errors = select.select(inputs, outputs, inputs)
	for sock in readable:
		if sock is serversocket:
			(clientsock, address) = sock.accept()
			clientsock.setblocking(500)

			print('connecting to client (\'%s\', %s)' % address)
			inputs.append(clientsock)
			cmd[clientsock] = ''
		else:
			try:
				data = sock.recv(8)
				if data:
					print('recieved %s bytes from %s' % (data.decode(), sock.getpeername()))
					cmd[sock] = sock.recv(int(data.decode(), 16)).decode()
					if sock not in outputs:
						outputs.append(sock)
				else:
					print('Disconnecting from client %s' % (sock.getpeername()))
					if sock in outputs:
						outputs.remove(sock)
					inputs.remove(sock)
					del cmd[sock]
					sock.close()
			except socket.timeout:
				print('Connection to %s timed out.' % sock.getpeername())
				if sock in outputs:
					outputs.remove(sock)
				inputs.remove(sock)
				del cmd[sock]
				sock.close()
	for sock in writeable:
		result = subprocess.run(cmd[sock], shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		fname = 'server-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
		outToClient = ''
		with open(fname, 'w+') as f:
			f.write(result.stdout)
		with open(fname) as f:
			outToClient = f.read()

		outToClient = '%s%s' % ('{:08X}'.format(len(outToClient)), outToClient)
		try:
			sock.send(outToClient.encode())
		except socket.timeout:
			print('Connection to %s timed out.' % sock.getpeername())
			inputs.remove(sock)
			sock.close()
		outputs.remove(sock)
		cmd[sock] = ''
	for sock in errors:
		if sock in outputs:
			outputs.remove(sock)
		inputs.remove(sock)
		del cmd[sock]
		sock.close()

			
