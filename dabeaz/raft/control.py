# control.py
#
# The Raft controller

class RaftController:
    pass

class MockRaftController(RaftController):
    def __init__(self):
        self.messages = []
        self.election_timer_reset = False

    def send_message(self, msg):
        self.messages.append(msg)

    def reset_election_timer(self):
        self.election_timer_reset = True

    
