import math
'''
methods for computing steering and speed
'''
MAX_SPEED = 0.28

class MoveLogic(object):

    def __init__(self):
        self.curr_steering_angle = 0
        self.current_speed = MAX_SPEED

    def getSpeed(self, steering):
        steering = abs(steering)

        if self.current_speed > MAX_SPEED:
            self.current_speed = MAX_SPEED
        else:
            if steering > 5:
                if self.current_speed < 0.2:
                    self.current_speed = self.current_speed + 0.01
                self.current_speed = self.current_speed - 0.01
            elif steering < 1:
                self.current_speed = self.current_speed + 0.01
        return self.current_speed

    def getSteer(self, frame, lane_lines):
        '''
        returns the steering angle
        '''
        if len(lane_lines) == 0:
            print("No lane lines..")
            return 0
        else:
            new_steering_angle = compute_steering_angle(frame, lane_lines)
            self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))
            return self.curr_steering_angle



def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        print('No lane lines detected, do nothing')
        return 0

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        print('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.01 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset) * 20  # angle (in radian) to center vertical line

    return angle_to_mid_radian

def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=2, max_angle_deviation_one_lane=1.5):
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
