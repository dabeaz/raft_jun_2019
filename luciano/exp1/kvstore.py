# kvstore.py

import pickle

data = { }

def get(key):
    return data.get(key)

def set(key, value):
    data[key] = value


class KVServer:

    def __init__(self, channel):
        self.ch = channel

    def run(self):
        while True:
            msg = self.ch.recv()   # Get a message
            op, args = pickle.loads(msg)      # Unpack the message
            if op == 'get':
                result = get(*args)
            elif op == 'set':
                result = set(*args)
            self.ch.send(pickle.dumps(result))


class KVClient:

    def __init__(self, channel):
        self.ch = channel

    def get(self, key):
        msg = pickle.dumps(('get', (key,)))
        self.ch.send(msg)
        resp = self.ch.recv()
        return pickle.loads(resp)

    def set(self, key, value):
        msg = pickle.dumps(('set', (key, value)))
        self.ch.send(msg)
        resp = self.ch.recv()
        return pickle.loads(resp)


import message


def make_server(port=29000):
    address = ('', port)
    ch = message.accept_connection(address)
    server = KVServer(ch)
    return server


def make_client(port=29000):
    address = ('', port)
    ch = message.make_connection(address)
    client = KVClient(ch)
    return client


def server_task(server_ready):
    print('server starting')
    s = make_server(27000)
    print('server ready')
    server_ready.set()
    s.run()


def client_task(server_ready):
    print('client starting')
    print('client waiting')
    server_ready.wait()
    c = make_client(27000)
    print('client ready')
    # client_ready.set()
    print(c.get('a'))
    print(c.set('a', 1))
    print(c.get('a'))


def smoke_test():
    from threading import Thread, Event
    server_ready = Event()
    st = Thread(target=server_task, args=(server_ready,))
    ct = Thread(target=client_task, args=(server_ready,))
    st.start()
    ct.start()

# smoke_test()
