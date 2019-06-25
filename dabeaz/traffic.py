# traffic.py
import time

class LightState:
    @staticmethod
    def handle_clock_tick(light):
        pass

    @staticmethod
    def handle_button_press(light):
        pass

class Green1(LightState):
    @staticmethod
    def handle_clock_tick(light):
        if light.clock == 30:
            light.clock = 0
            light.state = Yellow1
            
            
class Yellow1(LightState):
    @staticmethod
    def handle_clock_tick(light):
        if light.clock == 5:
            light.clock = 0
            light.state = Green2
            
class Green2(LightState):
    @staticmethod
    def handle_clock_tick(light):
        if light.clock == 60 or (light.walk and light.clock >= 30):
            light.clock = 0
            light.walk = False
            light.state = Yellow2

    @staticmethod
    def handle_button_press(light):
        light.walk = True

class Yellow2(LightState):
    @staticmethod
    def handle_clock_tick(light):
        if light.clock == 5:
            light.clock = 0
            light.state = Green1
            
class TrafficLight:
    def __init__(self):
        self.state = Green1
        self.clock = 0
        self.walk = False

    def __repr__(self):
        return f'TrafficLight(state={self.state}, clock={self.clock}, walk={self.walk})'
    
    def handle_clock_tick(self):
        self.clock += 1
        self.state.handle_clock_tick(self)
        
    def handle_button_press(self):
        self.state.handle_button_press(self)

# This class is responsible for driving the traffic light.
# This is separate from the state machine

import threading
import queue

class LightController:
    def __init__(self, light):
        self.light = light
        self.event_queue = queue.Queue()
        self.observers = set()

    def subscribe(self, callback):
        self.observers.add(callback)
        
    def run(self):
        self.running = True
        threading.Thread(target=self.run_clock, daemon=True).start()
        threading.Thread(target=self.run_button, daemon=True).start()
        while True:
            evt = self.event_queue.get()
            if evt is None:
                break
            if evt == 'tick':
                self.light.handle_clock_tick()
            elif evt == 'button':
                self.light.handle_button_press()
            else:
                print("BAD EVENT:", evt)
            # Notify all observers watching the light
            for observer in self.observers:
                observer(self.light)
        self.running = False

    def run_clock(self):
        while self.running:
            time.sleep(0.25)
            self.event_queue.put('tick')

    def run_button(self):
        import sys
        while self.running:
            sys.stdin.readline()
            self.event_queue.put('button')

            
light = TrafficLight()
control = LightController(light)
control.subscribe(print)
control.run()
