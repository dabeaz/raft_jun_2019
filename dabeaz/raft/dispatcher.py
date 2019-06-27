# dispatcher.py

import queue

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


