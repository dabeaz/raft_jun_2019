from traffic import LightState, STATES

def test_initial_state():
    ls = LightState()
    assert ls.state == STATES[0]


def test_cycle_once():
    ls = LightState()
    delay = ls.cycle()
    assert delay == STATES[1].delay
    assert ls.state == STATES[1]


def test_cycle_six_times():
    ls = LightState()
    for _ in range(6):
        delay = ls.cycle()
    assert delay == STATES[2].delay
    assert ls.state == STATES[2]

