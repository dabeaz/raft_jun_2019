# kvclient.py
#
# Client interface to the key-value store

from .config import *
from .channel import Channel

import socket
import time
import pickle

class KVClient:
    def __init__(self):
        self.ch = None

    def _connect(self):
        while True:
            for addr in KV_SERVER_CONFIG:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(addr)
                    self.ch = Channel(sock)
                    resp = pickle.loads(self.ch.recv())
                    if resp == 'ok':
                        print("Connected to", sock)
                        return
                    else:
                        sock.close()
                        self.ch = None
                except (OSError, pickle.PicklingError):
                    sock.close()
            print('No servers available. Retrying')
            time.sleep(2)

    def encode_command(self, name, *args):
        return pickle.dumps((name, args))

    def decode_response(self, msg):
        status, result = pickle.loads(msg)
        if status == 'ok':
            return result
        else:
            raise KVError(result)
        
    def command(self, name, *args):
        while True:
            if self.ch is None:
                self._connect()
            try:
                self.ch.send(self.encode_command(name, *args))
                return self.decode_response(self.ch.recv())
            except (OSError, pickle.PicklingError):
                self.ch = None

    def get(self, key):
        return self.command('get', key)

    def set(self, key, value):
        return self.command('set', key, value)

if __name__ == '__main__':
    client = KVClient()
