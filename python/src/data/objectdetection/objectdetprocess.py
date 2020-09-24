import sys
from src.data.objectdetection.signthread import SignThread
from src.utils.templates.workerprocess import WorkerProcess

sys.path.append('.')


class ObjectDetectProcess(WorkerProcess):
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
        super(ObjectDetectProcess, self).__init__(inPs, outPs)

    def _init_threads(self):
        '''
        '''
        signTh = SignThread(self.inPs[0], self.outPs[0])
        self.threads.append(signTh)

    def run(self):
        super(ObjectDetectProcess, self).run()

    def stop(self):
        super(ObjectDetectProcess, self).stop()
