# message.py
#
# Raft Messages (from pg. 4)
#
# Some general assumptions and notes:
#
#   1. The source of a message is implicit and filled in by whatever
#      controller handles the message
#
#   2. All message arguments are keyword arguments (better readability)
#
#   3. All messages include source, dest, and term.

class RaftMessage:
    pass

# This is the "Arguments" (from pg. 4 table)
class AppendEntries(RaftMessage):
    def __init__(self, *, dest, term, prevLogIndex, prevLogTerm, entries, leaderCommit, source=None):
        self.source = source
        self.dest = dest
        self.term = term
        self.prevLogIndex = prevLogIndex
        self.prevLogTerm = prevLogTerm
        self.entries = entries
        self.leaderCommit = leaderCommit

    def __repr__(self):
        return f'AppendEntries(dest={self.dest}, term={self.term}, prevLogIndex={self.prevLogIndex}, prevLogTerm={self.prevLogTerm}, leaderCommit={self.leaderCommit}, entries={self.entries})'

# This is the "Results" (from pg. 4 table)
class AppendEntriesResponse(RaftMessage):
    def __init__(self, *, dest, term, success, matchIndex, source=None):
        self.source = source
        self.dest = dest
        self.term = term
        self.success = success
        self.matchIndex = matchIndex
        
    def __repr__(self):
        return f'AppendEntriesResponse(dest={self.dest}, term={self.term}, success={self.success}, matchIndex={self.matchIndex})'

class RequestVote(RaftMessage):
    def __init__(self, *, dest, term, lastLogIndex, lastLogTerm, source=None):
        self.source = source
        self.dest = dest
        self.term = term
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm

    def __repr__(self):
        return f'RequestVote(dest={self.dest}, term={self.term}, lastLogIndex={self.lastLogIndex}, lastLogTerm={self.lastLogTerm})'

class RequestVoteResponse(RaftMessage):
    def __init__(self, *, dest, term, voteGranted, source=None):
        self.source = source
        self.dest = dest
        self.term = term
        self.voteGranted = voteGranted

    def __repr__(self):
        return f'RequestVoteResponse(dest={self.dest}, term={self.term}, voteGranted={self.voteGranted})'
