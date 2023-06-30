import cv2 as cv
import cv2.aruco as aruco
import numpy as np

def detect(image):
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

# Define the parameters for marker detection
    parameters = aruco.DetectorParameters()

    # Detect ArUco markers in the image
    detector = aruco.ArucoDetector(aruco_dict,parameters)

    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)
    # Draw the detected markers on the image
    order=[0,1,5,4]
    box=[0 for _ in range(len(markerCorners))]
    for i in range(len(markerCorners)):
        try:
            box[order.index(markerIds[i][0])]=markerCorners[i].mean(axis=1)[0].astype('int32')
            image=cv.polylines(image,markerCorners[i].astype('int32'),True,(255,0,0),2)
        except:
            continue
        print(markerIds[i])
    try:
        image=cv.polylines(image,[np.array(box)],True,(0,255,0),2)
    except:
        pass
    
    if len(box)==4:
        inp=np.float32(box)
        out=np.float32([[0,0],[0,500],[500,500],[500,0]])
        matrix = cv.getPerspectiveTransform(inp, out)
        image = cv.warpPerspective(image, matrix, (500, 500))

    return image


class MobileCamera:
    def getVideo(self, camera):
        self.camera = camera
        cap = cv.VideoCapture(self.camera)
        while True:
            ref, frame = cap.read()
            frame = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv.imshow("mobileCam", detect(frame))
            if cv.waitKey(1) == ord('q'):
                break
            
        cap.release()
        cv.destroyAllWindows()


cam = MobileCamera()
cam.getVideo("http://192.168.0.121:8080/video")