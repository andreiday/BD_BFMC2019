import sys
import time
import os
from src.utils.templates.threadwithstop import ThreadWithStop
from src.brain.decisionmaking.decisionhandle import DecisionHandler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

sys.path.append('.')


class DecisionThread(ThreadWithStop):
    def __init__(self, inP, outP):

        super(DecisionThread, self).__init__()
        self.daemon = True

        self.inPs = inP
        self.outPs = outP
        self.decisions = DecisionHandler()

    def run(self):
        try:
            while self._running:

                steering = self.inPs.recv()
                
                '''
                stamps.append(time.time())

                print("[INFO[1]: Decision Thread]")
                print("Time delay 1: (decision - detection) : {:.2f} ms".format(stamps[2]-stamps[1]))
                print("Time delay 2: (decision - cam) : {:.2f} ms".format(stamps[2]-stamps[0]))


                data = [lane_lines, detected_sign, intersection_line, steering_angle, speed]

                control_data = self.decisions.doState(data)
                '''
                #logging.debug("Steering {}".format(steering))
                self.outPs.send(steering)

        except Exception as e:
            logging.exception("Failed:{}".format(e))
            pass

        finally:
            self.outPs.close()
            logging.info("DecisionThread Pipe successfully closed")

    def stop(self):
        super(DecisionThread, self).stop()