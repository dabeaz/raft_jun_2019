# kvstore.py
import pickle
import threading
import time
import socket

from .channel import Channel
from .dispatcher import ChannelDispatcher
from .control import RaftController
from .machine import RaftMachine, Leader
from .config import *

class KVStore:
    def __init__(self):
        self.data = { }

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

class KVServer:
    def __init__(self, control):
        self.control = control
        self.control.applicator = self.apply_entries
        self.store = KVStore()
        self.write_lock = threading.Lock()
        self.commit_evt = threading.Event()

    def apply_entries(self, entries):
        print("KVSTORE: applying entries", entries)
        for ent in entries:
            key, value = ent.entry
            self.store.set(key, value)
        self.commit_evt.set()

    def do_command(self, msg):
        # This could be executed by multiple client threads
        name, args = pickle.loads(msg)
        print(name, args)
        if name == 'get':
            # Gets run immediately
            result = ('ok', self.store.get(*args))
        elif name == 'set':
            # Set operations involve raft
            key, value = args
            with self.write_lock:
                # Only one write at a time
                self.commit_evt.clear()
                self.control.append_entry((key, value))
                self.commit_evt.wait()
            result = ('ok', None)
        else:
            result = ('error', f'Unknown command: {name}')
        return pickle.dumps(result)

    def handle_client(self, sock):
        # This handles the processing of a single client
        with sock:
            ch = Channel(sock)
            if self.control.machine.state != Leader:
                ch.send(pickle.dumps('error'))
                return
            else:
                ch.send(pickle.dumps('ok'))
                while True:
                    msg = ch.recv()   # Get a message
                    ch.send(self.do_command(msg))
            
    def run_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(KV_SERVER_CONFIG[self.control.addr])
        sock.listen()
        print(f"Server {self.control.addr} listening on {sock}")
        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client,),
                             daemon=True).start()

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()

def main(addr):
    dispatch = ChannelDispatcher(addr)
    dispatch.start()
    controller = RaftController(addr, dispatch, RaftMachine())
    controller.start()
    kvserver = KVServer(controller)
    kvserver.start()
    return kvserver
    
if __name__ == '__main__':
    import sys
    server = main(int(sys.argv[1]))
    while True:
        time.sleep(1)


