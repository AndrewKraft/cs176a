import socket
import sys
import time
import random
import subprocess

# general inspiration from https://docs.python.org/3/howto/sockets.html, Author: Gordon McMillan
# specific usage of select from https://pymotw.com/2/select/, Author: Doug Hellmann
# formatting of filename from https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
# https://docs.python.org/3/library/random.html
# https://docs.python.org/3/library/subprocess.html
# https://docs.python.org/3/library/socket.html

HOST = input('Enter server name or IP address: ')
try:
	PORT = int(input('Enter port: '), 10)
except ValueError as e:
	print('Invalid port number')
	exit(0)

if (PORT > 65353) | (PORT < 1024):
	print('Invalid port number.')
	exit(0)

BUFFSIZE = 1500
NUM_CLIENTS = 1
DROP_CHANCE = 0.0

def unreliable_sendto(clientsock, buff, addr):
	if random.random() > DROP_CHANCE:
		clientsock.sendto(buff, addr)
		print('SENT')
	else:
		print('DROPPED')

def run(cmd, length, addr):
	# send command to server
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	for i in range(3):
		try:
			unreliable_sendto(sock, length.encode(), addr)
			unreliable_sendto(sock, cmd.encode(), addr)
			(packet, addr) = sock.recvfrom(BUFFSIZE)
			print('ACK')
			break
		except socket.timeout:
			if i == 2:
				print('Failed to send command. Terminating.')
				sock.close()
				exit(0)
			continue
		except ConnectionError:
			print('Failed to send command. Terminating.')
			sock.close()
			exit(0)

	# vars for receiving command
	bytes_remaining = 0
	msg = []
	last = ''
	# wait for response from server
	while bytes_remaining == 0:
		try:
			(packet, addr) = sock.recvfrom(BUFFSIZE)
		except Exception as e:
			print(e)
			print('Did not receive response.')
			sock.close()
			exit(0)
		try:
			bytes_remaining = int(packet.decode(), 10)
		except ValueError:
			print('Length message not received.')
	while bytes_remaining > 0:
		try:
			(packet, addr) = sock.recvfrom(BUFFSIZE)
		except Exception:
			print('Did not receive response.')
			sock.close()
			exit(0)
		sock.sendto('ACK'.encode(), addr)
		if packet.decode() != last:
			last = packet.decode()
			msg.append(last)
			bytes_remaining -= BUFFSIZE

	# print output to file
	from_server = ''.join(i for i in msg)
	fname = 'client-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
	try:
		with open(fname, 'a') as f:
			f.write(from_server)
	except Exception:
		with open(fname, 'w+') as f:
			f.write(from_server)
	print('File %s saved.' % fname)

addr = (HOST, PORT)
cmd = input('Enter command: ')
length = str(len(cmd))

threads = []
for i in range(NUM_CLIENTS):
	t = subprocess.threading.Thread(target=run,kwargs={'cmd':cmd,'length':length,'addr':addr})
	t.start()
	threads.append(t)

for t in threads:
	t.join()
