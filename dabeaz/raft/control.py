# control.py
#
# The Raft controller

class RaftController:
    pass

class MockRaftController(RaftController):
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

    def get_log_entry(self, index):
        pass

    def log_size(self):
        pass

    
