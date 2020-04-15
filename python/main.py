# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

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
