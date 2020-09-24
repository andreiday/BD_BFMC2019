# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
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
