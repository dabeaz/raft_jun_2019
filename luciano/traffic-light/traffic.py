
from collections import namedtuple
import time


State = namedtuple('State', 'name out1 out2 delay')


STATES = [
    State('G1', 'G', 'R', 30),
    State('Y1', 'Y', 'R', 5),
    State('G2', 'R', 'G', 60),
    State('Y2', 'R', 'Y', 5),
]


class LightState:

    def __init__(self):
        self.state_index = 0

    def cycle(self):
        self.state_index = (self.state_index + 1) % len(STATES)
        return self.state.delay

    @property
    def state(self):
        return STATES[self.state_index]


class TrafficLight:

    def __init__(self):
        self.state = LightState()




DELAY_SCALE = .05
END_TIME = 200

def driver():
    t = 0
    ls = LightState()
    dt = ls.state.delay
    while True:
        print(f't={t:4d} {ls.state}')
        time.sleep(dt * DELAY_SCALE)
        dt = ls.cycle()
        t += dt
        if t > END_TIME:
            break

if __name__ == '__main__':
    driver()




