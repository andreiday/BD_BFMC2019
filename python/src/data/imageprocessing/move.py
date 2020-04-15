import math
'''
class for computing steering and speed
'''

MAX_SPEED = 0.25

class MoveLogic(object):

    def __init__(self):

        self.curr_steering_angle = 0.0
        self.current_speed = 0.0

    def getSpeed(self, lane_lines, steering):

        steering = abs(steering)

        if len(lane_lines) == 2:
            self.current_speed = MAX_SPEED
            # if steering > 5:
            #     self.current_speed = MAX_SPEED
            if steering > 10:
                self.current_speed = MAX_SPEED - 0.02

        if len(lane_lines) == 1:
            self.current_speed = MAX_SPEED
            # if steering > 5:
            #     self.current_speed = MAX_SPEED
            if steering > 10:
                self.current_speed = MAX_SPEED - 0.02

        if len(lane_lines) == 0:
            self.current_speed = MAX_SPEED - 0.02

        return self.current_speed


    def getSteer(self, frame, lane_lines):
        '''
        returns the steering angle
        '''

        if len(lane_lines) == 0:
            # print("No lane lines.")
            return self.curr_steering_angle

        else:
            new_steering_angle = compute_steering_angle(frame, lane_lines)

            self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))

            return self.curr_steering_angle


def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    displayHeadlingLine = False

    if len(lane_lines) == 0:
        # print('No lane lines detected.')
        return lane_lines

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        # print('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1

    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.07 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    if displayHeadlingLine:
        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel
        return steering_angle
    else:
        angle_to_mid_radian = math.atan(x_offset / y_offset) # angle (in radian) to center vertical line
        steering_angle = angle_to_mid_radian * 15
        return steering_angle

def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=1.5, max_angle_deviation_one_lane=2.5):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """

    if num_of_lane_lines == 2:
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else:
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane

    angle_deviation = new_steering_angle - curr_steering_angle

    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle

    return stabilized_steering_angle
