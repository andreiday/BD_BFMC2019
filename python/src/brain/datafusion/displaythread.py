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
import time
import os
from src.utils.templates.threadwithstop import ThreadWithStop
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sys.path.append('.')


class DisplayThread(ThreadWithStop):
    def __init__(self, inP):
        super(DisplayThread, self).__init__()
        self.inPs = inP
        self.timeDisplay = 0

    def run(self):
        try:
            stamps = []
            while self._running:
                # receive frames and stamp from pipe
                stampLane, steering = self.inPs[0].recv()
                stampSign, sign = self.inPs[1].recv()
                #stampGps, coords = self.inPs[2].recv()

                if time.time() - self.timeDisplay > 0.5:

                    self.timeDisplay = time.time()

                    stamps.append(stampLane[0][0])
                    stamps.append(stampLane[0][1])
                    stamps.append(stampSign[0][1])
                    stamps.append(time.time())

                    #print("fusion: ", stamps, steering, sign)

                    """Display all parameters on the screen.
                    """

                    # clear stdout for a smoother display
                    #os.system('cls' if os.name=='nt' else 'clear')
                    '''
                    print("========= Status =========")

                    print(
                        "speed:                         " + str(test) +
                        "\nangle:                       " + str(steering) +
                        "\nsign:                        " + str(sign) +
                        "\nlane lines:                  " + str(test) +
                        "\nintersection line flag:      " + str(test) +
                        "\ncurrent state label:         " + str(test) +
                        "\ncurrent states:              " + str(test) +
                    

                    logger.debug("\n========= Delays ========= " +
                        "\nCam -> Lane:                 " + str(stamps[1]-stamps[0]) +
                        "\nCam -> Sign:                 " + str(stamps[2]-stamps[0]) +
                        "\nCam -> Fzz:                  " + str(stamps[3]-stamps[0]) +
                        "\nLane -> Fzz:                 " + str(stamps[3]-stamps[1]) +
                        "\nSign -> Fzz:                 " + str(stamps[3]-stamps[2]))
                    '''

                    stamps.clear()

        except Exception as e:
            logger.exception(os.path.realpath(__file__))
            logger.exception("Failed : ", e, "\n")
            pass

    def stop(self):
        super(DisplayThread, self).stop()
