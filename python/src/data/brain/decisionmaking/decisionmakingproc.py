import io
import time
import datetime
import sys

sys.path.append('.')

import multiprocessing
from multiprocessing import Process
from threading import Thread

from src.utils.templates.workerprocess import WorkerProcess

from src.data.brain.decisionmaking.decisionthread import DecisionThread

class DecisionMakingProcess(WorkerProcess):
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
        super(DecisionMakingProcess,self).__init__(inPs, outPs)


    def _init_threads(self):
        '''
        '''
        decisionTh = DecisionThread(self.inPs[0], self.outPs[0])
        self.threads.append(decisionTh)


    def run(self):
        super(DecisionMakingProcess,self).run()
