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
from src.utils.templates.threadwithstop import ThreadWithStop
import logging
import socket
from src.utils.imageprocessing.move import steeringFit
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sys.path.append('.')


class DisplayThread(ThreadWithStop):
    def __init__(self, inP):
        super(DisplayThread, self).__init__()
        self.inPs = inP
        self.timeDisplay = 0.25
        self.enableUdpSend = False

        if self.enableUdpSend:
            logger.info("Init udp sender to unity")
            self.clientIp = '192.168.1.4'
            self.portClient = 8052
            self.client_address = (self.clientIp, self.portClient)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.connect((self.client_address))

    def run(self):
        try:
            oldTime = 0
            stamps = []
            while self._running:
                # receive data and stamps from pipes
                stampSign, sign = self.inPs[0].recv()
                stampLane, steering = self.inPs[1].recv()
                gpsInfo = self.inPs[2].recv()
                traffic = self.inPs[3].recv()

                stamps.append(stampLane[0][0])
                stamps.append(stampLane[0][1])
                stamps.append(stampSign[0][1])
                stamps.append(gpsInfo[0])
                stamps.append(time.time())

                if self.enableUdpSend:
                    message = int.to_bytes(steering, length=1, byteorder='big', signed=True)
                    print(message)
                    self.client_socket.sendto(message, self.client_address)
                
                if time.time() - oldTime > self.timeDisplay:
                    oldTime = time.time()
                    """Display all parameters on the screen.
                    """
                    steering = steeringFit(steering, 1, 179, -23, 23)
                    steering = round(steering, 3)
                    # clear stdout for a smoother display
                    # os.system('cls' if os.name=='nt' else 'clear')
                   
                    logger.debug("\n========= Status ========="
                        "\nspeed:                       " + str("nothing") +
                        "\nsteering:                    " + str(steering) +
                        "\nsign:                        " + str(sign) +
                        "\nTraffic:                     " + str(traffic) +
                        "\nGPS:                         " + str(gpsInfo[1]))
                    '''
                    logger.debug("\n========= Delays Delta ========= " +
                        "\nCam -> Lane:                 " + str(stamps[1]-stamps[0]) +
                        "\nCam -> Sign:                 " + str(stamps[2]-stamps[0]) +
                        "\nCam -> Fzz:                  " + str(stamps[3]-stamps[0]) +
                        "\nLane -> Fzz:                 " + str(stamps[3]-stamps[1]) +
                        "\nSign -> Fzz:                 " + str(stamps[3]-stamps[2]))
                     '''
                stamps.clear()
                
        except Exception as e:
            logging.exception("Failed : ", e)
            pass

    def stop(self):
        if self.enableUdpSend:
            self.client_socket.close()
        super(DisplayThread, self).stop()
