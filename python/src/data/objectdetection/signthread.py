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
from src.utils.templates.threadwithstop import ThreadWithStop
from src.utils.imageprocessing.frameprocessing import DetectionProcessing
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sys.path.append('.')


class SignThread(ThreadWithStop):

    def __init__(self, inP, outP):
        super(SignThread, self).__init__()
        self.daemon = True

        self.detectionProcessing = DetectionProcessing()

        self.inPs = inP
        self.outPs = outP

        self.enableDetection = True
        self.detected_sign = "None"

    def run(self):
        try:
            while self._running:

                # receive frames and stamp from pipe

                stamps, frame = self.inPs.recv()

                stamps.append(time.time())

                if self.enableDetection:
                    enabled = time.time()
                    self.detected_sign = self.detectionProcessing.detectSigns(frame)
                    self.enableDetection = False

                self.detected_sign = str(self.detected_sign)

                logging.debug("Detected sign: {}".format(self.detected_sign))

                if self.enableDetection is False and time.time()-enabled > 0.25:
                    self.enableDetection = True

                logging.debug("sign:", stamps)

                self.outPs.send([[stamps], self.detected_sign])

        except Exception as e:
            logging.exception(os.path.realpath(__file__))
            logging.exception("Failed:", e, "\n")
            pass

        finally:
            self.outPs.close()
            logging.info("SignTh Pipe successfully closed")

    def stop(self):
        super(SignThread, self).stop()
