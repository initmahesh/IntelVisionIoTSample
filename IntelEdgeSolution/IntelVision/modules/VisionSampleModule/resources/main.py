# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError
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

def model_inferencing(hub_manager):
    
    clut = [(0,0,0),(255,0,0),(255,0,255),(0,0,255),(0,200,0)]
    label = ["unprotected","bunny suit","glasses","head","robot"]

    sess = rt.InferenceSession("Tiny_YoloV2_Cleanroom.onnx")
    input_name = sess.get_inputs()[0].name

    cap = cv2.VideoCapture('manufacture1.mp4')
    #cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    x_scale = float(width)/416.0
    y_scale = float(height)/416.0

    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #output_video = cv2.VideoWriter('cpu_output.avi',fourcc, float(17.0), (640,360))
    ret, frame = cap.read()
    sentTime = datetime.datetime.now()
    headCount = 0
    bunnySuitCount = 0
    glassesCount = 0
    headCountAccuracy = []
    bunnySuitCountAccuracy = []
    glassesCountAccuracy = []


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

        numClasses = 5
        anchors = [1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52]

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

                    w = np.exp(tw) * 32 * anchors[2*b  ]
                    h = np.exp(th) * 32 * anchors[2*b+1] 

                    confidence = sigmoid(tc)

                    classes = np.zeros(numClasses)
                    for c in range(0,numClasses):
                        classes[c] = out[channel + 5 +c][cy][cx]
                    classes = softmax(classes)
                    detectedClass = classes.argmax()
                    
                    if 0.45< classes[detectedClass]*confidence:
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
                        resultConficence = np.around(confidence*100, decimals = 4)
                        print('Result Conficence: ' + str(resultConficence))
                        if label[detectedClass] == "bunny suit":
                            bunnySuitCount = bunnySuitCount + 1
                            bunnySuitCountAccuracy.append(resultConficence)
                        elif label[detectedClass] == "glasses":
                            glassesCount = glassesCount + 1
                            glassesCountAccuracy.append(resultConficence)
                        elif label[detectedClass] == "head":
                            headCount = headCount + 1
                            headCountAccuracy.append(resultConficence)

                        currentTime = datetime.datetime.now()
                        print("total seconds since message: " + str((currentTime - sentTime).total_seconds()))
                        if (currentTime - sentTime).total_seconds() > 5:
                            inference_result = {"bunnySuitCount": bunnySuitCount,
                             "bunnySuitCountAccuracy":(sum(glassesCountAccuracy) / len(glassesCountAccuracy)),
                             "glassesCount": glassesCount,
                             "glassesCountAccuracy":(sum(glassesCountAccuracy) / len(glassesCountAccuracy)),
                             "headCount": headCount,
                             "headCountAccuracy":(sum(headCountAccuracy) / len(headCountAccuracy))
                             }
                            hub_manager.send_msg_to_cloud(json.dumps(inference_result))
                            headCount = 0
                            bunnySuitCount = 0
                            glassesCount = 0
                            headCountAccuracy = []
                            bunnySuitCountAccuracy = []
                            glassesCountAccuracy = []
                            sentTime = datetime.datetime.now()

        #output_video.write(frame)
        cv2.putText(frame,'VPU',(10,20),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
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



# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT




# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )


# receive_message_callback is invoked when an incoming message arrives on the specified 
# input queue (in the case of this sample, "input1").  Because this is a filter module, 
# we will forward this message onto the "output1" queue.
def receive_message_callback(message, hubManager):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    hubManager.forward_event_to_output("output1", message, 0)
    return IoTHubMessageDispositionResult.ACCEPTED


class HubManager(object):

    def __init__(
            self,
            protocol=IoTHubTransportProvider.MQTT):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)
        
        # sets the callback when a message arrives on "input1" queue.  Messages sent to 
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback("input1", receive_message_callback, self)
        #self.client.set_module_twin_callback(self.module_twin_callback, self)

    # Forwards the message received onto the next stage in the process.
    def forward_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)
    def send_msg_to_cloud(self, msg):
        try :
            #logging.info("sending message...")
            message=IoTHubMessage(msg)
            self.client.send_event_async(
                "output1", 
                message, 
                send_confirmation_callback, 
                0)
            print("finished sending message...")
        except Exception :
            print ("Exception in SendMsgToCloud")
            pass


def main(protocol):
    try:
        print ( "\nPython %s\n" % sys.version )
        print ( "IoT Hub Client for Python" )

        hub_manager = HubManager(protocol)

        print ( "Starting the IoT Hub Python sample using protocol %s..." % hub_manager.client_protocol )
        model_inferencing(hub_manager)
        # print ( "The sample is now waiting for messages and will indefinitely.  Press Ctrl-C to exit. ")

        # while True:
        #     time.sleep(1)
        #     inference_result = {"label":"test","confidence":100}
        #     hub_manager.send_msg_to_cloud(json.dumps(inference_result))

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubModuleClient sample stopped" )

if __name__ == '__main__':
    main(PROTOCOL)