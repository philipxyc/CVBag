import numpy as np
import cv2
import pyrealsense2 as rs
import time, math

# Configuration
depth_range = (0, 50000)
depth_thresh = 20000
area_thresh = 200

def findObstacle(depth):
    start = time.clock()
    
    ret, depth = cv2.threshold(depth, depth_range[0], 255, cv2.THRESH_TOZERO)
    ret, depth = cv2.threshold(depth, depth_range[1], 255, cv2.THRESH_TOZERO_INV)    
    depth = np.ubyte(depth)

    # Get a 15x15 kernel filled with 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    # Open operation, separate depth, suppress insignificant blocks
    opening = cv2.morphologyEx(depth, cv2.MORPH_OPEN, kernel)

    # Search contours
    ret, binary_depth = cv2.threshold(depth, depth_thresh, 255, cv2.THRESH_BINARY)
    ret, contours, hierarchy = cv2.findContours(binary_depth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find convex hull
    hulls = contoursOut = []
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) >= area_thresh: 
            hulls.append(cv2.convexHull(contours[i], False))
            contoursOut.append(contours[i])

    return (depth, binary_depth, hulls, contours, hierarchy)

def depthIntensity(depth):
    ret, depth = cv2.threshold(depth, depth_range[0], 255, cv2.THRESH_TOZERO)
    ret, depth = cv2.threshold(depth, depth_range[1], 255, cv2.THRESH_TOZERO_INV)
    depth(depth == 0.0) = float('inf')
    depth = 1.0 / depth
    numBlock = 5
    step = math.ceil(depth.shape[1] / numBlock)
    intensity = [0.0] * 5.0
    for i in range(numBlock):
        if i <= numBlock - 2:
            intensity.append(np.sum(depth[...,i*step:(i+1)*step]))
        else:
            intensity.append(np.sum(depth[...,i*step:]))
    return intensity

if __name__ == "__main__":
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
    # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    pc = rs.pointcloud()
            
    # Start streaming
    pipeline.start(config)

    try:
        colorizer = rs.colorizer()

        color_contours = (255, 255, 0)
        color_hull = (255, 255, 255)
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
            #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())

            # Convert to point cloud
            # points = pc.calculate(depth_frame)
            # analyzePointCloud(points, depth_frame)

            # Detection
            threshed, binary, hulls, contours, hierarchy = findObstacle(depth_image)
            for i in range(len(hulls)):
                # draw ith contour
                cv2.drawContours(depth_colormap, contours, i, color_contours, 1, 8)
                cv2.drawContours(depth_colormap, hulls, i, color_hull, 2, 8)

            intensity = depthIntensity(depth_image)
            print(intensity)

            # Show images
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', depth_colormap)
            cv2.imshow('Threshed', threshed)
            # cv2.imshow('Binary', binary)
            cv2.waitKey(1)

    finally:
        # Stop streaming
        pipeline.stop()
