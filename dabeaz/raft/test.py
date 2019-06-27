from .machine import RaftMachine, Follower, Candidate, Leader, LogEntry
from .control import MockRaftController
from .message import RequestVote, RequestVoteResponse, AppendEntries, AppendEntriesResponse

NSERVERS = 5

def test_initial():
    control = MockRaftController(0, NSERVERS)
    machine = RaftMachine(control)
    assert machine.state == Follower
    assert machine.term == 0
    return machine, control

def test_election_timeout():
    machine, control = test_initial()
    initial_term = machine.term
    assert not control.election_timer_reset

    machine.handle_ElectionTimeout()

    assert machine.state == Candidate
    assert machine.term == initial_term + 1
    assert control.election_timer_reset
    assert machine.votedFor == 0
    assert len(control.messages) == NSERVERS-1
    assert all(type(msg) is RequestVote for msg in control.messages)
    return machine, control

def test_election_successful():
    machine, control = test_election_timeout()
    for msg in control.messages:
        machine.handle_RequestVoteResponse(
            RequestVoteResponse(source=msg.dest,
                                dest=0,
                                term=msg.term,
                                voteGranted=True)
            )

    assert machine.state == Leader
    assert machine.votedFor is None
    assert machine.nextIndex == {peer:0 for peer in control.peers }
    assert machine.matchIndex == {peer:-1 for peer in control.peers }

    # Upon leader, should have sent append entries to all peers
    msgs = control.messages[-len(control.peers):]
    assert all(type(msg) is AppendEntries for msg in msgs)
    # Messages should have empty entries list
    assert all(not msg.entries for msg in msgs)
    return machine, control

def test_election_failure():
    machine, control = test_election_timeout()
    for msg in control.messages:
        machine.handle_Message(
            RequestVoteResponse(source=msg.dest,
                                dest=0,
                                term=msg.term,
                                voteGranted=False)
            )

    # If election fails, server stays a candidate
    assert machine.state == Candidate
    return machine, control

def test_election_no_response():
    # Tests if an election is called and no VoteResponse
    # messages are received at all.
    machine, control = test_election_timeout()
    before_size = len(control.messages)
    before_term = machine.term
    machine.handle_ElectionTimeout()
    assert machine.state == Candidate
    assert machine.term == before_term + 1
    assert len(control.messages) == NSERVERS - 1 + before_size
    return machine, control

def test_request_vote():
    machine, control = test_initial()
    machine.handle_Message(
        RequestVote(source=1,
                    dest=0,
                    term=2,
                    lastLogIndex=-1,
                    lastLogTerm=-1,
                    )
        )
    assert control.election_timer_reset
    assert machine.state == Follower
    assert machine.term == 2
    assert machine.votedFor == 1

    assert len(control.messages) == 1
    assert type(control.messages[0]) is RequestVoteResponse
    assert control.messages[0].voteGranted
    assert control.messages[0].term == 2
    return machine, control

def test_request_vote_fail():
    machine, control = test_initial()
    machine.term = 3
    machine.handle_Message(
        RequestVote(source=1,
                    dest=0,
                    term=2,
                    lastLogIndex=-1,
                    lastLogTerm=-1,
                    )
        )
    
    # This should fail because machine term is higher than request vote
    assert not control.election_timer_reset
    assert machine.state == Follower
    assert machine.term == 3
    assert machine.votedFor == None

    assert len(control.messages) == 1
    assert type(control.messages[0]) is RequestVoteResponse
    assert not control.messages[0].voteGranted
    assert control.messages[0].term == 3
    return machine, control

def test_request_vote_fail_already_voted():
    machine, control = test_initial()
    machine.term = 2
    machine.votedFor = 0
    machine.handle_Message(
        RequestVote(source=1,
                    dest=0,
                    term=2,
                    lastLogIndex=-1,
                    lastLogTerm=-1,
                    )
        )
    
    # This should fail because machine already voted for another in same term
    assert not control.election_timer_reset
    assert machine.state == Follower
    assert machine.term == 2
    assert machine.votedFor == 0

    assert len(control.messages) == 1
    assert type(control.messages[0]) is RequestVoteResponse
    assert not control.messages[0].voteGranted
    assert control.messages[0].term == 2
    return machine, control

