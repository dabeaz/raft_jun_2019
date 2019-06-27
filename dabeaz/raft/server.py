# server.py

from .dispatcher import ChannelDispatcher
from .control import RaftController
from .machine import RaftMachine

def main(addr):
    dispatch = ChannelDispatcher(addr)
    dispatch.start()
    controller = RaftController(addr, dispatch, RaftMachine())
    controller.start()
    return controller

if __name__ == '__main__':
    import sys
    import time
    main(int(sys.argv[1]))
    while True:
        time.sleep(1)

