import time, socket, sys

address = ('localhost', 12345)
window = 16
received = [] 
next = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("hello")
sock.sendto(str(window).encode(), address)

while True:
    time.sleep(0.4)  # rallento il client a scopo didaatico
    data, address = sock.recvfrom(4096)
    data = data.decode('utf8')
    if int(data) == next:
        print("received : %s, next: %d" % (data, next))
        received.append(data)
        next = (next + 1) % window
    else:
        print("received out of order packet: %s, expected: %d" % (data, next))
    
    #invio ack
    sock.sendto(str(next).encode(), address)

#TODO timeout
