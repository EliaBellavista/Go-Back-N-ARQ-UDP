import time, socket, sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('localhost', 12345))
window = 1

while True:
    data, address = sock.recvfrom(4096)
    window = data.decode('utf8')
    while True:
        for i in range(window):
            data1 = i
            sock.sendto(data1.encode(), address)


'''
go back N
ack a ogni ricezione, contenente il numero di sequenza che ci si aspetta di ricevere.
la ritrasmissione parte al timeout, non al ricevimento dell'ack
al ricevimento di un ack che fa scorrere la finestra, invio il pacchetto più nuovo
'''