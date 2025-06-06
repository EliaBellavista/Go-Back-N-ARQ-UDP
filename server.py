import random
import time, socket, sys

#TODO
# magari un check di ip + porta?

address = ('localhost', 12345)
window = 8
received = [] 
next = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 12345))

print("in attesa di client")
data, address = sock.recvfrom(4096)

while True:
    time.sleep(0.3)  # tempo di elaborazione
    # con il timer inseruto nel client, aumentare ulteriormente il delay inizia a creare problemi
    # come perdita di pacchetti e ricezioni out of order
    try:
        data, address = sock.recvfrom(4096)
    except Exception as e:
        print("Errore durante la ricezione dei dati: ", e)
        continue
    seqN = data[0]
    payload = data[1:]

    if not(random.randint(0, 7)):  # 1/8 di probabilità di perdere il pacchetto
        print("simulazione pacchetto perso, seqN: %s" % data)
        continue

    if seqN == next:
        if payload == b'\xff':
            break

        payload = payload.decode('utf8')
        print("received : %s, next: %d" % (seqN, next))
        received.append(payload)
        next = (next + 1) % window
    else:
        print("received out of order packet: %s, expected: %d" % (seqN, next))

    sock.sendto(str(next).encode(), address) #ack 
    
print(''.join(received))
print("received all packets, closing server")
sock.sendto(str(next).encode(), address)
sock.close()
sys.exit(0)