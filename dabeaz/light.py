# light.py

# A "State" - A dictionary of values

INITIAL = {
    'out1': 'G',
    'out2': 'R',
    'clock': 0,
    'walk': False
    }

# s is an instance of "the state"  (like INITIAL)
G1 = lambda s: (s['out1'] == 'G' and
                s['out2'] == 'R' and (
                   (s['clock'] < 30 and dict(s, clock=s['clock']+1)) or
                   (s['clock'] == 30 and dict(s, clock=0, out1='Y')))
                )


Y1 = lambda s: (s['out1'] == 'Y' and
                s['out2'] == 'R' and (
                    (s['clock'] < 5 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 5 and dict(s, clock=0, out1="R", out2="G"))
                    )
                )

G2 = lambda s: (s['out1'] == 'R' and
                s['out2'] == 'G' and (
                    (s['clock'] >= 30 and s['walk'] and
                        dict(s, clock=0, out2="Y", walk=False)) or
                    (s['clock'] < 60 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 60) and dict(s, clock=0, out2="Y")
                  )   
                )

Y2 = lambda s: (s['out1'] == 'R' and
                s['out2'] == 'Y' and (
                    (s['clock'] < 5 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 5) and dict(s, clock=0, out1="G", out2="R")
                  )
                )

INVARIANTS = lambda s: not (s['out1'] in {'G','Y'} and s['out1'] == s['out2'])

# State machines only run in response to events.  These functions take an
# event and a state and return the next state (if there is one)
TICK = lambda evt, s: evt == 'tick' and (G1(s) or Y1(s) or G2(s) or Y2(s))
BUTTON = lambda evt, s: evt == 'button' and dict(s, walk=True)
NEXT = lambda evt, s: TICK(evt, s) or BUTTON(evt, s)

def run():
    import queue
    import threading
    import time
    event_queue = queue.Queue()
    
    def run_timer():
        while True:
            time.sleep(0.25)
            event_queue.put('tick')

    def run_button():
        import sys
        while True:
            sys.stdin.readline()
            event_queue.put('button')

    threading.Thread(target=run_timer, daemon=True).start()
    threading.Thread(target=run_button, daemon=True).start()

    state = INITIAL
    while True:
        print(state)
        evt = event_queue.get()
        state = NEXT(evt, state)


def freeze(d):
    return tuple(sorted(d.items()))

def simulate():
    from collections import deque
    seen_states = set()
    must_check = deque([INITIAL])   # Queue of pending states

    while must_check:
        state = must_check.popleft()    # Get a state
        if freeze(state) in seen_states:
            continue
        seen_states.add(freeze(state))
        num_pending = len(must_check)
        for evt in ['tick', 'button']:   # ALL possible events
            nextstate = NEXT(evt, state)
            if nextstate:
                must_check.append(nextstate)
        if num_pending == len(must_check):
            print("DEADLOCK in", state)

    print("Checked", len(seen_states), "states")
simulate() 

