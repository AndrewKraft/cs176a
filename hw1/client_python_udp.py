import socket
import sys
import time

HOST = input('Enter server name or IP address: ')
try:
	PORT = int(input('Enter port: '), 10)
except ValueError as e:
	print('Invalid port number')
	exit(0)
NUM_CLIENTS = 1

if (PORT > 65353) | (PORT < 1024):
	print('Invalid port number.')
	exit(0)

clientsocks = []
for i in range(NUM_CLIENTS):
	clientsocks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
for sock in clientsocks:
	try:
		sock.connect((HOST,PORT))
		sock.setblocking(0)
	except socket.error as e:
		print('Could not connect to server.')
		exit(0)

cmd = {}
for sock in clientsocks:
	cmd[sock] = input('Enter command: ')
	cmd[sock] = "%s%s" % (
		'{:08X}'.format(len(cmd[sock])),
		cmd[sock])

for sock in clientsocks:
	sock.settimeout(500)
	try:
		sock.send(cmd[sock].encode())
	except socket.error as e:
		print('Failed to send command. Terminating.')
		del cmd[sock]
		clientsocks.remove(sock)
		sock.close()
if clientsocks is None:
	exit(0)

for sock in clientsocks:
	try:
		inFromServer = sock.recv(8).decode()
		inFromServer = sock.recv(int(inFromServer,16)).decode()
		fname = 'client-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
		with open(fname, 'w+') as f:
			f.write(inFromServer)
			print('File %s saved.' % fname)
	except socket.error as e:
		print('Did not recieve response.')
		del cmd[sock]
		clientsocks.remove(sock)
		sock.close()
if clientsocks is None:
	exit(0)

for sock in clientsocks:
	sock.close()
