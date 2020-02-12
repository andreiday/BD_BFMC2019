import io
import cv2
import numpy as np
import math
import time
import datetime
import sys
import os


class SteeringFrameProcessing(object):
    def __init__(self):
        self.curr_steering_angle = 0

    def followLaneFrame(self,frame):
        lane_lines = detectLanes(frame)

        steering_angle = self.steer(frame, lane_lines)

        return steering_angle

    def steer(self, frame, lane_lines):
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

#================================ PROCESSING STEPS ============================================

def detectLanes(frame):

    edges = detectEdges(frame)

    cropped_edges = regionOfInterest(edges)

    line_segments = detectLineSegments(cropped_edges)

    lane_lines = averageSlopeIntercept(frame, line_segments)



    return lane_lines


#================================ PROCESSING FUNCTIONS ============================================

def detectEdges(frame,hue=(40, 140), lum=(177, 255), sat=(0, 111)):
    '''
    '''
    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    lower_white = np.array([hue[0],lum[0],sat[0]], dtype=np.uint8)
    upper_white = np.array([hue[1],lum[1],sat[1]], dtype=np.uint8)
    mask = cv2.inRange(hls, lower_white, upper_white)
    edges = cv2.Canny(mask, 200, 400)

    return edges

def regionOfInterest(edges):
    '''
    '''
    height, width = edges.shape
    mask = np.zeros_like(edges)

    polygon = np.array([[
        (0, (height * 1 / 2)),
        (width, (height * 1 / 2)),
        (width, height),
        (0, height ),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)

    return cropped_edges

def detectLineSegments(cropped_edges):
    '''
    '''
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 50  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
    np.array([]), minLineLength=8, maxLineGap=4)

    return line_segments

def averageSlopeIntercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        print('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                print('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    #logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines

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
    #print('steering angle: %s' %  stabilized_steering_angle)

    return stabilized_steering_angle

'''
def displayLines(frame, lines, line_color=(0, 0, 255), line_width=25):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image
'''

def make_points(frame, line):
    '''
    make_points is a helper function for the average_slope_intercept function, which takes a line’s slope and intercept, and returns the endpoints of the line segment.
    '''
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def showVideo(title, frame):
    '''
    show frame buffer in a window
    '''
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, frame)
