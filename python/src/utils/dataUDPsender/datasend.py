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


import socket
import struct
import time
import numpy as np
from multiprocessing import Process
from threading import Thread
import sys
import cv2
from io import BytesIO

from src.utils.templates.workerprocess import WorkerProcess

class DataSend(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
        """Process used for sending computed data over UDP to unity for training purpose

        Parameters
        ----------
        inPs : list(Pipe)
            List of input pipes, only the first pipe is used to transfer the data as a string
        outPs : list(Pipe)
            List of output pipes (not used at the moment)
        """
        super(DataSend, self).__init__(inPs, outPs)
        self.serverIp = '192.168.1.254'
        self.port = 2244
        self.server_address = (self.serverIp, self.port)

    def run(self):
        self._init_socket()
        super(DataSend, self).run()

    def _init_threads(self):
        """Initialize the sending thread.
        """
        # if self._blocker.is_set():
        #     return

        sendTh = Thread(name='DataStream Sending',target=self._send_thread, args=(self.inPs, ))
        sendTh.daemon = True
        self.threads.append(sendTh)

    # ===================================== INIT SOCKET ==================================
    def _init_socket(self):
        """Initialize the socket.
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.connect((self.serverIp, self.port))
        # Trying repeatedly to connect the UnityReceiver.
        # try:
        #     while not self._blocker.is_set():
        #         try:
        #             self.client_socket.connect((self.serverIp, self.port))
        #         except ConnectionRefusedError as error:
        #             time.sleep(0.5)
        #             pass
        # except KeyboardInterrupt:
        #     self._blocker.set()
        #     pass

    def _send_thread(self, inPs):
        """Send data received through the input pipe.
        """
        print("successfully started udp datasend")

        try:
            while True:
                stamp = time.time()

                for p in self.inPs:
                    data = p.recv()

                stamped_data = [[stamp], data]

                stamped_data = str(stamped_data).encode()
                print(stamped_data)

                self.client_socket.sendto(stamped_data, self.server_address)

        except Exception as e:
            print("Failed to transmit data:", e, "\n")
            # Reinitialize the socket for reconnecting to client.
            self.client_socket.close()
            self._init_socket()
            pass
