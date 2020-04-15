import sys
import time
import os
sys.path.append('.')

from src.utils.templates.threadwithstop import ThreadWithStop


class WriteThreadFzz(ThreadWithStop):

    def __init__(self, inP, outP):
        super(WriteThreadFzz, self).__init__()
        self.inP = inP
        self.outP = outP


    def run(self):
        try:
            while True:

                # receive frames and stamp from pipe
                lane_lines, detected_sign, steering_angle = self.inP.recv()
                print("test", lane_lines)
                # process the frames, output no. lanes

                # send no. lanes through pipe
                #self.outP.send([speed, steering_angle, detected_sign])

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed to start WriteThreadFzz because : : " , e ,"\n")
            pass
