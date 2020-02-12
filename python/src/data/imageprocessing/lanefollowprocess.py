import io
import time
import datetime
import sys
sys.path.append('.')

import multiprocessing
from multiprocessing import Process
from threading import Thread

from src.utils.templates.workerprocess import WorkerProcess
from src.data.imageprocessing.frameprocessing import SteeringFrameProcessing
from src.hardware.serialhandler.messageconverter import MessageConverter


class LaneFollowProcess(WorkerProcess):
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

        super(LaneFollowProcess,self).__init__(inPs, outPs)


    def run(self):
        super(LaneFollowProcess,self).run()

    def _init_threads(self):
        '''
        '''
        for inPipe in self.inPs:
            for outPipe in self.outPs:
                self.threads.append(Thread(name = 'FrameReceiving', target = LaneFollowProcess._steer, args = ([],inPipe, outPipe)))



    @staticmethod
    def _steer(self, inPipe, outPipe):

        print('\n\nStarting frame processing')
        frame_process = SteeringFrameProcessing()

        while True:
            # receive frames and stamp from pipe
            stamp, frame = inPipe.recv()
            print("\nStamp time: ", stamp)

            # process the frames to output the steering angle
            steering_angle = frame_process.followLaneFrame(frame)
            steering_angle = round(steering_angle, 5)

            print("Steering angle: ", steering_angle)

            # convert steering angle in a message appropriate for sending through serial
            messageConverter = MessageConverter()


            commands = {
            'speed' : 0.12345,
            'steerAngle' : float(steering_angle),
            }

            msg = messageConverter.get_command('MCTL', **commands)

            # send move control message through the output pipe
            outPipe.send(msg)

            time.sleep(0.05)
