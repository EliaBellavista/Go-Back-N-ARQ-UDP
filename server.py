#TODO
#il server deve: inviare fino a riempimento finestra
#aspettare gli ack per andare avanti o ripartire dala perdita
#se riparto e avevo già settato timer o acks, devo azzerarli

#TODO
# magari un check di ip + porta
#magari un thread per ogni client?

import time, socket, sys
import threading

window = 8
max_window = 16
timeout = 1
lock = threading.Lock()
sent_window = {} 
SeqN = 0
delay = 0.5


def is_newer(seq1, seq2): #treu if seq1 is newer than seq2
    return (0 < (seq1 - seq2) % max_window <= max_window // 2)

def elaborate_ACKS(socket):
    print("hello from ack thread")
    global delay
    while True:
        try:
            time.sleep(0.3)  # sleep to avoid busy waiting
            ack, address = socket.recvfrom(4096)
            ack = ack.decode('utf8')
            ack = int(ack)
            print("received ack: %s" % ack)
            with lock:
                if ack in sent_window:
                    keys = list(sent_window.keys())
                    for i in keys:
                        if is_newer(ack, i):
                            del sent_window[i]
                    delay = max(0.01, delay * 0.9)
                else:
                    delay = min(1, delay * 1.5)
                
        except Exception as e:
            print("Error receiving ACK: ", e)
            continue

print("server started")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 12345))
print("socket binded")

#thread per ricevere ack mentre invio pacchetti
print("starting ack receiving thread")
thread_ack = threading.Thread(target=elaborate_ACKS, args=(sock,))
thread_ack.daemon = True
thread_ack.start()
print("started ack receiving thread")

print("in attesa di client")
data, address = sock.recvfrom(4096)
#window = data.decode('utf8')


while True:
    print("inizio invio finestra")
    while len(sent_window) < window: #continua finchè c`è spazio nella finestra
        print("delay: %f" % delay)
        time.sleep(delay)
        print("invio pacchetto : %d" % SeqN)
        sock.sendto(str(SeqN).encode(), address)
        with lock:
            sent_window[SeqN] = time.time()
        SeqN = (SeqN + 1) % max_window
    print("finestra comleta, check timeout")
    print("finestra inviata: %s" % str(sent_window))
    #check timeout
    with lock:
        now = time.time()
        for seq in list(sent_window.keys()):
            if now - sent_window[seq] > timeout:
                print("timeout per il pacchetto con seq: %d" % seq)
                sent_window = {} #resetto tutta la finestra
                SeqN = seq
                break
    time.sleep(0.4)


'''
go back N
ack a ogni ricezione, contenente il numero di sequenza che ci si aspetta di ricevere.
la ritrasmissione parte al timeout, non al ricevimento dell'ack
al ricevimento di un ack che fa scorrere la finestra, invio il pacchetto più nuovo
'''