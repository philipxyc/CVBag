import numpy as np
import pyrealsense2 as rs
import cv2




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
                "sheep", "sofa", "train", "tvmonitor"]


if __name__ == "__main__":
    

    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt",
                                    "MobileNetSSD_deploy.caffemodel")
    
    pipe = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    
    pipe.start(config)
    

    align_to = rs.align(rs.stream.color)

    profile_data = pipe.wait_for_frames().get_color_frame()


    #Size cropSize

    cropSize = (0,0)

    if profile_data.width / float(profile_data.height) > WHRatio:
        cropSize = (int(profile_data.height * WHRatio) ,profile_data.height)
    else:   
        cropSize = (profile_data.width, int(profile_data.width/WHRatio))


    #crop = cv2.rectangle(((profile_data.width - cropSize[1]) / 2, (profile_data.height - cropSize[0]]) / 2), cropSize,(0,0,0))
    crop = [( int ((profile_data.width - cropSize[1]) / 2), int((profile_data.height - cropSize[0]) / 2 )), cropSize]


    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)

    while(True):
        data = pipe.wait_for_frames()

        data = align_to.process(data)

        color_frame = data.get_color_frame()
        depth_frame = data.get_depth_frame()

        last_frame_number = 0
        if color_frame.get_frame_number == last_frame_number:
            continue

        last_frame_number = color_frame.get_frame_number()

        color_mat = np.asanyarray(color_frame.get_data())        
        depth_mat = np.asanyarray(depth_frame.get_data())


        
        input_blob = cv2.dnn.blobFromImage(color_mat,inScaleFactor,(inWidth,inHeight),meanVal,False)

        
        net.setInput(input_blob,"data")


        # print(net.getLayerNames())
        # detection = net.forward("fc")
        detection = net.forward("detection_out")

        #????? how to initialize
        
        
        detectionMat = np.reshape(detection,(detection.shape[2],detection.shape[3]))
        # detectionMat = np.zeros(detection.shape[2],detection.shape[3],cv2.CV_32F,detection)

        #?? how to crop a mat with rectangle
        print(crop)
        color_mat = color_mat[crop[0][0]:crop[1][0],crop[0][1]:crop[1][1]]

        depth_mat = depth_mat[crop[0][0]:crop[1][0],crop[0][1]:crop[1][1]]

        confiddenceThreshold = 0.0

        for i in range(0,detection.size // 7):
            confidence = detectionMat[i][2]
            if confidence > confiddenceThreshold:
                
                objectClass = detectionMat[i][1]

                xLeftBottom = int(detectionMat[i][3] * color_mat.shape[1])
                yLeftBottom = int(detectionMat[i][4] * color_mat.shape[0])
                xRightTop = int(detectionMat[i][5] * color_mat.shape[1])
                yRightTop = int(detectionMat[i][6] * color_mat.shape[0])

                print("obj is " , classNames[int(objectClass)] )

                obj = [ xLeftBottom, yLeftBottom, xRightTop - xLeftBottom, yRightTop-yLeftBottom ]

                # #crop again, how?
                m = cv2.mean(depth_mat[obj])
                
                conf = classNames[objectClass] + " " + m[0] + "meters away"

                cv2.rectangle(color_mat, obj, (0, 255, 0))
                # baseLine = 0
                # SlabelSize = cv2.getTextSize(ss.str(), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseLine)

                # center = (obj.br() + obj.tl())*0.5
                # center.x = center.x - labelSize.width / 2

                # cv2.rectangle(color_mat, cv2.rectangle((center.x, center.y - labelSize.height),\
                #     (labelSize.width, labelSize.height + baseLine)),\
                #     (255, 255, 255), FILLED)
                # putText(color_mat, classNames[objectClass], center, \
                #         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))


        cv2.imshow("Display Image",color_mat)
        


