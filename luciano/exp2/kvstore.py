# kvstore.py
import pickle
import message

data = { }

def get(key):
    return data.get(key)    # Returns None for non-existing key

def set(key, value):
    data[key] = value

class KVHandler:
    def __init__(self, channel):
        # Same issue as with channels.  Do you create the channel inside
        # __init__ or do you require the channel to be created externally
        # and passed in?  Again, thinking about testing/debugging.
        self.ch = channel    # An already existing channel object

    def run(self):
        running = True
        while running:
            msg = self.ch.recv()   # Get a message
            name, args = pickle.loads(msg)
            if name == 'get':
                result = ('ok', get(*args))
            elif name == 'set':
                result = ('ok', set(*args))
            elif name == 'quit':
                result = ('ok', None)
                running = False
            else:
                result = ('error', f'Unknown command: {name}')
            self.ch.send(pickle.dumps(result))
        print("Stopped")

class KVClient:
    def __init__(self, channel):
        self.ch = channel  # An already existing Channel instance

    def command(self, name, *args):
        msg = pickle.dumps((name, args))
        self.ch.send(msg)
        resp = self.ch.recv()
        status, result = pickle.loads(resp)
        if status == 'ok':
            return result
        else:
            raise KVError(result)

    def get(self, key):
        return self.command('get', key)

    def set(self, key, value):
        return self.command('set', key, value)

    def quit(self):
        return self.command('quit')

def handle_client(ch):     # Ch already created (by server)
    server = KVHandler(ch)
    server.run()

def run_kv_server(address):
    import message
    message.run_channel_server(address, handle_client)
    
def make_client(address):
    '''
    Example use:

    client = make_client(('localhost', 29000))
    client.set('key', value)
    value = client.get('key')
    '''
    ch = message.make_channel_connection(address)
    return KVClient(ch)


def smoke_test():
    address = ('', 29000)
    import threading
    srv = threading.Thread(target=run_kv_server, args=(address,), daemon=True)
    srv.start()
    c1 = make_client(address)
    print(c1.get('x'))
    c1.set('x', 3)
    print(c1.get('x'))
    c1.quit()
    # srv.join()


if __name__ == '__main__':
    # run_kv_server(('', 29000))
    smoke_test()
