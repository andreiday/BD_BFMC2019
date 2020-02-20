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

class MovementProcess(WorkerProcess):
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

        super(MovementProcess,self).__init__(inPs, outPs)

    def run(self):
        super(MovementProcess, self).run()

    def _init_threads(self):
        '''
        '''
        for inPipe in self.inPs:
            for outPipe in self.outPs:
                self.threads.append(Thread(name = 'MovementProcess', target = MovementProcess._steerSpeed, args = (inPipe, outPipe)))

    def _steerSpeed(inPipe, outPipe):
        print('Starting control process\n')
        move_logic = MoveLogic()

        while True:
            # receive frames and stamp from pipe
            frame, lane_lines, _ = inPipe.recv()
            #print("\nStamp time: ", stamp)

            # print("Lane lines movement: ", lane_lines)

            # process the frames, output no. lanes
            steering_angle = move_logic.getSteer(frame, lane_lines)
            steering_angle = round(steering_angle, 5)
            speed = move_logic.getSpeed(steering_angle)

            #print("steering_angle: ", steering_angle)
            #print("Speed: ", speed)


            # send no. lanes through pipe
            outPipe.send([speed, steering_angle, lane_lines])

    def _detectedSign(inPipe, outPipe):
        while True:
            # get detected sign through pipe
            _, _, detected_sign = inPipe.recv()

            print("DETECTED SIGN: ", detected_sign)
