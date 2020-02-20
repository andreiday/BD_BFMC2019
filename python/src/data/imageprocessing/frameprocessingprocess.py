import io
import time
import datetime
import sys
sys.path.append('.')

import multiprocessing
from multiprocessing import Process
from threading import Thread

from src.utils.templates.workerprocess import WorkerProcess
from src.data.imageprocessing.frameprocessing import FrameProcessing



class FrameProcessingProcess(WorkerProcess):
    #================================ LANE DETECTION PROCESS =====================================
    def __init__(self, inPs, outPs):
        """Process that:
            -   receives information about the frames from the cameraprocess.
            -   outputs information about the computed steering angle

        Parameters
        ----------
        inPs : list()
            input pipes
        outPs : list()
            output pipes
        daemon : bool, optional
            daemon process flag, by default True
        """

        super(FrameProcessingProcess,self).__init__(inPs, outPs)


    def run(self):
        super(FrameProcessingProcess,self).run()

    def _init_threads(self):
        '''
        '''
        for inPipe in self.inPs:
            for outPipe in self.outPs:
                self.threads.append(Thread(name = 'FrameProcessingProcess', target = FrameProcessingProcess._frameProcAlgos, args = (inPipe, outPipe)))


    @staticmethod
    def _frameProcAlgos(inPipe, outPipe):

        print('Starting frame processing')
        frame_processing = FrameProcessing()

        while True:
            # receive frames and stamp from pipe
            stamp, frame = inPipe.recv()
            print("##### IMAGE PROCESSING #####")

            print("\nStamp time frame proc: ", stamp)

            # process the frames, output no. lanes
            lane_lines = frame_processing.detectLanes(frame)

            detected_sign = frame_processing.detectSigns(frame)

            # send no. lanes through pipe

            outPipe.send([frame, lane_lines, detected_sign])
