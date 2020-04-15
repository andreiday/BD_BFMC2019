import os
import time
from random import randint
from src.data.imageprocessing.move import stabilize_steering_angle

class DecisionHandler:
    def __init__(self):
        self.lane_lines = []
        self.detected_sign = "None"
        self.intersection_line = "N"
        self.steering_angle = 0.0
        self.speed = 0.0
        self.currentState = [False,False,False,False,False,False]
        # current state = stateLabels positions except parking
        self.stateLabels = ["Keeping lane", "Intersecion detected, keeping steering", "Intersection detected, steering left", "Intersection detected, steering right", "Stopping at sign", "Pedestrian sign, slowing down", "Parking?", "init"]
        self.currentStateLabel = self.stateLabels[0]
        self.doneStop = False
        self.donePeds = False
        self.lastStateLabel = self.stateLabels[7]
        self.canChangeState = True
        self.stateTime = 0
        self.timeLeft = 0
        self.timeDisplay = 0

    def setData(self, data):

        self.lane_lines = data[0]
        self.detected_sign = data[1]
        self.intersection_line = data[2]

        if self.currentState[1] or self.currentState[4]:
            self.steering_angle = 0.0
        elif self.currentState[2]: #left
            new_steering_angle = self.steering_angle - 0.3
            self.steering_angle = stabilize_steering_angle(self.steering_angle,new_steering_angle,len(self.lane_lines))
            self.steering_angle = round(self.steering_angle, 3)
        elif self.currentState[3]: #right
            new_steering_angle = self.steering_angle + 0.5
            self.steering_angle = stabilize_steering_angle(self.steering_angle,new_steering_angle,len(self.lane_lines))
            self.steering_angle = round(self.steering_angle, 3)
        else:
            self.steering_angle = data[3]

        if self.currentState[5]:
            self.speed = data[4] - 0.07
        elif self.currentState[4]:
            self.speed = 0.0
        else:
            self.speed = data[4]

        # frame = data[5]
        # steering_frame = display_heading_line(frame,self.steering_angle)
        # showVideo("steeringframe", steering_frame)


    def displayInfo(self):
        """Display all parameters on the screen.
        """
        # clear stdout for a smoother display
        # os.system('cls' if os.name=='nt' else 'clear')

        print("=========== Status ============")
        print(
            "speed:                         " + str(self.speed) +
            "\nangle:                       " + str(self.steering_angle) +
            "\nsign:                        " + str(self.detected_sign) +
            "\nlane lines:                  " + str(self.lane_lines) +
            "\nintersection line flag:      " + str(self.intersection_line) +
            "\ncurrent state label:         " + str(self.currentStateLabel) +
            "\ncurrent states:              " + str(self.currentState)
        )

    def _stateDict(self):
        """It generates a dictionary with the robot current states.
         Returns
         -------
         dict
             It contains the robot current control state, speed and angle.
        """

        data = {}
        # if self.currentState[4]:
        #     data['action']        =  'BRAK'
        # else:
        data['action']        =  'MCTL'
        data['speed']         =  float(self.speed)
        data['steerAngle']    =  float(self.steering_angle)

        return data

    def doState(self,data):


        self._updateMotionState()
        #self._updateParameters(data)
        self.setData(data)

        if time.time() - self.timeDisplay > 0.25:
            self.displayInfo()
            self.timeDisplay = time.time()

        return self._stateDict()

    def _updateMotionState(self):
        updateTime = time.time()

        if(updateTime - self.stateTime > self.timeLeft) and self.canChangeState == False:

            self.currentState[0] = True
            self.currentState[1] = False
            self.currentState[2] = False
            self.currentState[3] = False
            self.currentState[4] = False
            self.currentState[5] = False
            self.intersection_line = "N"
            self.canChangeState = True


        if (self.detected_sign == "None" and self.intersection_line == "N") and self.canChangeState == True:

            self.currentState[0] = True

            self.currentState[1] = False
            self.currentState[2] = False
            self.currentState[3] = False
            self.currentState[4] = False
            self.currentState[5] = False
            self.currentStateLabel = self.stateLabels[0]


        elif self.detected_sign == "priority" and self.intersection_line == ("N" or "Y") and self.canChangeState == True:
            self.stateTime = time.time()
            self.canChangeState = False

            self.timeLeft = 5

            self.currentState[1] = True

            self.currentState[0] = False
            self.currentState[2] = False
            self.currentState[3] = False
            self.currentState[4] = False
            self.currentState[5] = False
            self.currentStateLabel = self.stateLabels[1]



        elif self.detected_sign == "park" and self.canChangeState == True:
            self.currentStateLabel = self.stateLabels[6]

        elif self.detected_sign == "pedestrians" and self.donePeds == False and self.canChangeState == True:
            self.stateTime = time.time()
            self.canChangeState = False

            self.timeLeft = 5

            self.currentState[5] = True

            self.currentState[0] = False
            self.currentState[1] = False
            self.currentState[2] = False
            self.currentState[3] = False
            self.currentState[4] = False
            self.donePeds = True
            self.currentStateLabel = self.stateLabels[5]


        elif self.detected_sign == "stop" and self.doneStop == False and self.canChangeState == True:
            self.stateTime = time.time()
            self.canChangeState = False

            self.timeLeft = 5

            self.currentState[4] = True


            self.currentState[0] = False
            self.currentState[1] = False
            self.currentState[2] = False
            self.currentState[3] = False

            self.currentState[5] = False
            self.doneStop = True
            self.currentStateLabel = self.stateLabels[4]


        elif self.detected_sign == "None" and self.intersection_line == "Y" and self.canChangeState == True:

            self.stateTime = time.time()
            self.canChangeState = False
            self.timeLeft = 6

            idk = randint(2, 3)

            if idk == 2 or self.steering_angle < 0:
                self.currentState[2] = True
                self.currentStateLabel = self.stateLabels[2]
                self.currentState[1] = False
                self.currentState[3] = False
            elif idk == 3:
                self.currentStateLabel = self.stateLabels[3]
                self.currentState[3] = True
                self.currentState[1] = False
                self.currentState[2] = False

            self.currentState[0] = False
            self.currentState[1] = False
            self.currentState[4] = False
            self.currentState[5] = False

        #    self.currentStateLabel = self.stateLabels[idk]
