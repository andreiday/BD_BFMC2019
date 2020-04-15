import sys
import os
import time
sys.path.append('.')

from imutils.video import FPS
from src.utils.templates.threadwithstop import ThreadWithStop
from src.data.imageprocessing.frameprocessing import FrameProcessing
from src.data.imageprocessing.move import MoveLogic
import time


class WriteThreadFrameProc(ThreadWithStop):

    def __init__(self, inP, outP):
        super(WriteThreadFrameProc, self).__init__()

        self.inP = inP
        self.outP = outP
        self.frameProcessing = FrameProcessing()
        self.moveLogic = MoveLogic()
        self.enableDetection = True
        self.detected_sign = "None"

        # self.lane_lines = [[[27, 480, 219, 240]], [[647, 480, 470, 240]]]

    def run(self):
        while(self._running):
            try:
                while True:
                    # receive frames and stamp from pipe
                    # fps = FPS().start()
                    stamp, frame = self.inP.recv()

                    lane_lines = self.frameProcessing.detectLanes(frame)

                    if self.enableDetection:
                        enable = time.time()
                        self.detected_sign = self.frameProcessing.detectSigns(frame)
                        self.enableDetection = False

                    self.detected_sign = str(self.detected_sign)

                    intersection_line = self.frameProcessing.detectIntersection(frame)

                    steering_angle = self.moveLogic.getSteer(frame, lane_lines)
                    speed = self.moveLogic.getSpeed(lane_lines, steering_angle)

                    steering_angle = round(steering_angle, 3)
                    speed = round(speed, 3)

                    # steering_frame = display_heading_line(frame,steering_angle)
                    # showVideo("steeringframe", steering_frame)

                    self.outP.send([lane_lines, self.detected_sign, intersection_line , steering_angle, speed, frame])

                    if self.enableDetection == False and time.time()-enable > 0.42:
                        self.enableDetection = True

                    # fps.stop()
                    # print("[INFO] elapsed time frame proc: {:.2f}".format(fps.elapsed()))


            except Exception as e:
                print(os.path.realpath(__file__))

                print("Failed to start WriteThreadFrameProc because :" , e ,"\n")
                pass
