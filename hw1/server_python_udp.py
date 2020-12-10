import socket
import subprocess
import time
import sys

# https://stackoverflow.com/questions/4067786/checking-on-a-thread-remove-from-list
# https://docs.python.org/3/library/threading.html
# general inspiration from https://docs.python.org/3/howto/sockets.html, Author: Gordon McMillan
# formatting of filename from https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
# https://docs.python.org/3/library/random.html
# https://docs.python.org/3/library/subprocess.html
# https://docs.python.org/3/library/socket.html


class Client():
	def __init__(self, bytes_not_recieved):
		self.bytes_not_recieved = bytes_not_recieved
		self.msg = []
		self.last = ''
		self.last_accessed = time.time()

	def send(self, data, addr):
		bytes_remaining = len(data)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.settimeout(1)

		# send len and first bit of message 3 times
		sendl = min(bytes_remaining, BUFFSIZE)
		for i in range(3):
			try:	
				sock.sendto(str(bytes_remaining).encode(), addr)
				sock.sendto(data[:sendl], addr)
				(packet, addr) = sock.recvfrom(BUFFSIZE)
				print('ACK')
				bytes_remaining -= sendl
				break
			except socket.timeout:
				if i == 2:
					print('File transmission failed.')
					sock.close()
					return 0
				continue
			except ConnectionError:
				print('Client unexpectedly disconnected.')
				sock.close()
				return 0

		# send remaining packets of message
		while bytes_remaining != 0:
			data = data[sendl+1:]
			sendl = min(bytes_remaining, BUFFSIZE)
			for i in range(3):
				try:
					sock.sendto(data[:sendl], addr)
					(packet, addr) = sock.recvfrom(BUFFSIZE)
					print('ACK')
					bytes_remaining -= sendl
					break
				except socket.timeout:
					if i == 2:
						print('File transmission failed.')
						sock.close()
						return 0
					continue
				except ConnectionError:
					print('Client unexpectedly disconnected.')
					sock.close()
					return 0
		sock.close()
		return 1

	def send_response(self, addr):
		# start by turning msg into string
		cmd = ''.join(i for i in self.msg)

		# run command, create file and write output
		result = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		fname = 'server-' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
		try:
			with open(fname, 'a') as f:
				f.write(result.stdout)
		except FileNotFoundError:
			with open(fname, 'w+') as f:
				f.write(result.stdout)
		
		with open(fname, 'r') as f:
			msg_to_client = f.read()
		
		#send output to client
		self.send(msg_to_client.encode(), addr)

PORT = 3300
HOST = ''
BUFFSIZE = 1500

if len(sys.argv) > 1:
	try:
		PORT = int(sys.argv[1], 10)
	except ValueError as e:
		print('Invalid port number')
		exit(0)
	if (PORT < 1024) | (PORT > 65535):
		print('Invalid port number.')
		exit(0)

serversocket = socket.socket(
	socket.AF_INET,
	socket.SOCK_DGRAM)
serversocket.bind((HOST, PORT))

clients = {}
addrs = []
threads = []

while 1:
	# listen for incoming packet
	try:
		serversocket.settimeout(0.5)
		(packet, addr) = serversocket.recvfrom(BUFFSIZE)
	except socket.timeout:
		# if more than 500 milliseconds pass between 2 messages, all current clients have timed out
		addrs = []
		clients = {}
		if threads:
			for t in threads:
				t.join()
			threads = []
		continue

	# if no previous packet from address 'addr', create a new Client and add it to map
	if addr not in clients:
		try:
			clients[addr] = Client(int(packet.decode(), 10))
			addrs.append(addr)
		except ValueError:
			print('No length message recieved from (\'%s\', %s)' % addr)
			continue

	# else, we are receiving message packets, and should send ack and add them to the command list
	else:
		try:
			serversocket.sendto('ACK'.encode(), addr)
			clients[addr].last_accessed = time.time()
		except ConnectionError:
			print('Client unexpectedly closed or was shutdown')
			del clients[addr]
			addrs.remove(addr)
			continue
		# check to make sure not a dupe command, then add to msg
		if packet.decode() != clients[addr].last:
			clients[addr].last = packet.decode()
			clients[addr].msg.append(clients[addr].last)
			clients[addr].bytes_not_recieved -= BUFFSIZE
		
		# if we have recieved the full message, create a new thread to run the command, log the output and send it to the client
		if clients[addr].bytes_not_recieved <= 0:
			client = clients[addr]
			del clients[addr]
			addrs.remove(addr)
			t = subprocess.threading.Thread(target=client.send_response, kwargs={'addr':addr})
			t.start()
			threads.append(t)
	
	# iterate through clients and remove those which have timed out
	timeout = time.time() - 0.5
	for addr in addrs:
		if clients[addr].last_accessed < timeout:
			print('Failed to receive instructions from the client.')
			del clients[addr]
			addrs.remove[addr]

	# remove threads which have completed transmission back to client
	threads = [t for t in threads if t.is_alive()]
