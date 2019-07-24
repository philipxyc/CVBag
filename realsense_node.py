import numpy as np
import cv2
import pyrealsense2 as rs
import multiprocessing, queue
import math, time
from pyfirmata import Arduino


##################################################################
# DNN Parameters
##################################################################
inWidth      = 300
inHeight     = 300
WHRatio       = inWidth /float(inHeight)
inScaleFactor = 0.007843
meanVal       = 127.5
classNames  = ["background",
                "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair",
                "cow", "diningtable", "dog", "horse",
                "motorbike", "person", "pottedplant",
                "sheep", "sofa", "train", "monitor"]

net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")

def objectDetect(color_mat, depth_mat, crop):

    input_blob = cv2.dnn.blobFromImage(color_mat, inScaleFactor, (inWidth, inHeight), meanVal, False)
    
    net.setInput(input_blob, "data")

    # detection = net.forward("fc")
    detection = net.forward("detection_out")

    # How to initialize
    detectionMat = np.reshape(detection,(detection.shape[2],detection.shape[3]))
    # detectionMat = np.zeros(detection.shape[2],detection.shape[3],cv2.CV_32F,detection)

    # Crop a mat with rectangle
    color_mat = color_mat[crop[0][1]:crop[0][1]+crop[1][1], crop[0][0]:crop[0][0]+crop[1][0]]
    depth_mat = depth_mat[crop[0][1]:crop[0][1]+crop[1][1], crop[0][0]:crop[0][0]+crop[1][0]]

    # Tweak confident threshold here!!!
    confidenceThreshold = 0.8

    results = []
    for i in range(0, detectionMat.shape[0]):
        confidence = detectionMat[i][2]
        if confidence > confidenceThreshold:
            objectClass = detectionMat[i][1]

            xLeftBottom = int(detectionMat[i][3] * color_mat.shape[1])
            yLeftBottom = int(detectionMat[i][4] * color_mat.shape[0])
            xRightTop = int(detectionMat[i][5] * color_mat.shape[1])
            yRightTop = int(detectionMat[i][6] * color_mat.shape[0])

            # Rectangle Constrain
            if xLeftBottom < 0: xLeftBottom = 0
            if yLeftBottom > depth_mat.shape[0]: yLeftBottom = depth_mat.shape[0]
            if xRightTop > depth_mat.shape[1]: xRightTop = depth_mat.shape[1]
            if yRightTop < 0: yRightTop = 0
            
            classIdx = int(objectClass)
            print("Recog Index:", classIdx)

            className = classNames[int(objectClass)]
            # bounding box
            rect = (xLeftBottom, yLeftBottom, xRightTop, yRightTop)
            # calculate average distance
            m = cv2.mean(depth_mat[yLeftBottom:yRightTop][xLeftBottom:xRightTop])

            results.append({"classid": int(objectClass)
                , "classname": className
                , "rect": rect
                , "confidence": confidence
                , "distance": m[0]
            })
    return results

##################################################################
# Obstacle Estimation Parameters
##################################################################
depth_range = (0, 2000)

def obstacleEstimate(depth):
    depth = np.float32(depth)
    ret, depth = cv2.threshold(depth, depth_range[0], 255, cv2.THRESH_TOZERO)
    ret, depth = cv2.threshold(depth, depth_range[1], 255, cv2.THRESH_TOZERO_INV)
    depth[depth == 0.0] = float('inf')
    depth = 1.0 / depth
    numBlock = 5
    step = math.ceil(depth.shape[1] / numBlock)
    intensity = [] 
    for i in range(numBlock):
        if i <= numBlock - 2:
            intensity.append(np.sum(depth[...,i*step:(i+1)*step]))
        else:
            intensity.append(np.sum(depth[...,i*step:]))
    return intensity

def edgeDetection(depth):
    ret, depth = cv2.threshold(depth, depth_range[0], 255, cv2.THRESH_TOZERO)
    ret, depth = cv2.threshold(depth, depth_range[1], 255, cv2.THRESH_TOZERO_INV)    
    depth = np.ubyte(depth)

    # Get a 15x15 kernel filled with 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    # Open operation, separate depth, suppress insignificant blocks
    opening = cv2.morphologyEx(depth, cv2.MORPH_OPEN, kernel)

    # Search contours
    ret, binary_depth = cv2.threshold(depth, depth_thresh, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary_depth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find convex hull
    hulls = contoursOut = []
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) >= area_thresh: 
            hulls.append(cv2.convexHull(contours[i], False))
            contoursOut.append(contours[i])

    return (hulls, contours, hierarchy)

