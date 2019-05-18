import numpy as np
import cv2
import pyrealsense2 as rs
import time
 
def maskDepth(image, thresh = 1000):
	nr = image.shape[0] # number of rows
	nc = image.shape[1]	# number of columns
	cv2.threshold(depth, depth_thresh, 255, cv2.THRESH_BINARY)
	for i in range(nr):
		for j in range(nc):
			if image[i][j] >= thresh:
				image[i][j] = 0

def findObstacle(depth, mask_thresh = 1000, depth_thresh = 20, max_thresh = 255, area_thresh = 500):
	start = time.clock()	
	ret, depth = cv2.threshold(depth, mask_thresh, 255, cv2.THRESH_TOZERO)
	depth = np.ubyte(depth * (1.0/16.0))
	# print("Mask:", time.clock() - start)
	# start = time.clock()
	# cv2.imshow("Preprocessed Depth", depth)

	# Get a 15x15 kernel filled with 1
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
	# Open operation, separate depth, suppress insignificant blocks
	opening = cv2.morphologyEx(depth, cv2.MORPH_OPEN, kernel)
	# cv2.imshow("Morphology", opening)
	# print("Morphology:", time.clock() - start)
	# start = time.clock()

	# Search contours
	ret, binary_depth = cv2.threshold(depth, depth_thresh, 255, cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(binary_depth, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# print("Contours:", time.clock() - start)
	# start = time.clock()

	# Find convex hull
	hulls = contoursOut = []
	for i in range(len(contours)):
		if cv2.contourArea(contours[i]) >= area_thresh: 
			hulls.append(cv2.convexHull(contours[i], False))
			contoursOut.append(contours[i])
	# print("Filter:", time.clock() - start)

	return (hulls, contours, hierarchy)

	# results = []
	# # create an empty black image
	# drawing = np.zeros((binary_depth.shape[0], binary_depth.shape[1], 3), np.uint8)
	# for i in range(len(hulls)):
	# 	if cv2.contourArea(contours[i]) >= area_thresh:
	# 		results.append(hulls[i])
	# 		color_contours = (0, 255, 0)
	# 		color_hull = (0, 0, 255)
	# 	else:
	# 		color_contours = (0, 128, 0)
	# 		color_hull = (0, 0, 128)
	# 	# draw ith contour
 #    	cv2.drawContours(drawing, contours, i, color_contours, 1, 8, hierarchy)
 #    	cv2.drawContours(drawing, hulls, i, color_hull, 1, 8)
 #    cv2.imshow("Contours and Hulls", drawing)
 #    return results

if __name__ == "__main__":
	# Configure depth and color streams
	pipeline = rs.pipeline()
	config = rs.config()
	config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
	config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

	# Start streaming
	pipeline.start(config)

	try:
		color_contours = (0, 255, 0)
		color_hull = (0, 0, 255)
		while True:

			# Wait for a coherent pair of frames: depth and color
			frames = pipeline.wait_for_frames()
			depth_frame = frames.get_depth_frame()
			color_frame = frames.get_color_frame()
			if not depth_frame or not color_frame:
				continue

			# Convert images to numpy arrays
			depth_image = np.asanyarray(depth_frame.get_data())
			color_image = np.asanyarray(color_frame.get_data())

			# Apply colormap on depth image (image must be converted to 8-bit per pixel first)
			depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
			# Detection
			hulls, contours, hierarchy = findObstacle(depth_image)
			for i in range(len(hulls)):
			 	# draw ith contour
				cv2.drawContours(depth_colormap, contours, i, color_contours, 1, 8, hierarchy)
				cv2.drawContours(depth_colormap, hulls, i, color_hull, 1, 8)
			# Stack both images horizontally
			images = np.hstack((color_image, depth_colormap))

			# Show images
			cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
			cv2.imshow('RealSense', images)
			cv2.waitKey(1)

	finally:

		# Stop streaming
		pipeline.stop()

	# # Configure depth and color streams
	# pipeline = rs.pipeline()
	# config = rs.config()
	# config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
	# config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
	# # Start streaming
	# pipeline.start(config)


	# color_contours = (0, 255, 0)
	# color_hull = (0, 0, 255)
	# try:
	# 	while True:
	# 		# Wait for a coherent pair of frames: depth and color
	# 		frames = pipeline.wait_for_frames()
	# 		depth_frame = frames.get_depth_frame()
	# 		color_frame = frames.get_color_frame()
	# 		if not depth_frame or not color_frame:
	# 			continue
	# 		depth_image = np.asanyarray(depth_frame.get_data())
	# 		rgb_image = np.asanyarray(color_frame.get_data())

	# 		depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
	# 		# print(depth_colormap)
	# 		cv2.imshow('Webcam', depth_colormap)

	# 		# Detection
	# 		# hulls, contours, hierarchy = findObstacle(depth_image)
	# 		# for i in range(len(hulls)):
	# 		# 	# draw ith contour
	# 		# 	cv2.drawContours(depth_image, contours, i, color_contours, 1, 8, hierarchy)
	# 		# 	cv2.drawContours(depth_image, hulls, i, color_hull, 1, 8)
			
	# 		# time.sleep(10)

	# 		# key = cv2.waitKey(1)
	# 		# Press esc or 'q' to close the image window
	# 		# if key & 0xFF == ord('q') or key == 27:
	# 		# 	cv2.destroyAllWindows()
	# 		# 	break
	# 		# break
	# finally:
	# 	# Stop streaming
	# 	pipeline.stop()
