import sys
sys.path.append('.')

import threading

from threading import Thread
from multiprocessing import Process
from src.utils.templates.workerthread import WorkerThread

class Controller(WorkerThread):

    def __init__(self, inPs, outPs):
        self.inPs = inPs
        self.outPs = outPs
        super(Controller, self).__init__(self.inPs, self.outPs)
        self.daemon = True


    def run(self):
        while True:
            action, speed, steering_angle = self.inPs.recv()

            movecommands = {
                'action' : action,
                'speed' : float(speed),
                'steerAngle' : float(steering_angle),
            }

            print(movecommands)
            # self.outPs.send(movecommands)
