#Import packages
import os
import sys
import cv2
import argparse
import time
import datetime
import imutils
import pandas as pd
import numpy as np

#def motion_detection():

#Create a dataframe to write movement times
motion_list = [ None, None ]
Time = []
df = pd.DataFrame(columns = ["Start", "End"])

#Select video file to analyse
video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW) # value (0) selects the devices default camera (Webcam). Write a path instead for a video file

if (video_capture.isOpened() == False):
    print("Error opening the video file")
#else:
    # Get frame rate information
    #fps = int(video_capture.get(5))
    #print("Frame Rate : ",fps,"frames per second")  
    # Get frame count
    #frame_count = video_capture.get(7)
    #print("Frame count : ", frame_count)

#define sensitivity and background upgrade rate
background_memory = 0.2 #higher number = faster update of the backgroud
sensitivity = 800 #how many changed pixels needed to detect event as "motion". Needs to be higher if noisy view! 
threshold = 10 #how much a pixel has to change by to be marked as "changed". In the greyscale image, from 1 (black) to 255 (white).
first_frame = None # instinate the first fame

while True:
    frame = video_capture.read()[1] # gives 2 outputs retval,frame - [1] selects frame
    text = 'Quiet'
    motion = 0

    greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # make each frame greyscale wich is needed for threshold 
    gaussian_frame = cv2.GaussianBlur(greyscale_frame, (21,21),0)
    # uses a kernal of size(21,21) // has to be odd number to ensure there is a valid integer in the centre
    # and we need to specify the standerd devation in x and y direction wich is the (0) if only x(sigma x) is specified 
    # then y(sigma y) is taken as same as x. sigma = standerd deveation(mathmetics term) 
    blur_frame = cv2.blur(gaussian_frame, (5,5)) # uses a kernal of size(5,5)(width,height) wich goes over 5x5 pixel area left to right
    # does a calculation and the pixel located in the centre of the kernal will become 
    # a new value(the sum of the kernal after the calculations) and then it moves to the right one and has a new centre pixel
    # and does it all over again..untill the image is done, obv this can cause the edges to not be changed, but is very minute
    greyscale_image = blur_frame 
    # greyscale image with blur etc wich is the final image ready to be used for threshold and motion detecion

    if first_frame is None:
        first_frame = greyscale_image.copy().astype("float")
        # first frame is set for background subtraction(BS) using absdiff and then using threshold to get the foreground mask
        # foreground mask (black background anything that wasnt in image in first frame but is in newframe over the threshold will
        # be a white pixel(white) foreground image is black with new object being white...there is the motion detection
    else:
        pass

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(greyscale_image, first_frame, background_memory)
    frame_delta = cv2.absdiff(greyscale_image, cv2.convertScaleAbs(first_frame))    
    # calculates the diffrence between each element/pixel between the two images, first_frame - greyscale (on each element)
    #0.02 in accumulateWeighted is the time of the background update
    
    # edit the ** thresh ** depending on the light/dark in room, change the 100(anything pixel value over 100 will become 255(white))
    thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
    # threshold gives two outputs retval,threshold image. using [1] on the end i am selecting the threshold image that is produced

    dilate_image = cv2.dilate(thresh, None, iterations=2)
    # dilate = dilate,grow,expand - the effect on a binary image(black background and white foregorund) is to enlarge/expand the white 
    # pixels in the foreground wich are white(255), element=Mat() = default 3x3 kernal matrix and iterartions=2 means it
    # will do it twice

    contours, hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # contours gives 3 diffrent ouputs image, contours and hierarchy, so using [1] on end means contours = [1](cnt)
    # cv2.CHAIN_APPROX_SIMPLE saves memory by removing all redundent points and comppressing the contour, if you have a rectangle
    # with 4 straight lines you dont need to plot each point along the line, you only need to plot the corners of the rectangle
    # and then join the lines, eg instead of having say 750 points, you have 4 points.... look at the memory you save!

    for c in contours:
        if cv2.contourArea(c) > 800: # if contour area is more than the sensitivity number of non-zero(not-black) pixels(white)
            #cv2.accumulateWeighted(greyscale_image, first_frame, 0.005)
            #(x, y, w, h) = cv2.boundingRect(c) # x,y are the top left of the contour and w,h are the width and hieght 
            #cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2) # (0, 255, 0) = color R,G,B = lime / 2 = thickness
            # image used for rectangle is frame so that its on the secruity feed image and not the binary/threshold/foreground image
            # as its already used the threshold/(binary image) to find the contours this image/frame is what image it will be drawed on            
            text = 'Movement'
            # text that appears when there is motion in video feed
            motion = 1
            #print("Motion detected at " + datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'))
            #put datetime in the image
            cv2.putText(frame, datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'), 
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX , 0.35, (0, 0, 255),1)

            path = "C:/Users/Marçal Pou Rossell/OneDrive - CREAF/Documentos/Codi/motionpictures"
            # save frame as JPEG file, 1 frame per second, in a folder
            os.chdir(path)
            st = datetime.datetime.now().strftime('%Y %m %d %H %M %S') #date and time
            
            cv2.imwrite('BoxName '+ st +'.jpg', frame)
            if not cv2.imwrite('BoxName '+ st +'.jpg', frame):
                print("Could not write image")
        else:
            pass

    #Now write movement detections in the dataframe
    #Appending status of motion
    motion_list.append(motion) 
    motion_list = motion_list[-2:]
    # Appending Start time of motion
    if motion_list[-1] == 1 and motion_list[-2] == 0:
        Time.append(datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'))
    # Appending End time of motion
    if motion_list[-1] == 0 and motion_list[-2] == 1:
        Time.append(datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'))

    ''' now draw text and timestamp on the images '''
    font = cv2.FONT_HERSHEY_SIMPLEX 
    cv2.putText(frame, '{+} Nest box Status: %s' % (text), 
        (10,20), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (0, 0, 255), 2)
    # frame is the image on wich the text will go. 0.5 is size of font, (0,0,255) is R,G,B color of font, 2 on end is LINE THICKNESS!


    cv2.putText(frame, datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'), 
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX , 0.35, (0, 0, 255),1) # frame.shape[0] = hieght, frame.shape[1] = width,ssssssssssssss
    # using datetime to get date/time stamp, for font positions using frame.shape() wich returns a tuple of (rows,columns,channels)
    # going 10 accross in rows/width so need columns with frame.shape()[0] we are selecting columns so how ever many pixel height 
    # the image is - 10 so oppisite end at bottom instead of being at the top like the other text

    cv2.imshow('Raw video', frame)
    cv2.imshow('Threshold(foreground mask)', dilate_image)
    cv2.imshow('Frame_delta', frame_delta)

    key = cv2.waitKey(1) & 0xFF # (1) = time delay in seconds before execution, and 0xFF takes the last 8 bit to check value or sumin
    if key == ord('q'): #Press Q key to kill the runing process.
        cv2.destroyAllWindows()
        break

#Create a dataframe of the times of movements.csv
for i in range(0, len(Time), 2):
    df = df.append({"Start":Time[i], "End":Time[i + 1]}, ignore_index = True)

df.to_csv("Time_of_movements.csv")
video_capture.release()
cv2.destroyAllWindows()

#if __name__=='__main__':    
    #motion_detection()