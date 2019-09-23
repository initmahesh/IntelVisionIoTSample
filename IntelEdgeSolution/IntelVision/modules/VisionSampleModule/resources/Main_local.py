import random
import time
import sys
import numpy as np
import onnxruntime as rt
import cv2
import json
import datetime
from PIL import Image,ImageDraw


def sigmoid(x, derivative=False):
  return x*(1-x) if derivative else 1/(1+np.exp(-x))

def softmax(x):
  scoreMatExp = np.exp(np.asarray(x))
  return scoreMatExp / scoreMatExp.sum(0)

def model_inferencing():
    
    clut = [(0,0,0),(255,0,0),(255,0,255),(0,0,255),(0,200,0)]
    label = ["person"]

    sess = rt.InferenceSession("model.onnx")
    input_name = sess.get_inputs()[0].name

    cap = cv2.VideoCapture('peopletest.mp4')
    #cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    source_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    souce_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(source_width/2)
    height = int(souce_height/2)
    x_scale = float(width)/416.0
    y_scale = float(height)/416.0

    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #output_video = cv2.VideoWriter('cpu_output.avi',fourcc, float(17.0), (640,360))
    ret, frame = cap.read()
    sentTime = datetime.datetime.now()

    i = 0
    while cap.isOpened():
        l_start = time.time()
        _, _ = cap.read()
        ret, frame = cap.read()       
        if not ret:
            print('no video RESETTING FRAMES TO 0 TO RUN IN LOOP')
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        initial_w = cap.get(3)
        initial_h = cap.get(4)
        
        # preprocessing the input frame
        frame = cv2.resize(frame, (width, height))
        in_frame = cv2.resize(frame, (416, 416))
        X = np.asarray(in_frame)
        X = X.astype(np.float32)
        X = X.transpose(2,0,1)
        X = X.reshape(1,3,416,416)
        
        start = time.time()
        out = sess.run(None, {input_name: X.astype(np.float32)})
        end = time.time()
        inference_time = end - start
        print("Inference time is ::{}".format(inference_time))
        out = out[0][0]

        numClasses = 1
        anchors = [1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52]
        anchors = np.array(anchors, dtype='f') / 2

        existingLabels = {l: [] for l in label}

        for cy in range(0,13):
            for cx in range(0,13):
                for b in range(0,5):
                    channel = b*(numClasses+5)
                    tx = out[channel  ][cy][cx]
                    ty = out[channel+1][cy][cx]
                    tw = out[channel+2][cy][cx]
                    th = out[channel+3][cy][cx]
                    tc = out[channel+4][cy][cx]

                    x = (float(cx) + sigmoid(tx))*32
                    y = (float(cy) + sigmoid(ty))*32

                    w = np.exp(tw) * 32 * anchors[2*b]
                    h = np.exp(th) * 32 * anchors[2*b+1] 

                    confidence = sigmoid(tc)

                    classes = np.zeros(numClasses)
                    for c in range(0,numClasses):
                        classes[c] = out[channel + 5 +c][cy][cx]
                    classes = softmax(classes)
                    detectedClass = classes.argmax()
                    
                    if 0.55< classes[detectedClass]*confidence:
                        color =clut[detectedClass]
                        x = (x - w/2)*x_scale
                        y = (y - h/2)*y_scale
                        w *= x_scale
                        h *= y_scale
                        #cv2.rectangle(frame, (int(x),int(y)),(int(x+w),int(y+h)),color,1)
                        
                        labelX = int((x+x+w)/2)
                        labelY = int((y+y+h)/2)
                        addLabel = True
                        labThreshold = 40
                        for point in existingLabels[label[detectedClass]]:
                            if labelX < point[0] + labThreshold and labelX > point[0] - labThreshold and \
                                labelY < point[1] + labThreshold and labelY > point[1] - labThreshold:
                                addLabel = False
                        if addLabel:
                            cv2.rectangle(frame, (int(x),int(y)),(int(x+w),int(y+h)),color,2)
                            cv2.rectangle(frame, (int(x),int(y-13)),(int(x)+9*len(label[detectedClass]),int(y)),color,-1)
                            cv2.putText(frame,label[detectedClass],(int(x)+2,int(y)-3),cv2.FONT_HERSHEY_COMPLEX,0.4,(255,255,255),1)
                            existingLabels[label[detectedClass]].append((labelX,labelY))
                        print('{} detected in frame {}'.format(label[detectedClass],i))


        #output_video.write(frame)
        cv2.putText(frame,'CPU',(10,20),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        cv2.putText(frame,'FPS: {}'.format(1.0/inference_time),(10,40),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print('Processed Frame {}'.format(i))
        i += 1
        l_end = time.time()
        print('Loop Time = {}'.format(l_end - l_start))
    #output_video.release()
    cv2.destroyAllWindows()


model_inferencing()
