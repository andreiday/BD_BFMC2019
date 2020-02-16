# will start all the processes with their threads
import sys
sys.path.append('.')
import os

import time
import signal

import multiprocessing

# windows stuff - nope
# multiprocessing.set_start_method('spawn')

from multiprocessing import Pipe, Process, Event


# hardware imports
from src.hardware.camera.cameraprocess               import CameraProcess
from src.hardware.serialhandler.serialhandler        import SerialHandler

# utility imports
from src.utils.cameraspoofer.cameraspooferprocess  import CameraSpooferProcess
from src.utils.camerastreamer.camerareceiver import CameraReceiver

# image processing imports
from src.data.imageprocessing.lanefollowprocess import LaneFollowProcess

# test consumer process
from src.data.consumer.consumerprocess import Consumer as SerialSimulationProc

dir = os.path.join("src","vid")


def main():
    #================================ PROCESSES ==============================================
    allProcesses = list()

    camR, camS = Pipe(duplex = False)
    serialRecv, steerAngle = Pipe(duplex = False)

    udpRecv = CameraReceiver([],[])
    allProcesses.append(udpRecv)

    #================================ CAMERA Handler ==============================================
    # camSpoofer = CameraSpooferProcess([],[camS], dir)
    # allProcesses.append(camSpoofer)
    #
    # #================================ LaneDetect ==============================================
    # laneFollowRecv = LaneFollowProcess([camR], [steerAngle])
    # allProcesses.append(laneFollowRecv)
    #
    #
    # #================================ SERIAL ==============================================
    # testSerialSimProc = SerialSimulationProc([serialRecv],[])
    # allProcesses.append(testSerialSimProc)


    #SerialProc = SerialHandler([serialRecv],[])
    #allProcesses.append(SerialProc)

    #================================ PROCESS HANDLER ==============================================

    print("Starting the processes!")
    print(allProcesses)
    for proc in allProcesses:
        proc.daemon = True
        proc.start()

    blocker = Event()

    try:
        blocker.wait()
    except KeyboardInterrupt:
        print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
        for proc in allProcesses:
            if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
                print("Process with stop",proc)
                proc.stop()
                proc.join()
            else:
                print("Process without stop",proc)
                proc.terminate()
                proc.join()


if __name__ == "__main__":
    main()
