from socket import *

class Channel:
    def __init__(self, sock):
        self.sock = sock
    
    def send(self, msg: bytes):
        """Send len(msg), then msg"""
        sz = b'%12d' % len(msg)
        self.sock.sendall(sz)
        self.sock.sendall(msg)

    def recv_exactly(self, nbytes):
        msg = b''
        while len(msg) < nbytes:
            fragment = self.sock.recv(nbytes)
            if not fragment:
                raise IOError('Incomplete message')
            msg += fragment
        return msg

    def recv(self) -> bytes:
        """Receive len(msg), then msg"""
        szmsg = self.recv_exactly(12)
        sz = int(szmsg)
        msg = self.recv_exactly(sz)
        return msg


# for manual testing

def accept_connection(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(1)
    client, addr = sock.accept()
    ch = Channel(client)
    return ch


def make_connection(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    return Channel(sock)


def serve():
    srv = accept_connection(('', 28000))
    srv_got = ch.recv()
    print(srv_got)

import time

def smoke_test():
    from threading import Thread
    srv = Thread(target=serve)
    srv.start()
    time.sleep(1)
    cli_ch = make_connection(('localhost', 28000))
    cli_ch.send(b'Hello World')
    cli_got = cli_ch.recv()
    print(cli_got)

def smoke_server():
    ch = accept_connection(('', 28000))
    got = ch.recv()
    print(got)
    ch.send(b'It works!')

def smoke_client():
    ch = make_connection(('localhost', 28000))
    ch.send(b'Hello World')
    got = ch.recv()
    print(got)

if __name__ == '__main__':
    #smoke_test()
    pass
