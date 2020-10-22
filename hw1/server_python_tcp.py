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

def run(sock):
	cmd = ''
	try:
		from_client = sock.recv(8).decode()
		# if len message recd, settimeout to 500ms and wait for cmd
		sock.settimeout(0.5)
		from_client = sock.recv(int(from_client, 16)).decode()
	except socket.timeout:
		print('Failed to receive instructions from the client.')
		sock.close()
		return 0
	
	result = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	fname = 'server-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
	to_client = ''
	try:
		with open(fname, 'a') as f:
			f.write(result.stdout)
	except Exception:
		with open(fname, 'w+') as f:
			f.write(result.stdout)
	with open(fname) as f:
		to_client = f.read()

	to_client = '{:08X}{}'.format(len(cmd), cmd)
	try:
		sock.settimeout(1)
		sock.send(to_client.encode())
	except socket.timeout:
		print('File trainsfer failed.')
		sock.close()
		return 0
	sock.close()
	return 1
	

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
serversocket.settimeout(0.5)

serversocket.bind((HOST, PORT))

serversocket.listen(5)
print('socket listening on %s port %s' % (HOST, PORT))

threads = []
while 1:
	try:
		serversocket.settimeout(1)
		(sock, addr) = serversocket.accept()
		t = subprocess.threading.Thread(target=run, kwargs={'sock':sock})
		t.start()
		threads.append(t)
	except socket.timeout:
		for t in threads:
			t.join()
		threads = []
	except ConnectionError:
		print('Failed to connect to client.')
		continue

	# remove threads which have finished
	t = [t for t in threads if t.is_alive()]
			
