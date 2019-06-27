# dispatcher.py

import queue
import pickle
import threading
import socket

from .channel import Channel

class Dispatcher:
    def send_message(self, msg):
        pass

    def recv_message(self, addr):
        pass

class QueueDispatcher(Dispatcher):
    def __init__(self, nservers):
        self.nservers = nservers
        self.channels = [queue.Queue() for n in range(nservers) ]

    def send_message(self, msg):
        self.channels[msg.dest].put(msg)

    def recv_message(self, addr):
        return self.channels[addr].get()

# A Dispatcher that uses sockets

# Connection endpoints for each server
CHANNEL_CONFIG = [
    ('localhost', 19000),
    ('localhost', 19001),
    ('localhost', 19002),
    ('localhost', 19003),
    ('localhost', 19004)
]

class ChannelDispatcher(Dispatcher):
    def __init__(self, addr):
        self.addr = addr
        self.nservers = len(CHANNEL_CONFIG)
        self._recv_queue = queue.Queue()
        self._send_queues = [ queue.Queue() for n in range(self.nservers) ]

    def start(self):
        threading.Thread(target=self.raft_server, daemon=True).start()
        for n in range(self.nservers):
            if n != self.addr:
                threading.Thread(target=self.raft_sender, args=(n,), daemon=True).start()

    def recv_message(self, addr):
        assert addr == self.addr
        return self._recv_queue.get()

    def send_message(self, msg):
        self._send_queues[msg.dest].put(msg)

    def raft_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(CHANNEL_CONFIG[self.addr])
        sock.listen()
        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.raft_receiver, args=(client,), daemon=True).start()

    # Thread that reads message from other servers
    def raft_receiver(self, client):
        with client:
            ch = Channel(client)
            msg = pickle.loads(ch.recv())
            self._recv_queue.put(msg)

    # Thread that sends messages to destination server
    def raft_sender(self, addr):
        ch = None
        while True:
            msg = self._send_queues[addr].get()
            try:
                if ch is None:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(CHANNEL_CONFIG[addr])
                    ch = Channel(sock)
                ch.send(pickle.dumps(msg))
            except OSError:
                ch = None
        
        
        
        
    

