# machine.py
#
# The Raft state machine

from .message import RequestVote, RequestVoteResponse, AppendEntries, AppendEntriesResponse

class LogEntry:
    def __init__(self, term, entry):
        self.term = term
        self.entry = entry
    def __repr__(self):
        return f'LogEntry({self.term}, {self.entry})'
    def __eq__(self, other):
        return (self.term, self.entry) == (other.term, other.entry)

class RaftMachine:
    def __init__(self, control):
        self.control = control   # All configuration/system dependent details in control

        self.term = 0            # Must be a persistent value (Eventually)
        self.state = Follower    
        self.votedFor = None     # Who voted for in current term

        self.log = [ ]           # Persistent data.  Part of controller?

        # Volatile state (on all servers)
        self.commitIndex = -1     # Highest log entry known to be committed
        self.lastApplied = -1     # Highest log entry applied to state machine

        # There is state that is initialized just on the leader (when becoming leader)
        self.reset_leader()

    # Transactions on the state machine.  These represent actions that need to
    # result in persistent state and logged.
    def append_entries(self, previndex, prevterm, entries):
        assert all(isinstance(e, LogEntry) for e in entries)
        if previndex + 1 > len(self.log):
            return False
        if previndex >= 0 and self.log[previndex].term != prevterm:
            return False
        self.log[previndex+1:] = entries
        return True

    def update(self, name, value):
        setattr(self, name, value)
    
    def reset_leader(self):
        # On becoming leader, these values are reset.

        # Next index is the next log index to be sent on append_entries
        self.nextIndex = { peer: len(self.log) for peer in self.control.peers }

        # Match index is the highest known index for matching logs
        self.matchIndex = { peer: -1 for peer in self.control.peers }
        
        # Who voted for in current election
        self.votedFor = None

    # Generic dispatch for any message
    def handle_Message(self, msg):
        if msg.term > self.term:
            self.term = msg.term
            self.state = Follower
        getattr(self, f'handle_{type(msg).__name__}')(msg)

    # Different message types that could be received
    def handle_AppendEntries(self, msg):
        self.state.handle_AppendEntries(self, msg)

    def handle_AppendEntriesResponse(self, msg):
        if msg.term == self.term:
            self.state.handle_AppendEntriesResponse(self, msg)

    def handle_RequestVote(self, msg):
        self.state.handle_RequestVote(self, msg)

    def handle_RequestVoteResponse(self, msg):
        if msg.term == self.term:
            self.state.handle_RequestVoteResponse(self, msg)

    def handle_ElectionTimeout(self):
        self.state.handle_ElectionTimeout(self)

    def handle_LeaderTimeout(self):
        self.state.handle_LeaderTimeout(self)

    def send_AppendEntries(self):
        # Send an AppendEntries message to all peers
        for dest in self.control.peers:
            self.send_AppendEntry(dest)

    def send_AppendEntry(self, dest):
        # Send a single AppendEntry message to one server
        prevLogIndex = self.nextIndex[dest] - 1
        prevLogTerm = self.log[prevLogIndex].term if prevLogIndex >= 0 else -1
        self.control.send_message(
            AppendEntries(
                dest=dest,
                term=self.term,
                prevLogIndex=prevLogIndex,
                prevLogTerm=prevLogTerm,
                entries=self.log[prevLogIndex+1:],
                leaderCommit=self.commitIndex
                )
            )

