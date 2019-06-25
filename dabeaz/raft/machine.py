# machine.py
#
# The Raft state machine

class RaftMachine:
    def __init__(self, id, nservers):
        assert isinstance(nservers, int) and nservers > 1 and nservers % 2
        self.nservers = nservers

        assert isinstance(id, int) and id in range(nservers)
        self.id = id        # id is an integer indicating what node of the
                            # cluster this is.  Needed for message source

        self.term = 0       # Must be a persistent value (Eventually)
        self.state = Follower

    # Different message types that could be received
    def handle_AppendEntries(self, msg):
        pass

    def handle_AppendEntriesResponse(self, msg):
        pass

    def handle_RequestVote(self, msg):
        pass

    def handle_RequestVoteResponse(self, msg):
        pass

    # Called if no messages received within timeout period
    def handle_MessageTimeout(self):
        pass

    

class RaftState:
    pass

class Follower(RaftState):
    pass

class Leader(RaftState):
    pass

class Candidate(RaftState):
    pass


