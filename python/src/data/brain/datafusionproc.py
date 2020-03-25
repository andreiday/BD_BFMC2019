import io
import time
import datetime
import sys

sys.path.append('.')

import multiprocessing
from multiprocessing import Process
from threading import Thread

from src.utils.templates.workerprocess import WorkerProcess
from src.data.brain.move import MoveLogic
from src.data.brain.writethread import WriteThreadFzz

class DataFusionProcess(WorkerProcess):
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
        super(DataFusionProcess,self).__init__(inPs, outPs)



    def _init_threads(self):
        '''
        '''
        writeTh = WriteThreadFzz(self.inPs[0], self.outPs[0])
        self.threads.append(writeTh)

    def run(self):
        super(DataFusionProcess,self).run()

    def displayInfo(self):
        """Display all parameters on the screen.
        """
        # clear stdout for a smoother display
        os.system('cls' if os.name=='nt' else 'clear')
