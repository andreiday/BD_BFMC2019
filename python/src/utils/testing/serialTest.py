import sys
from src.hardware.serialhandler.messageconverter import MessageConverter
#from src.hardware.serialhandler.filehandler import FileHandler
import serial

sys.path.append(os.path.abspath('.'))
'''
    commands = {
                'MCTL' : [ ['speed','steerAngle'],[float, float],  [True]  ],
                'BRAK' : [ ['steerAngle' ],       [float],         [False] ],
                'PIDA' : [ ['activate'],       [ bool],         [False] ],
                #'SFBR' : [ ['activate'],       [ bool],         [False] ],
                #'DSPB' : [ ['activate'],       [ bool],         [False] ],
                'ENPB' : [ ['activate'],       [ bool],         [False] ],

                # optional commands
                'PIDS' : [ ['kp','ki','kd','tf'],[ float, float, float, float], [True] ],
                'SPLN' : [ ['A','B','C','D', 'dur_sec', 'isForward'],
                           [complex, complex, complex, complex, float, bool], [False] ],
            }
'''


def CreateBezier(p1='1.0+1.0j', p2='1.54+0.44j', p3='1.54-0.44j', p4='1.0-1.0j', duration_sec=1.0, isForward=True):

    data = {}
    A = complex(p1)
    B = complex(p2)
    C = complex(p3)
    D = complex(p4)

    data['A'] = A
    data['B'] = B
    data['C'] = C
    data['D'] = D
    data['dur_sec'] = duration_sec
    data['isForward'] = isForward

    return data


def SendCmd():
    devFile = '/dev/ttyACM0'
    logFile = 'historyFile.txt'
    #historyFile = FileHandler(logFile)

    serialCom = serial.Serial(devFile, 256000, timeout=0.1)
    serialCom.flushInput()
    serialCom.flushOutput()

    msgConverter = MessageConverter()
    CMD = CreateBezier()

    print(CMD)

    command_msg = msgConverter.get_command('SPLN', CMD)

    # print("COMMAND ", command_msg)
    serialCom.write(command_msg.encode('ascii'))
    logFile.write(command_msg)

SendCmd()

