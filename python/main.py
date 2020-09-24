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
import os

from multiprocessing import Pipe, Event

# hardware imports
from src.hardware.camera.cameraprocess import CameraProcess
from src.hardware.serialhandler.serialhandler import SerialHandler

# data acquisition imports
from src.data.lanedetection.laneprocess import LaneDetectionProcess
from src.data.objectdetection.objectdetprocess import ObjectDetectProcess
from src.data.gpstracker.gpsprocess import GPSProcess

# brian imports
from src.brain.controller.controllerprocess import ControllerProcess
from src.brain.decisionmaking.decisionmakingproc import DecisionMakingProcess
from src.brain.datafusion.datafusionproc import DataFusionProcess

# utility imports
from src.utils.cameraspoofer.cameraspooferprocess import CameraSpooferProcess

# others


# udp data sending & receiving imports
# from src.utils.camerastreamer.camerareceiver import CameraReceiver

commSerial_b = False          # enable serial communication
spoof_b = True                # enable camera spoofer
gps_b = True                  # enable gps communication
objDet_b = True
laneDet_b = True
flowTest_b = False

sys.path.append('.')
dir = os.path.join("src", "vid")


def main():

    # ======================= PROCESSES =======================
    allProcesses = list()
    allCamPipes = list()
    allDataFzzInPipes = list()

    # pipes description

    # allCamPipes()         - output from camera process to:
    # laneCamRecv           - input for lane detection process
    # objCamRecv            - input for object detection process

    laneCamRecv, laneCamSend = Pipe(duplex=False)
    objCamRecv, objCamSend = Pipe(duplex=False)


    # fzzIn        - input for data fusion process from:
    # laneOut      - output from lane detection process             TODO
    # objDetOut    - output from object recognition process         TODO
    # gpsOut       - output from gps process                        TODO

    laneFzzRecv, laneFzzSend = Pipe(duplex=False)
    objFzzRecv, objFzzSend = Pipe(duplex=False)

    #if gps_b:
    #    gpsFzzRecv, gpsFzzSend = Pipe(duplex=False)

    # fzzOut       - output from data fusion process to:
    # decIn        - input for decision making process              TODO

    if flowTest_b:
        decIn, fzzOut = Pipe(duplex=False)

    # decOut        - output from decision making process to:       TODO
    # cntIn         - input for controller process                  TODO

    # serialIn      - input for serial communication from:
    # cntOut        - output from controller

        cntIn, decOut = Pipe(duplex=True)       # controller I/O <=> decision making I/O
        serialIn, cntOut = Pipe(duplex=True)    # controller I/O <=> serial I/O

    allCamPipes.append(laneCamSend)
    allCamPipes.append(objCamSend)

    allDataFzzInPipes.append(laneFzzRecv)
    allDataFzzInPipes.append(objFzzRecv)

    #if gps_b:
    #    allDataFzzInPipes.append(gpsFzzRecv)

    #
    # ================================ CAMERA Handler ==============================================
    # create process with :
    #       - input ([])            :   []
    #       - output ([camOut])     :   [[stamps], frame]]

    if spoof_b:
        camSpoofer = CameraSpooferProcess([], allCamPipes, dir)
        allProcesses.append(camSpoofer)
    else:
        camHwPi = CameraProcess([], allCamPipes)
        allProcesses.append(camHwPi)

    # ================================ Lane detection process =============================================
    # create process with :
    #       - input ([laneIn])      :   [[stamps], frame]]
    #       - output ([laneOut])    :

    if laneDet_b:
        laneDetection = LaneDetectionProcess([laneCamRecv], [laneFzzSend])
        allProcesses.append(laneDetection)


    # ================================ Object detection process =============================================
    # create process with :
    #       - input ([objDetIn])      :   [[stamps], frame]]
    #       - output ([objDetOut])    :

    if objDet_b:
        objDetection = ObjectDetectProcess([objCamRecv], [objFzzSend])
        allProcesses.append(objDetection)

    if gps_b:
        gpsProcess = GPSProcess([], [])
        allProcesses.append(gpsProcess)
   
   
    # ================================ Data fusion process ==============================================
    # create process with :
    #       - input ([fzzIn])            :
    #       - output ([fzzOut])           :

    dataFusionProc = DataFusionProcess(allDataFzzInPipes, [])
    allProcesses.append(dataFusionProc)

    # ================================ Decision making proc ==========================================
    # create process with :
    #       - input ([decIn])            :   []
    #       - output ([decOut])           :   []
    
    if flowTest_b:
        decisionMakingProc = DecisionMakingProcess([decIn], [decOut])
        allProcesses.append(decisionMakingProc)

    # ================================ CONTROLLER ==============================================
    # create process with :
    #       - input ([cntIn])            :   []
    #       - output ([cntOut])          :   []
    if commSerial_b:
        controllerProc = ControllerProcess([cntIn],[cntOut])
        allProcesses.append(controllerProc)

    # ================================ Serial Handler ================================================
    # create process with :
    #       - input ([serialIn])    :   []
    #       - output ([])     :   []

        serialProc = SerialHandler([serialIn],[])
        allProcesses.append(serialProc)

    # ================================ PROCESS HANDLER ==============================================

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
            if hasattr(proc, 'stop') and callable(getattr(proc, 'stop')):
                print("Process with stop", proc)
                proc.stop()
                proc.join()
            else:
                print("Process without stop", proc)
                proc.terminate()
                proc.join()


if __name__ == "__main__":
    main()
