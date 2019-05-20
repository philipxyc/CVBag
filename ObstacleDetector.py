import numpy as np
import cv2
import pyrealsense2 as rs
import time

def findObstacle(depth, mask_thresh = 1000, depth_thresh = 20, max_thresh = 255, area_thresh = 500):
    start = time.clock()    
    # ret, depth = cv2.threshold(depth, mask_thresh, 255, cv2.THRESH_TOZERO)
    depth = np.ubyte(depth * (1.0/16.0))

    yield depth
    # print("Mask:", time.clock() - start)
    # start = time.clock()
    # cv2.imshow("Preprocessed Depth", depth)

    # Get a 15x15 kernel filled with 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    # Open operation, separate depth, suppress insignificant blocks
    opening = cv2.morphologyEx(depth, cv2.MORPH_OPEN, kernel)

    # Search contours
    ret, binary_depth = cv2.threshold(depth, depth_thresh, 255, cv2.THRESH_BINARY)
    ret, contours, hierarchy = cv2.findContours(binary_depth, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    yield binary_depth

    # Find convex hull
    hulls = contoursOut = []
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) >= area_thresh: 
            hulls.append(cv2.convexHull(contours[i], False))
            contoursOut.append(contours[i])

    yield (hulls, contours, hierarchy)

if __name__ == "__main__":
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
    # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    try:
        colorizer = rs.colorizer()

        color_contours = (0, 255, 0)
        color_hull = (0, 0, 255)
        while True:

            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            # color_frame = frames.get_color_frame()
            # if not depth_frame or not color_frame:
            if not depth_frame:
                continue

            decimation = rs.decimation_filter()
            threshold = rs.threshold_filter()
            spatial = rs.spatial_filter()

            depth_to_disparity = rs.disparity_transform(True)
            disparity_to_depth = rs.disparity_transform(False)

            depth_frame = decimation.process(depth_frame)
            depth_frame = threshold.process(depth_frame)
            depth_frame = depth_to_disparity.process(depth_frame)
            depth_frame = spatial.process(depth_frame)
            depth_frame = disparity_to_depth.process(depth_frame)

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            # color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            # Detection
            finder = findObstacle(depth_image)
            filtered = next(finder)
            filtered = np.asanyarray(colorizer.colorize(filtered).get_data())
            binary = next(finder)
            hulls, contours, hierarchy = next(finder)
            for i in range(len(hulls)):
                # draw ith contour
                cv2.drawContours(depth_colormap, contours, i, color_contours, 1, 8, hierarchy)
                cv2.drawContours(depth_colormap, hulls, i, color_hull, 1, 8)

            # Stack both images horizontally
            images = np.hstack((filterd, binary, depth_colormap))

            # Show images
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', filtered)
            cv2.imshow('RealSense', binary)
            cv2.imshow('RealSense', images)
            cv2.waitKey(1)

    finally:
        # Stop streaming
        pipeline.stop()