class RaftState:
    @staticmethod
    def handle_AppendEntries(machine, msg):
        print('handle_AppendEntries not implemented')

    @staticmethod
    def handle_AppendEntriesResponse(machine, msg):
        print('handle_AppendEntriesResponse not implemented')

    @staticmethod
    def handle_RequestVote(machine, msg):
        if (msg.term < machine.term or 
            (msg.term == machine.term and 
             machine.votedFor is not None and
             machine.votedFor != msg.source)):
            machine.control.send_message(
                RequestVoteResponse(dest=msg.source,
                                    term=machine.term,
                                    voteGranted=False
                )
            )

        else: # This needs more work (there are issues with log being up to date)
            machine.votedFor = msg.source
            machine.control.send_message(
                RequestVoteResponse(dest=msg.source,
                                    term=machine.term,
                                    voteGranted=True
                                    )
                )
            machine.control.reset_election_timer()

    @staticmethod
    def handle_RequestVoteResponse(machine, msg):
        print('handle_RequestVoteResponse not implemented')

    @staticmethod
    def handle_ElectionTimeout(machine):
        print('handle_ElectionTimeout not implemented')

    @staticmethod
    def handle_LeaderTimeout(machine):
        print('handle_LeaderTimeout not implemented')

class Follower(RaftState):
    @staticmethod
    def handle_ElectionTimeout(machine):
        machine.state = Candidate
        machine.term += 1
        machine.votedFor = machine.control.id   # I vote for myself
        machine.control.reset_election_timer()
        machine.votesGranted = 1

        # Send a RequestVote to all other servers
        for dest in machine.control.peers:
            machine.control.send_message(
                RequestVote(dest=dest,
                            term=machine.term,
                            lastLogIndex = len(machine.log) - 1,
                            lastLogTerm = machine.log[len(machine.log)-1].term if machine.log else -1
                            )
                )

    @staticmethod
    def handle_AppendEntries(machine, msg):
        logOk = (msg.prevLogIndex == -1 or (
                     msg.prevLogIndex >= 0 and
                     msg.prevLogIndex < len(machine.log) and
                     msg.prevLogTerm == machine.log[msg.prevLogIndex].term
                     )
                 )
        if msg.term < machine.term or not logOk:
            # Failure
            machine.control.send_message(
                AppendEntriesResponse(
                    dest=msg.source,
                    term=machine.term,
                    success=False,
                    matchIndex=-1
                    )
                )
        else:
            # Appending should work
            ok = machine.append_entries(msg.prevLogIndex,
                                     msg.prevLogTerm,
                                     msg.entries)
            
            assert ok
            machine.control.send_message(
                AppendEntriesResponse(
                    dest=msg.source,
                    term=machine.term,
                    success=True,
                    matchIndex=msg.prevLogIndex+len(msg.entries)
                    )
                )

class Leader(RaftState):
    @staticmethod
    def handle_AppendEntriesResponse(machine, msg):
        # If the operation was successful, update leader settings for the follower
        if msg.success:
            machine.matchIndex[msg.source] = msg.matchIndex
            machine.nextIndex[msg.source] = msg.matchIndex+1

            # Check for consensus on log entries
            matches = sorted(machine.matchIndex.values())
            machine.commitIndex = matches[len(machine.matchIndex)//2]

        else:
            # It failed for this follower.   Immediately retry with a
            # lower nextIndex value
            machine.nextIndex[msg.source] -= 1
            machine.send_AppendEntry(msg.source)

    @staticmethod
    def handle_LeaderTimeout(machine):
        # Must send an append entries message to all followers
        machine.send_AppendEntries()

        # Must reset the leader timeout
        machine.control.reset_leader_timeout()


class Candidate(RaftState):
    @staticmethod
    def handle_RequestVoteResponse(machine, msg):
        if msg.term < machine.term:   # Ignore (out of date message)
            pass

        if msg.voteGranted:
            machine.votesGranted += 1
            if machine.votesGranted > (machine.control.nservers // 2):
                machine.state = Leader
                machine.reset_leader()
                # Upon leadership change, send an empty AppendEntries
                machine.send_AppendEntries()
                machine.control.reset_leader_timeout()
        
    @staticmethod
    def handle_ElectionTimeout(machine):
        # Oh well. Call a new election for myself
        Follower.handle_ElectionTimeout(machine)

    @staticmethod
    def handle_AppendEntries(machine, msg):
        if msg.term == machine.term:
            # Convert to follower and handle message
            machine.state = Follower
            machine.handle_AppendEntries(msg)


