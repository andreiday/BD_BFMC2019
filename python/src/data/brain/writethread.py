import sys
import time
import os
sys.path.append('.')

from src.utils.templates.threadwithstop import ThreadWithStop
from src.data.brain.move import MoveLogic

class WriteThreadFzz(ThreadWithStop):

    def __init__(self, inP, outP):
        super(WriteThreadFzz, self).__init__()
        self.inP = inP
        self.outP = outP
        self.moveLogic = MoveLogic()

    def run(self):
        try:
            while True:

                # receive frames and stamp from pipe
                frame, lane_lines, detected_sign = self.inP.recv()

                # process the frames, output no. lanes
                steering_angle = self.moveLogic.getSteer(frame, lane_lines)
                speed = self.moveLogic.getSpeed(steering_angle)

                steering_angle = round(steering_angle, 5)

                os.system('cls' if os.name=='nt' else 'clear')

                print("Calculated lane lines: ", lane_lines)
                print("Steering angle: ", steering_angle)
                print("Speed: ", speed)
                print("Detected sign: ", detected_sign)


                # send no. lanes through pipe
                # outPipe.send([speed, steering_angle, lane_lines])

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed : " , e ,"\n")
            pass
