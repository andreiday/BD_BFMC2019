import io
import time
import datetime
import sys

sys.path.append('.')

import multiprocessing
from multiprocessing import Process
from threading import Thread
from src.data.brain.controller.controlTh import Controller
from src.utils.templates.workerprocess import WorkerProcess

class ControllerProcess(WorkerProcess):
    def __init__(self, inPs, outPs):
        """Process that:
            -   receives information about the frames from the cameraprocess.
            -   outputs information about the computed steering angle

        Parameters
        ----------
            input pipes
        outPs : list()
            output pipes
        daemon : bool, optional
            daemon process flag, by default True
        """
        super(ControllerProcess,self).__init__(inPs, outPs)


    def _init_threads(self):
        '''
        '''
        controlTh = Controller(self.inPs[0], self.outPs[0])
        self.threads.append(controlTh)


    def run(self):
        super(ControllerProcess,self).run()