def test_follower_downgrade():
    # Tests to see if a message with higher term causes downgrade in state
    # to Follower
    machine, control = test_initial()
    machine.state = Leader
    machine.term = 0

    machine.handle_Message(
        RequestVoteResponse(source=1,
                            dest=0,
                            term=3,
                            voteGranted=False)
        )

    assert machine.state == Follower
    assert machine.term == 3

def test_append_entries_initial():
    machine, control = test_initial()
    # This handles the initial case (nothing in the log)
    machine.handle_Message(
        AppendEntries(source=1,
                      dest=0,
                      term=1,
                      prevLogIndex=-1,
                      prevLogTerm=None,
                      leaderCommit=-1,
                      entries=[ LogEntry(1, 'x') ]
                      )
        )
    assert len(control.messages) == 1
    resp = control.messages[0]
    assert type(resp) is AppendEntriesResponse
    assert resp.success
    assert resp.matchIndex == 0
    assert machine.log[0] == LogEntry(1, 'x')
    return machine, control

# Verify that more entries can be added to the log
def test_append_entries_more():
    machine, control = test_append_entries_initial()
    machine.handle_Message(
        AppendEntries(source=1,
                      dest=0,
                      term=1,
                      prevLogIndex=0,
                      prevLogTerm=1,
                      leaderCommit=-1,
                      entries=[ LogEntry(1, 'y') ]
                      )
        )
    assert len(control.messages) == 2
    resp = control.messages[1]
    assert type(resp) is AppendEntriesResponse
    assert resp.success
    assert resp.matchIndex == 1
    assert machine.log[1] == LogEntry(1, 'y')

def test_append_entries_bad_index():
    machine, control = test_append_entries_initial()
    machine.handle_Message(
        AppendEntries(source=1,
                      dest=0,
                      term=1,
                      prevLogIndex=1,    # Bad index.  Log isn't that long
                      prevLogTerm=1,
                      leaderCommit=-1,
                      entries=[ LogEntry(1, 'y') ]
                      )
        )
    assert len(control.messages) == 2
    resp = control.messages[1]
    assert type(resp) is AppendEntriesResponse
    assert not resp.success

def test_append_entries_bad_term():
    machine, control = test_append_entries_initial()
    machine.handle_Message(
        AppendEntries(source=1,
                      dest=0,
                      term=1,
                      prevLogIndex=0,    # 
                      prevLogTerm=0,     # Bad term. Prev entry has term=1
                      leaderCommit=-1,
                      entries=[ LogEntry(1, 'y') ]
                      )
        )
    assert len(control.messages) == 2
    resp = control.messages[1]
    assert type(resp) is AppendEntriesResponse
    assert not resp.success
       
    
def test_append_entries_response():
    machine, control = test_election_successful()
    assert machine.state == Leader
    
    # Fake some log entries.  These are uncommitted
    machine.log.extend([ LogEntry(1, 'x'), LogEntry(1, 'y'), LogEntry(1, 'z') ])

    # Upon election to leader, there ought to be some AppendEntries messages
    # that got sent out.  These were "empty" messages.  The leader knows
    # nothing about what has been committed.
    assert machine.commitIndex == -1

    # Fake some responses
    machine.handle_Message(
        AppendEntriesResponse(source=1,
                              dest=0,
                              term=1,
                              success=True,
                              matchIndex=2)
        )
    assert machine.commitIndex == -1    # No consensus!
    assert machine.matchIndex[1] == 2
    assert machine.nextIndex[1] == 3

    machine.handle_Message(
        AppendEntriesResponse(source=2,
                              dest=0,
                              term=1,
                              success=True,
                              matchIndex=2)
        )
    assert machine.commitIndex == 2
    assert machine.matchIndex[2] == 2
    assert machine.nextIndex[2] == 3


       

                      
