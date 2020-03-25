import sys
import os
sys.path.append('.')

from src.utils.templates.threadwithstop import ThreadWithStop
from src.data.imageprocessing.frameprocessing import FrameProcessing

class WriteThreadFrameProc(ThreadWithStop):

    def __init__(self, inP, outP):
        super(WriteThreadFrameProc, self).__init__()
        self.inP = inP
        self.outP = outP
        self.frameProcessing = FrameProcessing()

    def run(self):
        while(self._running):
            try:
                while True:
                    # receive frames and stamp from pipe
                    stamp, frame = self.inP.recv()

                    lane_lines = self.frameProcessing.detectLanes(frame)
                    detected_sign = self.frameProcessing.detectSigns(frame)


                    # print("\nStamp time frame proc: ", stamp)
                    # print("lanes: ", lane_lines)
                    # print("detected sign: ", detected_sign)

                    self.outP.send([frame, lane_lines, detected_sign])

            except Exception as e:
                print(os.path.realpath(__file__))

                print("Failed to process frames :" , e ,"\n")
                pass