##################################################################
# Main Loop Parameters
##################################################################
depthmap_visualization = True
colormap_visualization = False
objdetect_visualization = True
depthintensity_verbose = False
objdetection_verbose = True

def start_node(task_queue, result_queue):

    ##################################################################
    # Vibration Control Util
    ##################################################################

    '''
    try:
        board = Arduino('COM5')
    except:
        board = Arduino('COM3')

    pins = [board.get_pin('d:10:p'), board.get_pin('d:9:p'), board.get_pin('d:6:p'), board.get_pin('d:5:p'), board.get_pin('d:3:p')]

    def set_vib(l:list):
        val, idx = min((val, idx) for (idx, val) in enumerate(l))
        pins[idx].write(max(1 - l[idx]/60, 0))
        for i in range(len(l)):
            if i != idx:
                pins[i].write(0)
    '''

    ##################################################################
    # Vision Setup
    ##################################################################
    
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

    pipeline.start(config)
    print("Start camera pipelining ...")

    align_to = rs.align(rs.stream.color)

    profile_data = pipeline.wait_for_frames().get_color_frame()

    # Calculate crop Size
    cropSize = (0,0)
    if profile_data.width / float(profile_data.height) > WHRatio:
        cropSize = (int(profile_data.height * WHRatio), profile_data.height)
    else:   
        cropSize = (profile_data.width, int(profile_data.width / WHRatio))
    crop = [(int((profile_data.width - cropSize[1]) / 2), int((profile_data.height - cropSize[0]) / 2 )), cropSize]

    last_frame_number = 0

    colorizer = rs.colorizer()

    decimation = rs.decimation_filter()
    threshold = rs.threshold_filter()
    spatial = rs.spatial_filter()

    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)

    try:
        while(True):
            frame = pipeline.wait_for_frames()

            frame = align_to.process(frame)

            color_frame = frame.get_color_frame()
            depth_frame = frame.get_depth_frame()

            depth_frame = decimation.process(depth_frame)
            depth_frame = threshold.process(depth_frame)
            depth_frame = depth_to_disparity.process(depth_frame)
            depth_frame = spatial.process(depth_frame)
            depth_frame = disparity_to_depth.process(depth_frame)

            color_mat = np.asanyarray(color_frame.get_data())
            depth_mat = np.asanyarray(depth_frame.get_data())

            if depthmap_visualization:
                depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())
                cv2.imshow("Depth Map", depth_colormap)
            if colormap_visualization:
                cv2.imshow("Color Map", color_mat)

            intensity = obstacleEstimate(depth_mat)
            if depthintensity_verbose:
                print("Intensity:", intensity)

            #set_vib(intensity)

            task = None
            objDetectEnabled = False
            try:
                task = task_queue.get_nowait()
                if task is None:
                    break
                else:
                    objDetectEnabled = True
            except queue.Empty:
                pass

            # Detection by keyboard for testing
            key = cv2.waitKey(1)
            if key == 32: objDetectEnabled = True

            if objDetectEnabled:
                if color_frame.get_frame_number() != last_frame_number:
                    last_frame_number = color_frame.get_frame_number()

                    # Record start time
                    if objdetection_verbose:
                        start_time = time.clock()

                    objects = objectDetect(color_mat, depth_mat, crop)

                    # Send result to the message queue
                    if task is not None:
                        res = list(task)
                        res.append(objects)
                        result_queue.put(tuple(res))

                    for obj in objects:
                        className, confidence, rect, m = obj["classname"], obj["confidence"], obj["rect"], obj["distance"]
                        conf = "%s(%f), %fm" % (className, confidence, m/1000)

                        if objdetection_verbose:
                            print("Detected: %s" % conf)

                        if objdetect_visualization:
                            cv2.rectangle(color_mat, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0))
                            cv2.putText(color_mat, conf, (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))
                    if objdetection_verbose:
                        print("Detection time: %fs" % (time.clock() - start_time))

                    if objdetect_visualization:
                        cv2.imshow("Object Detection", color_mat)
                
    except KeyboardInterrupt:
        print("Shutdown realsense worker ...")
    finally:
        # Stop streaming
        pipeline.stop()
        #set_vib([60,60,60,60,60])
