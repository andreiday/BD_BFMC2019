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
from src.utils.templates.threadwithstop import ThreadWithStop

import numpy as np
import argparse
import imutils
import time
import cv2
import glob
import os

class SignDetection(ThreadWithStop):

    def __init__(self):
        super(SignDetection, self).__init__()

        self.label = "none"
        # self.RUN_DETECTION = True

        self.CLASSES = ["park", "pedestrians", "priority", "stop"]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self.net = cv2.dnn.readNetFromTensorflow('ssdlite_mobilenet_v2_coco.pb', 'graph.pbtxt')

    def sendFrame(self, frame):
        self.frame = frame

    def run(self):
        try:
            while(self._running):
                self.frame = cv2.resize(self.frame, (300,300))
                (h, w) = self.frame.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(self.frame, (300, 300)), swapRB=True)
                # grab the frame dimensions and convert it to a blob
                # pass the blob through the network and obtain the detections and
                # predictions
                self.net.setInput(blob)
                detections = self.net.forward()
                # loop over the detections
                for i in np.arange(0, detections.shape[2]):
                    # extract the confidence (i.e., probability) associated with
                    # the prediction
                    confidence = detections[0, 0, i, 2]
                    # filter out weak detections by ensuring the `confidence` is
                    # greater than the minimum confidence
                    if confidence > 0.7:
                        # extract the index of the class label from the
                        # `detections`
                        idx = int(detections[0, 0, i, 1])
                        # draw the prediction on the frame
                        self.label = "{}".format(self.CLASSES[idx-1])

        except Exception as e:
            print(os.path.realpath(__file__))
            print("Failed to run sign detection thread: " , e ,"\n")
            pass

    def getLabel(self):
        return self.label
