import io
import cv2
import numpy as np
import math
import time
import datetime
import sys
import os
from scipy.stats import itemfreq

class FrameProcessing(object):

    #================================ PROCESSING STEPS ============================================

    def detectLanes(self, frame):
        edges = detectEdges(frame)

        cropped_edges = regionOfInterestLanes(edges)
        line_segments = detectLineSegments(cropped_edges)

        showVideo("crpedges", cropped_edges)

        lane_lines = averageSlopeIntercept(frame, line_segments)


        return lane_lines

    def detectSigns(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(gray, 29)
        img = regionOfInterestSigns(img)

        # detect circles
        #   parameters:
        #   8-bit single channel image, method:Hough, dp - 1:the larger it gets the smaller the accumulator array gets (poor image quality)
        #   minDist - 50: if it too small, multiple circles in the same neighbourhood as the original may be falsly detected, but if is too large then sone circkes may not be detected at all.
        #   param 1: gradient value used to handle edge detection
        #   param 2: threshold accumulator (larger - more circles detected includibg false ones)

        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 70, param1=120, param2=30)
        # output: circles encoded as vectors -> (x, y, radius)
        # at least some circles are found

        if not circles is None:
            circles = np.uint16(np.around(circles))
            max_r, max_i = 0, 0
            for i in range(len(circles[:, :, 2][0])):
                if circles[:, :, 2][0][i] > 50 and circles[:, :, 2][0][i] > max_r:
                    max_i = i
                    max_r = circles[:, :, 2][0][i]
            x, y, r = circles[:, :, :][0][max_i]

            if y > r and x > r:
                square = frame[y-r:y+r, x-r:x+r]

                dominant_color = get_dominant_color(square, 2)
                if dominant_color[2] > 100:
                    return "STOP"
                elif dominant_color[0] > 80:
                    zone_0 = square[square.shape[0]*3//8:square.shape[0]
                                    * 5//8, square.shape[1]*1//8:square.shape[1]*3//8]
                    #cv2.imshow('Zone0', zone_0)

                    zone_0_color = get_dominant_color(zone_0, 1)

                    zone_1 = square[square.shape[0]*1//8:square.shape[0]
                                    * 3//8, square.shape[1]*3//8:square.shape[1]*5//8]
                    #cv2.imshow('Zone1', zone_1)
                    zone_1_color = get_dominant_color(zone_1, 1)

                    zone_2 = square[square.shape[0]*3//8:square.shape[0]
                                    * 5//8, square.shape[1]*5//8:square.shape[1]*7//8]
                    #cv2.imshow('Zone2', zone_2)
                    zone_2_color = get_dominant_color(zone_2, 1)

                    if zone_1_color[2] < 60:
                        if sum(zone_0_color) > sum(zone_2_color):
                            return "PARK"
                        else:
                            return "PARK"
                    else:
                        if sum(zone_1_color) > sum(zone_0_color) and sum(zone_1_color) > sum(zone_2_color):
                            return "PARK"
                        elif sum(zone_0_color) > sum(zone_2_color):
                            return "PARK"
                        else:
                            return "PARK"
                else:
                    return "N/A"

            for i in circles[0, :]:
                cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
        showVideo("sign", img)

#================================ PROCESSING FUNCTIONS FOR LANES ============================================

def detectEdges(frame,hue=(40, 140), lum=(177, 255), sat=(0, 111)):
    '''
    '''
    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    lower_white = np.array([hue[0],lum[0],sat[0]], dtype=np.uint8)
    upper_white = np.array([hue[1],lum[1],sat[1]], dtype=np.uint8)
    mask = cv2.inRange(hls, lower_white, upper_white)
    edges = cv2.Canny(mask, 200, 400)

    return edges

def regionOfInterestLanes(edges):
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



def displayLines(frame, lines, line_color=(0, 0, 255), line_width=25):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


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

#================================ PROCESSING FUNCTIONS FOR SIGNS ============================================


def get_dominant_color(image, n_colors):
    pixels = np.float32(image).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
#cv2.TERM_CRITERIA_EPS stops the algorithm iterations is sfecified accuracy (epsilon 0.1) is reached
#cv2.TERM_CRITERIA_MAX_ITER stops the algorithm after the specified number of iterations

    flags = cv2.KMEANS_RANDOM_CENTERS
#the flag is used to specify how initial centers are taken

    flags, labels, centroids = cv2.kmeans(
        pixels, n_colors, None, criteria, 10, flags)
    palette = np.uint8(centroids)

# pixels = data type in a single column
# n_colors = number of colors required
# NONE = attempts the algorithm is executed using different labels
# criteria = stops when no of iter or the accuracy is reached
# flags = tells how initial centers are taken

    return palette[np.argmax(itemfreq(labels)[:, -1])]
# returns the dominant color by computing the max of the color array


def regionOfInterestSigns(frame):
    '''
    '''
    height, width = frame.shape
    mask = np.zeros_like(frame)

    polygon = np.array([[
        (width * 1/3, 0),
        (width, 0),
        (width, (height * 1/2)),
        (width * 1/3, (height * 1/2)),
    ]], np.int64)

    cv2.fillPoly(mask, polygon, 255)
    cropped_frame = cv2.bitwise_and(frame, mask)

    return cropped_frame




def showVideo(title, frame):
    '''
    show frame buffer in a window
    '''
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, frame)
    cv2.waitKey(1)
