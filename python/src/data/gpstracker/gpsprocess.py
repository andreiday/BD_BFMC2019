import time
from threading import Thread
from src.utils.templates.workerprocess import WorkerProcess
from src.data.gpstracker.gpstracker import GpsTracker


class GPSProcess(WorkerProcess):
    def __init__(self, InPs, outPs):
        """
        Process that:
            -
            -

        Parameters
        ----------
        inPs : list()
            input pipes
        outPs : list()
            output pipes
        daemon : bool, optional
            daemon process flag, by default True
        """
        super(GPSProcess, self).__init__(InPs, outPs)
        #: serverData object with server parameters

    def _init_threads(self):
        '''
        '''
        self.gpsTh = GpsTracker()
        self.threads.append(self.gpsTh)

    def run(self):
        super(GPSProcess, self).run()

    def stop(self):
        super(GPSProcess, self).stop()
   