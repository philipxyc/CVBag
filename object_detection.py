import numpy as np
import pyrealsense2 as rs
import cv2




inWidth      = 300
inHeight     = 300
WHRatio       = inWidth / (float)inHeight
inScaleFactor = 0.007843
meanVal       = 127.5
classNames[]  = ["background",
                "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair",
                "cow", "diningtable", "dog", "horse",
                "motorbike", "person", "pottedplant",
                "sheep", "sofa", "train", "tvmonitor"]


if __name__ == "__main__":
    

    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt",
                                    "MobileNetSSD_deploy.caffemodel")
    
    pipe = rs.pipeline()
    config = pipe.start()
    profile = config.get_stream(rs.stream.color)

    align_to = rs.align(rs.stream.color)

    #Size cropSize

    cropSize = (0,0)

    if profile.width() / float(profile.height()) > WHRatio:
        cropSize = (int(profile.height() * WHRatio） ,profile.height()))
    else:
        cropSize = (profile.width(), int(profile.width()/WHRatio)

    crop = cv2.rectangle(((profile.width() - cropSize.width) / 2,\
                    (profile.height() - cropSize.height) / 2),\
              cropSize)

    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)

    while(true):
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

        detection = net.forward("detection_out")

        #????? how to initialize
        detectionMat = np.zeros(detection.size[2],detection.size[3],cv.CV_32F,detection.ptr)

        #?? how to crop a mat with rectangle
        color_mat = color_mat(crop)

        depth_mat = depth_mat(crop)

        confiddenceThreshold = 0.0

        for i in range(0,detection.rows):
            confidence = detectionMat[i][2]
            if confidence > confiddenceThreshold:
                
                objectClass = detectionMat[i][1]

                xLeftBottom = int(detectionMat[i][3] * color_mat.cols)
                yLeftBottom = int(detectionMat[i][4] * color_mat.rows)
                xRightTop = int(detectionMat[i][5] * color_mat.cols)
                yRightTop = int(detectionMat[i][6] * color_mat.rows)



                obj = cv2.rectangle((xLeftBottom,yLeftBottom),\
                        (xRightTop - xLeftBottom, yRightTop-yLeftBottom) )

                #crop again, how?
                m = cv2.mean(depth_mat(obj))
                
                conf = classNames[objectClass] + "" + m[0] + "meters away"

                cv2.rectangle(color_mat, obj, (0, 255, 0))
                baseLine = 0
                SlabelSize = cv2.getTextSize(ss.str(), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseLine);

                center = (obj.br() + obj.tl())*0.5;
                center.x = center.x - labelSize.width / 2

                cv2.rectangle(color_mat, cv2.rectangle((center.x, center.y - labelSize.height),\
                    (labelSize.width, labelSize.height + baseLine)),\
                    (255, 255, 255), FILLED);
                putText(color_mat, classNames[objectClass], center, \
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))


        cv2.imshow(window_name,color_mat)
        


