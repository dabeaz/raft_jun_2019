# machine.py
#
# The Raft state machine

from .message import RequestVote

class RaftMachine:
    def __init__(self, id, nservers, control):
        self.control = control
        assert isinstance(nservers, int) and nservers > 1 and nservers % 2
        self.nservers = nservers

        assert isinstance(id, int) and id in range(nservers)
        self.id = id        # id is an integer indicating what node of the
                            # cluster this is.  Needed for message source

        self.term = 0            # Must be a persistent value (Eventually)
        self.state = Follower    
        self.votedFor = None     # Who voted for in current term

    # Different message types that could be received
    def handle_AppendEntries(self, msg):
        self.state.handle_AppendEntries(self, msg)

    def handle_AppendEntriesResponse(self, msg):
        self.state.handle_AppendEntriesResponse(self, msg)

    def handle_RequestVote(self, msg):
        self.state.handle_RequestVote(self, msg)

    def handle_RequestVoteResponse(self, msg):
        self.state.handle_RequestVoteResponse(self, msg)

    def handle_ElectionTimeout(self):
        self.state.handle_ElectionTimeout(self)

class RaftState:
    @staticmethod
    def handle_AppendEntries(machine, msg):
        print('handle_AppendEntries not implemented')

    @staticmethod
    def handle_AppendEntriesResponse(machine, msg):
        print('handle_AppendEntriesResponse not implemented')

    @staticmethod
    def handle_RequestVote(machine, msg):
        print('handle_RequestVote not implemented')

    @staticmethod
    def handle_RequestVoteResponse(machine, msg):
        print('handle_RequestVoteResponse not implemented')

    @staticmethod
    def handle_ElectionTimeout(machine):
        print('handle_ElectionTimeout not implemented')

class Follower(RaftState):
    @staticmethod
    def handle_ElectionTimeout(machine):
        machine.state = Candidate
        machine.term += 1
        machine.votedFor = machine.id   # I vote for myself
        # Reset election timer????
        machine.control.reset_election_timer()
        machine.votesGranted = 1

        # Send a RequestVote to all other servers
        for i in range(machine.nservers):
            if i != machine.id:
                machine.control.send_message(
                    RequestVote(source=machine.id,
                                dest=i,
                                term=machine.term,
                                )
                    )

    @staticmethod
    def handle_RequestVote(machine, msg):
        # ...
        machine.control.send_message(
            RequestVoteResponse()
        )


class Leader(RaftState):
    pass

class Candidate(RaftState):
    @staticmethod
    def handle_RequestVoteResponse(machine, msg):
        if msg.term < machine.term:   # Ignore (out of date message)
            pass

        if msg.voteGranted:
            machine.votesGranted += 1
            if machine.votesGranted > (machine.nservers // 2):
                machine.state = Leader
        
    @staticmethod
    def handle_ElectionTimeout(machine):
        # Oh well. Call a new election for myself
        Follower.handle_ElectionTimeout(machine)




