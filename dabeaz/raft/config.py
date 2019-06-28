# Number of raft servers
NSERVERS = 5

# Timeout settings for Raft
LEADER_TIMEOUT = 1
ELECTION_TIMEOUT = 3
ELECTION_TIMEOUT_SPREAD = 0.5

# Connection endpoints for each server
RAFT_SERVER_CONFIG = [
    ('localhost', 19000),
    ('localhost', 19001),
    ('localhost', 19002),
    ('localhost', 19003),
    ('localhost', 19004)
]

# Client connection endpoints for the key-value store server
KV_SERVER_CONFIG = [
    ('localhost', 20000),
    ('localhost', 20001),
    ('localhost', 20002),
    ('localhost', 20003),
    ('localhost', 20004)
]
