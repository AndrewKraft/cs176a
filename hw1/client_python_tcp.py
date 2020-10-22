import socket
import time
import subprocess

# general inspiration from https://docs.python.org/3/howto/sockets.html, Author: Gordon McMillan
# formatting of filename from https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
# https://docs.python.org/3/library/random.html
# https://docs.python.org/3/library/subprocess.html
# https://docs.python.org/3/library/socket.html

NUM_CLIENTS = 1
HOST = input('Enter server name or IP address: ')
try:
	PORT = int(input('Enter port: '), 10)
except ValueError as e:
	print('Invalid port number.')
	exit(0)
	
if (PORT > 65353) | (PORT < 1024):
	print('Invalid port number.')
	exit(0)
addr = (HOST, PORT)

def run(cmd, sock):
	try:
		sock.settimeout(1)
		sock.send(cmd.encode())
	except socket.error:
		print('Failed to send command. Terminating.')
		sock.close()
		return 0
	
	try:
		from_server = sock.recv(8).decode()
		from_server = sock.recv(int(from_server, 16)).decode()
		
		fname = 'client-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
		try:
			with open(fname, 'a') as f:
				f.write(from_server)
		except Exception:
			with open(fname, 'w+') as f:
				f.write(from_server)
		print('File %s saved.' % fname)
	except socket.error:
		print('Did not receive response.')
		sock.close()
		return 0

sockets = []
for i in range(NUM_CLIENTS):
	sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

for sock in sockets:
	try:
		sock.connect(addr)
	except socket.error:
		print('Could not connect to server.')
		sock.close()
		sockets.remove(sock)

if not sockets:
	exit(0)

cmd = input('Enter command: ')
cmd = '{:08X}{}'.format(len(cmd), cmd)

threads = []
for i in range(NUM_CLIENTS):
	t = subprocess.threading.Thread(target=run, kwargs={'cmd': cmd, 'sock': sockets[i]})
	t.start()
	threads.append(t)

for t in threads:
	t.join()