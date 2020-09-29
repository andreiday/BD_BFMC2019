import cv2
import numpy as np
import math
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

sys.path.append('.')

dir = os.path.join("src", "utils", "models")

signsModelPath = os.path.join(dir, "signs",  "ssdlite_mobilenet_v2_coco.pb")
signGraphPath = os.path.join(dir, "signs", "graph.pbtxt")
lanesModelPath = os.path.join(dir, "lanes",  "keras_model.h5")

# enable keras lane follower model
MLFollower = False

# enable intel neural computing stick communication
NCSigns = False

class DetectionProcessing():
    def __init__(self):
        # init signs
        logger.info('Init detection processing...')

        self.net = cv2.dnn.readNetFromTensorflow(signsModelPath, signGraphPath)

        if NCSigns:
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

        self.enableDrawSigns = True

        # init LaMe follower
        if MLFollower:
            from keras.models import load_model
            self.lanesModel = load_model(lanesModelPath)
        
    def followLanesNvidia(self, frame):
        showVideo("orig", frame)

        steering_angle = self.compute_steering_angle(frame)
        logger.debug("steering_angle = %d" % steering_angle)
        final_frame = display_heading_line(frame, steering_angle)
        showVideo("heading", final_frame)
        return steering_angle

    def compute_steering_angle(self, frame):
        """ Find the steering angle directly based on video frame
            We assume that camera is calibrated to point to dead center
        """
        preprocessed = img_preprocess(frame)
        X = np.asarray([preprocessed])
        steering_angle = self.lanesModel.predict(X)[0]

        logger.debug('new steering angle: %s' % steering_angle)
        return int(steering_angle + 0.5) # round the nearest integer

    def followLanesCV(self, frame):
        
        edges = detectEdges(frame)

        cropped_edges = regionOfInterestLanes(edges)
        showVideo("crpedges", cropped_edges)

        line_segments = detectLineSegments(cropped_edges)

        lane_lines_images = displayLines(frame, line_segments)
        showVideo("lanelines", lane_lines_images)

        lane_lines = averageSlopeIntercept(frame, line_segments)

        return lane_lines

    def detectIntersection(self, frame):
        frame = cv2.medianBlur(frame, 9)
        edge = detectEdges(frame)

        framecut = regionOfInterestIntersection(edge)

        line_segments = []
        line_segments = detectLineSegmentsIntersection(framecut)

        if line_segments is None:
            return "N"
        else:
            for line_segment in line_segments:
                for _, y1, _, y2 in line_segment:
                    if y1 == y2 or abs(y1-y2) < 5:
                        return "Y"
                    else:
                        return "N"

    def detectSigns(self, frame):
        self.CLASSES = ["park", "pedestrians", "priority", "stop"]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))

        sign = cv2.resize(frame, (300, 300))
        (h, w) = sign.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(sign, (300, 300)), swapRB=True)
        showVideo("signs", frame)

        # grab the frame dimensions and convert it to a blob
        # pass the blob through the network and obtain the detections and
        # predictions

        self.net.setInput(blob)
        detections = self.net.forward()
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):

            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > 0.6:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])

                if self.enableDrawSigns:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(self.CLASSES[idx-1], confidence * 100)

                if self.enableDrawSigns:
                    cv2.rectangle(sign, (startX, startY), (endX, endY), self.COLORS[idx-1], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(sign, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx-1], 2)

                    cv2.namedWindow('sign', cv2.WINDOW_NORMAL)
                    cv2.imshow('sign', sign)
                    cv2.waitKey(1)

                label = "{}".format(self.CLASSES[idx-1])
                logger.debug("label: ", label)
                return label


# ====================== Image Processing functions =====================

def img_preprocess(image):
    height, _, _ = image.shape
    image = image[int(height/2):,:,:]  # remove top half of the image, as it is not relevant for lane following
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)  # Nvidia model said it is best to use YUV color space
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
    image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
    return image

def detectEdges(frame, hue=(27, 160), lum=(80, 255), sat=(0, 255)):
    '''
    '''
    frame = cv2.medianBlur(frame, 3)

    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    lower_white = np.array([hue[0], lum[0], sat[0]], dtype=np.uint8)
    upper_white = np.array([hue[1], lum[1], sat[1]], dtype=np.uint8)
    mask = cv2.inRange(hls, lower_white, upper_white)
    edges = cv2.Canny(mask, 200, 400)

    return edges

'''
# Nvidia model said it is best to use YUV color space
def detectEdgesNvidia(frame, hue=(27, 160), lum=(80, 255), sat=(0, 255)):
    frame = cv2.medianBlur(frame, 3)

    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    lower_white = np.array([hue[0], lum[0], sat[0]], dtype=np.uint8)
    upper_white = np.array([hue[1], lum[1], sat[1]], dtype=np.uint8)
    mask = cv2.inRange(hls, lower_white, upper_white)
    edges = cv2.Canny(mask, 200, 400)

    return edges
'''

def regionOfInterestLanes(edges):
    '''
    '''
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # cut a bit from the bottom
    # polygon = np.array([[
    #     (0, (height * 1 / 2)),
    #     (width, (height * 1 / 2)),
    #     (width, height * 1/1.05),
    #     (0, height * 1/1.05),
    # ]], np.int32)

    polygon = np.array([[
        (0, (height * 1 / 2)),
        (width, (height * 1 / 2)),
        (width, height),
        (0, height),
    ]], np.int32)

    # only car front triangle
    polygon_front = np.array([[
        ((width * 1 / 1.4), height * 1/2),
        ((width * 1 / 3), height * 1/2),
        (width * 1/3.1, height),
        (width * 1/1.3, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)

    # remove front
    cv2.fillPoly(mask, polygon_front, 0)

    cropped_edges = cv2.bitwise_and(edges, mask)

    return cropped_edges


def detectLineSegments(cropped_edges):
    '''
    '''

    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 50
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
    np.array([]), minLineLength=4, maxLineGap=32)

    return line_segments


def averageSlopeIntercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """

    '''
    numpy warning:
    Mean of empty slice.
    avg = a.mean(axis)

    cause for numpy warning:

    when segments for only a single lane line are created
    numpy.average trips
    '''

    lane_lines = []
    if line_segments is None:
        logger.debug('No line_segment segments detected')
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
                logger.debug('skipping vertical line segment (slope=inf): %s' % line_segment)
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

    return lane_lines


def displayLines(frame, lines, line_color=(0, 0, 255), line_width=15):

    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5):

    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image


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

# ================================ PROCESSING FUNCTIONS FOR INTERSECTION DETECTION ============================================


def detectLineSegmentsIntersection(cropped_edges):
    '''
    '''

    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 50
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
    np.array([]), minLineLength=8, maxLineGap=16)

    return line_segments


def regionOfInterestIntersection(frame):
    '''
    '''
    height, width = frame.shape
    mask = np.zeros_like(frame)

    polygon = np.array([[
        ((width * 1 / 1.4), height * 1/1.5),
        ((width * 1 / 3) , height * 1/1.5),
        (width * 1/3.1, height * 1/1.1),
        (width * 1/1.3, height* 1/1.1),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_frame = cv2.bitwise_and(frame, mask)

    return cropped_frame
# ===============others=================


def showVideo(title, frame):
    '''
    show frame buffer in a window
    '''
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, frame)
    cv2.waitKey(1)
