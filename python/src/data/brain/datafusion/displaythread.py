import sys
import time
import os
sys.path.append('.')

from src.utils.templates.threadwithstop import ThreadWithStop

class DisplayThread(ThreadWithStop):

    def __init__(self, inP):
        super(DisplayThread, self).__init__()
        self.inP = inP
        self.speed = 0.0

    def run(self):
        try:
            while True:

                # receive frames and stamp from pipe
                lane_lines, detected_sign, steering_angle = self.inP.recv()

                # process the frames, output no. lanes
                # os.system('cls' if os.name=='nt' else 'clear')

                print("Calculated lane lines: ", lane_lines)
                print("Steering angle: ", steering_angle)
                print("Speed: ", self.speed)
                print("Detected sign: ", detected_sign)
                print("############### Other processes prints ####################")

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed : " , e ,"\n")
            pass
