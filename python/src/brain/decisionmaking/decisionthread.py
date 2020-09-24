import sys
import time
import os
from src.utils.templates.threadwithstop import ThreadWithStop
from src.brain.decisionmaking.decisionhandle import DecisionHandler

sys.path.append('.')


class DecisionThread(ThreadWithStop):
    def __init__(self, inP, outP):

        super(DecisionThread, self).__init__()
        self.daemon = True

        self.inPs = inP
        self.outPs = outP
        self.decisions = DecisionHandler()

    def run(self):
        try:
            while self._running:


                lane_lines, detected_sign, intersection_line, steering_angle, speed, _ , stamps = self.inPs.recv()

                stamps.append(time.time())

                print("[INFO[1]: Decision Thread]")
                print("Time delay 1: (decision - detection) : {:.2f} ms".format(stamps[2]-stamps[1]))
                print("Time delay 2: (decision - cam) : {:.2f} ms".format(stamps[2]-stamps[0]))


                data = [lane_lines, detected_sign, intersection_line, steering_angle, speed]

                control_data = self.decisions.doState(data)


                #self.outPs.send(control_data)

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed : " , e ,"\n")
            pass
