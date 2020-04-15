import sys
import time
import os
sys.path.append('.')
from imutils.video import FPS
from src.utils.templates.workerthread import WorkerThread
from src.data.brain.decisionmaking.decisionhandle import DecisionHandler

class DecisionThread(WorkerThread):
    def __init__(self, inPs, outPs):

        self.inPs = inPs
        self.outPs = outPs
        self.decisions = DecisionHandler()
        super(DecisionThread, self).__init__(self.inPs, self.outPs)


    def run(self):
        try:
            while True:

                # fps = FPS().start()

                lane_lines, detected_sign, intersection_line, steering_angle, speed, _ = self.inPs.recv()

                data = [lane_lines, detected_sign, intersection_line, steering_angle, speed]

                control_data = self.decisions.doState(data)


                self.outPs.send(control_data)

                # fps.stop()
                # print("[INFO] elapsed time decisions: {:.2f}".format(fps.elapsed()))

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed : " , e ,"\n")
            pass
