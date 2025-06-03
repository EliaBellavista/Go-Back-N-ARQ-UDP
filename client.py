import time, socket, sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 12345)
window = 8

ack = 1

while True:
    sock.sendto(ack.encode(), address)
    data, address = sock.recvfrom(4096)

