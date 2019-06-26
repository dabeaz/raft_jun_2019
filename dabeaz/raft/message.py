# message.py
#
# Raft Messages (from pg. 4)
#
# Assumptions about the implementation:
#
# 1. Each server is identified by an integer (0...n-1)
# 2. Messages encode the source and destination 
#
class RaftMessage:
    def __init__(self, source, dest):
        assert (isinstance(source, int) and 
                isinstance(dest, int) and
                source != dest)
              
        self.source = source
        self.dest = dest

# This is the "Arguments" (from pg. 4 table)
class AppendEntries(RaftMessage):
    term = None
    leaderId = None
    prevLogIndex = None
    prevLogTerm = None
    entries = None
    leaderCommit = None     # Same as mcommitIndex in TLA+.  Check with
                            # bullet 5 in paper, "Receiver Implementation"

# This is the "Results" (from pg. 4 table)
class AppendEntriesResponse(RaftMessage):
    term = None
    success = None
    matchIndex = None   # Used in TLA+ spec.  For what???

class RequestVote(RaftMessage):
    def __init__(self, source, dest, term):
        super().__init__(source, dest)
        self.term = term
        # self.candidateId = candidateId   # Not needed (probably)
        # self.lastLogIndex = lastLogIndex
        # self.lastLogTerm = lastLogTerm

class RequestVoteResponse(RaftMessage):
    def __init__(self, source, dest, term, voteGranted):
        super().__init__(source, dest)
        self.term = term
        self.voteGranted = voteGranted
