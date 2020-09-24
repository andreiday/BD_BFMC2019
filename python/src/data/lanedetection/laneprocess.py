from src.utils.templates.workerprocess import WorkerProcess
from src.data.lanedetection.lanethread import LaneDetThread

"""
Create lane detection thread
"""


class LaneDetectionProcess(WorkerProcess):
    def __init__(self, inPs, outPs):
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
        super(LaneDetectionProcess, self).__init__(inPs, outPs)

    def _init_threads(self):
        '''
        '''
        laneTh = LaneDetThread(self.inPs[0], self.outPs[0])
        self.threads.append(laneTh)

    def run(self):
        super(LaneDetectionProcess, self).run()

    def stop(self):
        super(LaneDetectionProcess, self).stop()
