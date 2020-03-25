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
sys.path.append('.')

from src.utils.templates.workerprocess import WorkerProcess
from threading import Thread

class Consumer(WorkerProcess):
    def __init__(self, inPs, outPs):
        """[summary]

        Parameters
        ----------
        inPs : list(Pipe)
            List of the input pipes
        outPs : list(Pipe)
            List of the output pipes
        """

        super(Consumer,self).__init__(inPs, outPs)

    def run(self):
        super(Consumer,self).run()

    def _init_threads(self):
        """Initialize the threads by adding a consume method for each input pipes.
        """

        for inPipe, outPipe in zip(self.inPs, self.outPs):
            thReadWrite = Thread(name='Consume',target=Consumer._consume, args=(inPipe, outPipe),daemon=False)
        self.threads.append(thReadWrite)

    @staticmethod
    def _consume(inPipe, outPipe):
        """A simple method to read the content from the input pipe to consume the content of the connection.

        Parameters
        ----------
        pipe : Pipe
            Input communication channel.
        """
        try:
            while True:
                res = inPipe.recv()

                movecommands = {
                    'action' : 'MCTL',
                    'speed' : float(res[0]),
                    'steerAngle' : float(res[1])
                }

                print("res: ", res)
                print("Value: ", movecommands, end="\n")
                # outPipe.send(movecommands)

        except Exception as e:
            print("Failed consumer process: " , e ,"\n")
            pass
