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

# image processing imports
from src.data.imageprocessing.frameprocessingprocess import FrameProcessingProcess

# import datafusion process
# from src.data.brain.datafusion.datafusionproc import DataFusionProcess

# import decision making process
from src.data.brain.decisionmaking.decisionmakingproc import DecisionMakingProcess

# temporarly purposed as controller
# from src.data.consumer.consumerprocess import Consumer as ControllerProcess
from src.data.brain.controller.controllerprocess import ControllerProcess
# udp data sending & receiving imports
# from src.utils.camerastreamer.camerareceiver import CameraReceiver as UnityReceiver

dir = os.path.join("src","vid")

commSerial = True

def main():
    #================================ PROCESSES ==============================================
    allProcesses = list()


    camR, camS = Pipe(duplex = False)
    frameR, frameS = Pipe(duplex = False)
    # cntR, decS = Pipe(duplex = False)
    serialR, decS = Pipe(duplex = False)

    # dataFzzIn, frameProcDataOut = Pipe(duplex = False)
    # decisionIn, dataFzzOut = Pipe(duplex = False)
    # with controller process
    # controllerIn, decisionOut = Pipe(duplex = False)
    # serialRecv, controllerOut = Pipe(duplex = False)

    # without controller process
    # serialRecv, decisionOut = Pipe(duplex = False)


    #================================ CAMERA Handler ==============================================
    camSpoofer = CameraSpooferProcess([],[camS], dir)
    allProcesses.append(camSpoofer)

    #================================ Frameprocessing process ==============================================
    frameProcessing = FrameProcessingProcess([camR], [frameS])
    allProcesses.append(frameProcessing)

    # #================================ Movement process ==============================================
    # dataFusionProc = DataFusionProcess([dataFzzIn], [dataFzzOut])
    # allProcesses.append(dataFusionProc)

    #================================ Decision making proc ==========================================
    decisionMakingProc = DecisionMakingProcess([frameR], [decS])
    allProcesses.append(decisionMakingProc)
    #
    # #================================ CONTROLLER ==============================================
    # controllerProc = ControllerProcess([cntR],[cntS])
    # allProcesses.append(controllerProc)

    #================================ Serial     ==============================================
    if commSerial:
        serialProc = SerialHandler([serialR],[])
        allProcesses.append(serialProc)

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
