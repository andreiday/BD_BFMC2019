from src.utils.templates.workerprocess import WorkerProcess
from src.data.gpstracker.gpstracker import GpsTracker
from src.data.trafficlights import Listener as TrafficLightsTrack
from threading import Thread
import time
import logging

trafficTracker = TrafficLightsTrack.listener()
gpstracker = GpsTracker()

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class EnvironmentCommProcess(WorkerProcess):
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
        self.gpsOutP = outPs[0]
        self.traficOutP = outPs[1]
        
        self.timeListen = 1
        self.__running = False
        super(EnvironmentCommProcess, self).__init__(InPs, outPs)

    def _init_threads(self):
        '''
        '''
        if self._blocker.is_set():
            return

        listenersTh = Thread(name='listenersTh', target=self.runListeners, args=(self.outPs,))
        listenersTh.daemon = True
        self.threads.append(listenersTh)

        self.threads.append(trafficTracker)
        self.threads.append(gpstracker)

    def run(self):
        self.__running = True
        super(EnvironmentCommProcess, self).run()

    def stop(self):
        self.__running = False
        super(EnvironmentCommProcess, self).stop()

    def runListeners(self, outPs):
        oldTime = 0
        gpsInfo = []
        while self.__running:
            # Semaphore colors list
            colors = ['red', 'yellow', 'green']   
            gpsInfo.append(time.time())
            gpsInfo.append(gpstracker.coor())
            # Get time stamp when starting tester

            if time.time() - oldTime > self.timeListen:
                oldTime = time.time()
                # Print each semaphore's data
                logger.debug("S1 color {}, code {}.".format(colors[trafficTracker.s1_state], str(trafficTracker.s1_state)))
                #logger.debug("S2 color {}, code {}.".format(colors[trafficTracker.s2_state], str(trafficTracker.s2_state)))
                #logger.debug("S3 color {}, code {}.".format(colors[trafficTracker.s3_state], str(trafficTracker.s3_state)))
                logger.debug("GPS Coords {}".format(gpstracker.coor()))
            
            self.gpsOutP.send(gpsInfo)
            self.traficOutP.send((colors[trafficTracker.s1_state], str(trafficTracker.s1_state)))

            gpsInfo.clear()
