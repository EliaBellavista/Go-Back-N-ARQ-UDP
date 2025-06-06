import time, socket, sys
import threading

running = True
address = ('localhost', 12345)
window = 4
max_window = 8
timeout = 2
lock = threading.Lock()
sent_window = {} 
SeqN = 0
delay = 0.2
index = 0
confirmed_packets = 0
total_acks = 0
total_packets = 0

def is_newer(seq1, seq2): #treu if seq1 is newer than seq2
    return (0 < (seq1 - seq2) % max_window <= max_window // 2)

def elaborate_ACKS(socket):
    print("hello from ack thread")
    global sent_window, confirmed_packets, total_acks, running
    while running:
        try:
            ack, address = socket.recvfrom(4096)
            total_acks += 1
            ack = ack.decode('utf8')
            ack = int(ack)
            print("received ack: %s" % ack)
            with lock:
                keys = list(sent_window.keys())
                for i in keys:
                    if is_newer(ack, i):
                        confirmed_packets += 1
                        del sent_window[i]
                
        except Exception as e:
            print("Error receiving ACK: ", e)
            continue

message = input("Inserisci stringa da inviare: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("hello!".encode(), address)

#thread per ricevere ack mentre invio pacchetti
thread_ack = threading.Thread(target=elaborate_ACKS, args=(sock,))
thread_ack.daemon = True
thread_ack.start()
print("started ack receiving thread")

while running:
    print("inizio invio finestra")
    while len(sent_window) < window: #continua finchè c`è spazio nella finestra
        time.sleep(delay)

        seq = SeqN.to_bytes(1, 'big')
        
        index = confirmed_packets + len(sent_window)
        if index < len(message):
            char = message[index].encode('utf-8')
            print("sending char: %s" % char.decode('utf-8'))
        else:
            char = b'\xFF'

        packet = seq + char 

        print("invio pacchetto : %d" % SeqN)
        sock.sendto(packet, address)
        total_packets += 1
        with lock:
            sent_window[SeqN] = time.time()
        SeqN = (SeqN + 1) % max_window

    print("finestra completa, check timeout")
    print("finestra inviata: %s" % str(sent_window.keys()))
    #check timeout
    with lock:
        now = time.time()
        for seq in list(sent_window.keys()):
            if now - sent_window[seq] > timeout:
                print("timeout per il pacchetto con seq: %d" % seq)
                sent_window = {} #resetto tutta la finestra
                SeqN = seq
                break

    if confirmed_packets >= len(message):
            print("tutti i pacchetti confermati, invio terminato")
            running = False

    time.sleep(0.2)

sock.close
print("\ntotal packets sent: %d" % total_packets)
print("total acks received: %d" % total_acks)
print("of which %d were correct receptions" % confirmed_packets)
