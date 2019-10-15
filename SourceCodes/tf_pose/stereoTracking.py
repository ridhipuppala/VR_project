import argparse
import logging
import time
import numpy


import socket
HOST = '192.168.1.109' #SERVER IP
PORT = 52595
BUFFERSIZE = 1024
# TCP Socket client
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))
print("Socket Connection Established")
while True:
    s.sendall(campose.encode("utf-8"))
s.close()

import cv2
import numpy as np

from estimator import TfPoseEstimator
from networks import get_graph_path, model_wh

#python3 stereoTracking.py --cameraF=1 --cameraS=2
# To run the code and interchange 1 or 2 if necessary or check usb device number

'''
Nose = 0
Neck = 1
RShoulder = 2
RElbow = 3
RWrist = 4
LShoulder = 5
LElbow = 6
LWrist = 7
RHip = 8
RKnee = 9
RAnkle = 10
LHip = 11
LKnee = 12
LAnkle = 13
REye = 14
LEye = 15
REar = 16
LEar = 17
Background = 18
'''

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0
xl = 0
yl = 0
xr = 0
yr = 0
foc = 4.4
base = 70.0
zw0_prev = 0.0
ZA = [0.0]*5

#Origin coordinates intialization which will equal the first set of estimated world coordinate from first iteration
xw_origin = 0.0
yw_origin = 0.0
zw_origin = 0.0
flag = 0




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--cameraF', type=int, default=0)
    parser.add_argument('--cameraS', type=int, default=0)
    parser.add_argument('--zoom', type=float, default=1.0)
    parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resolution)
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    logger.debug('camF read+')
    camF = cv2.VideoCapture(args.cameraF)
    ret_val, image = camF.read()
    logger.info('camF image=%dx%d' % (image.shape[1], image.shape[0]))

    camS = cv2.VideoCapture(args.cameraS)
    ret_val, image = camS.read()
    logger.info('camS image=%dx%d' % (image.shape[1], image.shape[0]))

    while True:
	#Left Detection
        ret_valF, imageF = camF.read()

        if args.zoom < 1.0:
            canvasF = np.zeros_like(imageF)
            img_scaledF = cv2.resize(imageF, None, fx=args.zoom, fy=args.zoom, interpolation=cv2.INTER_LINEAR)
            dxF = (canvasF.shape[1] - img_scaledF.shape[1]) // 2
            dyF = (canvasF.shape[0] - img_scaledF.shape[0]) // 2
            canvasF[dyF:dyF + img_scaledF.shape[0], dxF:dxF + img_scaledF.shape[1]] = img_scaledF
            imageF = canvasF
        elif args.zoom > 1.0:
            img_scaledF = cv2.resize(imageF, None, fx=args.zoom, fy=args.zoom, interpolation=cv2.INTER_LINEAR)
            dxF = (img_scaled.shapeF[1] - image.shapeF[1]) // 2
            dyF = (img_scaled.shapeF[0] - image.shapeF[0]) // 2
            imageF = img_scaledF[dyF:image.shapeF[0], dxF:image.shapeF[1]]

        humansF = e.inference(imageF)

        imageF = TfPoseEstimator.draw_humans(imageF, humansF, imgcopy=False)
        centersF =TfPoseEstimator.joint_estimate(imageF, humansF, imgcopy=False)


	#Right Detection
        ret_valS, imageS = camS.read()

        if args.zoom < 1.0:
            canvasS = np.zeros_like(imageS)
            img_scaledS = cv2.resize(imageS, None, fx=args.zoom, fy=args.zoom, interpolation=cv2.INTER_LINEAR)
            dxS = (canvas.shapeS[1] - img_scaled.shapeS[1]) // 2
            dyS = (canvas.shapeS[0] - img_scaled.shapeS[0]) // 2
            canvasS[dyS:dyS + img_scaledS.shape[0], dxS:dxS + img_scaledS.shape[1]] = img_scaledS
            imageS = canvasS
        elif args.zoom > 1.0:
            img_scaledS = cv2.resize(imageS, None, fx=args.zoom, fy=args.zoom, interpolation=cv2.INTER_LINEAR)
            dxS = (img_scaledS.shape[1] - image.shapeS[1]) // 2
            dyS = (img_scaledS.shape[0] - image.shapeS[0]) // 2
            imageS = img_scaledS[dyS:imageS.shape[0], dxS:imageS.shape[1]]

        humansS = e.inference(imageS)
        imageS = TfPoseEstimator.draw_humans(imageS, humansS, imgcopy=False)
        centersS =TfPoseEstimator.joint_estimate(imageS, humansS, imgcopy=False)

        #World Coordinate Estimation
        try:
            ls_l = centersF[2]
            rs_l = centersF[5]
            xl = (ls_l[0] + rs_l[0])/2
            yl = (ls_l[1] + rs_l[1])/2
            #print("Left Cam: ",(xl,yl))
            ls_r = centersS[2]
            rs_r = centersS[5]
            xr = (ls_r[0] + rs_r[0])/2
            yr = (ls_r[1] + rs_r[1])/2
            #print("Right Cam: ",(xr,yr))

            if(xl == xr):
                continue
                print("xl == xr !!")
            zw0 = foc*base/(xl - xr)
            #Median Filter
            ZA.append(zw0)
            ZA.pop(0)
            ZA.sort()
            zw0 = ZA[2]
            xw0 = xl*zw0/foc
            yw0 = yl*zw0/foc

            #Coordinate Scaling
            zw = zw0/3
            xw = xw0/1000
            yw = yw0/1000

            #World coordinates origin
            if(flag == 0):
                xw_origin = xw
                yw_origin = -yw
                zw_origin = -zw
                flag = 1

            #Final Unity World coordinates
            zw = zw - zw_origin
            yw = -(yw - yw_origin)
            xw = -(xw - xw_origin)

            print("Cam World Coords: ", (xw,yw,zw))
            campose = str(xw) + ',' +str(yw) + ',' + str(zw)
            s.sendall(campose.encode("utf-8"))

        except KeyError:
            print("Shoulders not detected")


        #Display Both camera results
        a = (time.time() - fps_time)
        cv2.putText(imageF,
                    "FPS: %f" % (1.0 / a),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('Left Camera', imageF)

        cv2.putText(imageS,
                    "FPS: %f" % (1.0 / a),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('Right Camera', imageS)
        fps_time = time.time()

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    s.close()
