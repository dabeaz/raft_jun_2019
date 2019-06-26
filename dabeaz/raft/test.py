from .machine import RaftMachine, Follower, Candidate, Leader
from .control import MockRaftController
from .message import RequestVote

NSERVERS = 5

def test_initial():
    control = MockRaftController()
    machine = RaftMachine(0, NSERVERS, control)
    assert machine.state == Follower
    assert machine.term == 0

def test_follower_election_timeout():
    control = MockRaftController()
    machine = RaftMachine(0, NSERVERS, control)
    initial_term = machine.term
    assert not control.election_timer_reset

    machine.handle_ElectionTimeout()

    assert machine.state == Candidate
    assert machine.term == initial_term + 1
    assert control.election_timer_reset
    assert machine.votedFor == 0
    assert len(control.messages) == NSERVERS-1
    assert all(type(msg) is RequestVote for msg in control.messages)



    
