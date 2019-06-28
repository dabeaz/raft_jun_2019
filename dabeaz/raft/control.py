# control.py
#
# The Raft controller

import threading
import queue
import time
import random

from .machine import RaftMachine
from .config import *

class RaftControllerBase:
    def apply_entries(self, entries):
        pass

class RaftController(RaftControllerBase):
    def __init__(self, addr, dispatcher, machine, applicator=None):
        self.addr = addr
        self.dispatcher = dispatcher
        self.machine = machine
        self.applicator = applicator

        machine.control = self

        self.peers = [ i for i in range(dispatcher.nservers) if i != addr ]
        self.nservers = dispatcher.nservers
        self.event_queue = queue.Queue()
        self.running = False
        self._paused = False

        # Debug logging
        self.debug_log = open(f'log-{addr}.txt', 'wt')

    def apply_entries(self, entries):
        self.debug_log.write(f'Applying {entries}\n')
        self.debug_log.flush()
        if self.applicator:
            self.applicator(entries)

    # Commands used by the machine
    def send_message(self, msg):
        msg.source = self.addr
        self.debug_log.write(f'{self.addr}: send_message({msg})\n')
        self.debug_log.flush()
        self.dispatcher.send_message(msg)

    # The main event loop
    def start(self):
        self.running = True
        print(f"Starting server: {self.addr}")
        threading.Thread(target=self.run, daemon=True).start()
        threading.Thread(target=self.run_receiver, daemon=True).start()
        threading.Thread(target=self.run_leader_timer, daemon=True).start()
        threading.Thread(target=self.run_election_timer, daemon=True).start()

    def run(self):
        while self.running:
            evt, *args = self.event_queue.get()
            if not self._paused:
                self.debug_log.write(f'{self.addr}: {evt} {args}\n')
                self.debug_log.flush()
                getattr(self.machine, evt)(*args)

    def pause(self):
        self._paused = True

    def go(self):
        self._paused = False

    def run_receiver(self):
        while self.running:
            msg = self.dispatcher.recv_message(self.addr)
            self.event_queue.put(('handle_Message', msg))

    def run_leader_timer(self):
        self._leader_deadline = 0
        while self.running:
            delay = self._leader_deadline - time.monotonic()
            if delay <= 0:
                delay = LEADER_TIMEOUT
                self._leader_deadline = time.monotonic() + delay
            time.sleep(delay)
            if time.monotonic() > self._leader_deadline:
                self.event_queue.put(('handle_LeaderTimeout',))

    def reset_leader_timeout(self):
        self.debug_log.write(f'{self.addr}: reset_leader_timeout\n')
        self.debug_log.flush()
        self._leader_deadline = time.monotonic() + LEADER_TIMEOUT

    def run_election_timer(self):
        self._election_deadline = 0
        while self.running:
            delay = self._election_deadline - time.monotonic()
            if delay <= 0:
                self.new_election_deadline()
            time.sleep(self._election_deadline - time.monotonic())
            if time.monotonic() > self._election_deadline:
                self.event_queue.put(('handle_ElectionTimeout',))

    def new_election_deadline(self):
        new_deadline = time.monotonic() + random.random() * ELECTION_TIMEOUT_SPREAD + ELECTION_TIMEOUT
        if new_deadline > self._election_deadline:
            self._election_deadline = new_deadline
        
    def reset_election_timer(self):
        self.debug_log.write(f'{self.addr}: reset_election_timer\n')
        self.debug_log.flush()
        self.new_election_deadline()

    # Client function.  Add a new entry to the machine log
    def append_entry(self, item):
        self.event_queue.put(('append_new_entry', item))


class MockRaftController(RaftControllerBase):
    def __init__(self, id, nservers):
        self.id = id
        self.nservers = nservers
        self.peers = [ i for i in range(nservers) if i != id ]
        self.messages = []
        self.election_timer_reset = False
        self.leader_timeout_reset = False

    def send_message(self, msg):
        msg.source = self.id
        self.messages.append(msg)

    def reset_election_timer(self):
        self.election_timer_reset = True
        
    def reset_leader_timeout(self):
        self.leader_timeout_reset = True

    def append_log_entry(self, entry):
        pass

def main():
    from .dispatcher import QueueDispatcher
    dispatch = QueueDispatcher(NSERVERS)
    controllers = [ RaftController(i, dispatch, RaftMachine()) 
                    for i in range(NSERVERS) ]

    for cont in controllers:
        cont.start()

    return controllers
    
if __name__ == '__main__':
    servers = main()

    
    
