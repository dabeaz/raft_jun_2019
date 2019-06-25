# A "State" - a dictionary of values

import time

INITIAL = {
    'out1': 'G',
    'out2': 'R',
    'clock': 0,
}

# s is an instance of the "the state" (like INITIAL)
G1 = lambda s: (s['out1'] == 'G' and
                s['out2'] == 'R' and (
                    (s['clock'] < 30 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 30 and dict(s, clock=0, out1='Y')))
                )

Y1 = lambda s: (s['out1'] == 'Y' and
                s['out2'] == 'R' and (
                    (s['clock'] < 5 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 5 and dict(s, clock=0, out1='R', out2='G')))
                )


G2 = lambda s: (s['out1'] == 'R' and
                s['out2'] == 'G' and (
                    (s['clock'] < 60 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 60 and dict(s, clock=0, out2='Y')))
                )

Y2 = lambda s: (s['out1'] == 'R' and
                s['out2'] == 'Y' and (
                    (s['clock'] < 5 and dict(s, clock=s['clock']+1)) or
                    (s['clock'] == 5 and dict(s, clock=0, out1='G', out2='R')))
                )

INVARIANTS = lambda s:
NEXT = lambda s: G1(s) or Y1(s) or G2(s) or Y2(s)

# Run the machine
state = INITIAL
while state:
    print(state)
    state = NEXT(state)
    time.sleep(.25)
