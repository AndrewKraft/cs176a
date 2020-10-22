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
DROP_CHANCE = 0.1

def unreliable_sendto(clientsock, buff, addr):
	if random.random() > DROP_CHANCE:
		clientsock.sendto(buff, addr)
		print('SENT')
	else:
		print('DROPPED')

class Client():
	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.cmd = ''
		self.bytes_remaining = 0
		self.msg = []
		self.last = ''

	def send_to_server(self, addr):
		self.sock.settimeout(1)
		for i in range(3):
			try:
				unreliable_sendto(self.sock, str(len(self.cmd)).encode(), addr)
				unreliable_sendto(self.sock, self.cmd.encode(), addr)
				(packet, addr) = self.sock.recvfrom(BUFFSIZE)
				print('ACK')
				break
			except socket.timeout:
				if i == 2:
					print('Failed to send command. Terminating.')
					self.sock.close()
					exit(0)
				continue
			except ConnectionError:
				print('Failed to send command. Terminating.')
				self.sock.close()
				exit(0)
	
	def get_server_response(self):
		while self.bytes_remaining == 0:
			try:
				(packet, addr) = recvfrom(BUFFSIZE)
			except Exception:
				print('Did not recieve response.')
				self.sock.close()
				exit(0)
			try:
				self.bytes_remaining = int(packet.decode(), 10)
			except ValueError:
				print('Length message not recieved.')
		while self.bytes_remaining > 0:
			try:
				(packet, addr) = sock.recvfrom(BUFFSIZE)
			except Exception:
				print('Did not recieve response.')
				self.sock.close()
				exit(0)
			self.sock.sendto('ACK'.decode(), addr)
			if packet.decode() != self.last:
				self.last = packet.decode()
				self.msg.append(last)
				self.bytes_remaining -= BUFFSIZE
	def print_to_file(self):
		from_server = ''.join(i for i in self.msg)
		fname = 'client-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
		with open(fname, 'w+') as f:
			f.write(from_server)
		print('File %s saved.' % fname)
	def run(self, addr):
		print('sending...')
		self.send_to_server(addr)
		print('waiting for response...')
		self.get_server_response()
		print('outputting response to file...')
		self.print_to_file()

addr = (HOST, PORT)
client = Client()
client.cmd = input('Enter command: ')
client.run(addr)
