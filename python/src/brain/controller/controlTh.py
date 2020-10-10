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
from src.utils.templates.workerthread import WorkerThread
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
sys.path.append('.')
from src.utils.imageprocessing.move import steeringFit

class Controller(WorkerThread):

    def __init__(self, inPs, outPs):
        self.inPs = inPs
        self.outPs = outPs
        super(Controller, self).__init__(self.inPs, self.outPs)
        self.daemon = True


    def run(self):
        try:
            while True:
                steering_angle = self.inPs.recv()
                
                steering_car = steeringFit(steering_angle[0], 1, 179, -23, 23)

                movecommands = {
                    'action' : 'MCTL',
                    'speed' : float(0),
                    'steerAngle' : float(steering_car),
                }

                #print(movecommands)
                self.outPs.send(movecommands)
        
        except Exception as e:
            logging.exception("Failed:{}".format(e))
            pass

        finally:
            self.outPs.close()
            logging.info("ControlTh Pipe successfully closed")

