# message.py

class Channel:
    def __init__(self, sock):
        self.sock = sock   # An already existing socket object
                           # What it be better to create the 
                           # socket in here and hide implementation details?

    def send(self, msg: bytes):
        # Send len(msg)
        # How to encode the size header????
        #   - Binary integer (32-bit unsigned int? byte-order?)
        #   - Text? (length embedded in a 12-character field)
        sz = b'%12d' % (len(msg))
        assert len(sz) == 12, "Whoa!"
        self.sock.sendall(sz)
        self.sock.sendall(msg)

    def recv_exactly(self, nbytes):
        msg = b''  
        while len(msg) < nbytes:    
            fragment = self.sock.recv(nbytes-len(msg))
            if not fragment:   # EOF.
                raise OSError("Incomplete message")
            msg += fragment
        return msg

    def recv(self):
        # Receive the size of the message
        # Receive the payload (exactly size bytes)
        # Return the message.
        szmsg = self.recv_exactly(12)   # Get the 12-byte size
        sz = int(szmsg)
        msg = self.recv_exactly(sz)     # Get the rest of the message
        return msg

# For "testing" (experimentation) only

# Server
def run_channel_server(address, channel_handler):
    from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
    import threading
    sock = socket(AF_INET, SOCK_STREAM)
    # This avoids errors with "address in use"
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    sock.bind(address)
    sock.listen(1)
    #shutdown = threading.Event()
    while True:
        client, addr = sock.accept()  # Returns a socket and address2
        ch = Channel(client)
        t = threading.Thread(target=channel_handler, args=(ch,))
        t.start()

# Client
def make_channel_connection(address):
    from socket import socket, AF_INET, SOCK_STREAM
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    return Channel(sock)

def smoke_test():
    from socket import socketpair
    s1, s2 = socketpair()    # Makes a pair of connected sockets
    ch1 = Channel(s1)
    ch2 = Channel(s2)
    ch1.send(b'Hello World')
    msg = ch2.recv()
    assert msg == b'Hello World'
    s1.close()
    s2.close()

smoke_test()
