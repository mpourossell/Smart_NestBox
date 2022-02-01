import cv2
import glob
import os
import io
import numpy as np
from PIL import Image
import logging
import yagmail

# start a connection with GMAIL
FROM = "jackdaw.local@gmail.com"
PASS = "jackdaw1234"
yag = yagmail.SMTP(FROM, PASS)

# define the variables
to = "mpourossell@gmail.com"
subject = "ERROR in your Raspberry Pi!"

# define blackness sensitivity to check if LED is working
x = 20 # The range for a pixel's value in grayscale is (0-255), from black to white. 
	# mean pixel value > x denotes a considered bright image
	# mean pixel value < x denotes a considered black image

#Set logging parameters
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("CheckLED.log")
formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#Find the last recording folder created by PiRecorder
list_of_recs = glob.glob("/home/pi/pirecorder/recordings/*") # * means all if need specific format then *.jpg...
latest_rec = max(list_of_recs, key=os.path.getmtime)
logger.debug("Latest_rec is " + latest_rec)
#Find the last picture capured by PiRecorder
latest_pic = max(glob.glob(latest_rec + "/*"), key=os.path.getmtime)
logger.debug("Latest picture captured is " + latest_pic)

#Load the picture in PIL_Image
file_size = os.path.getsize(latest_pic)

#Check if image size is 0byte
if file_size == 0:
	logger.debug("Image " + latest_pic " is damaged! File size = 0bytes")
	# send the email
	body = "ERROR! Capturing damaged images! File size = 0bytes"
	yag.send(to, subject, body)
	logger.debug("ERROR Email sent to " + FROM)
else:
	logger.debug (latest_pic + " size is: " + str(file_size/1000) + " Kb")

	#Analize the blackness of the picture to see if LED is working (no black picture) or not (black picture)
	image = cv2.imread(latest_pic, 0)
	blur = cv2.blur(image, (5, 5))  # With kernel size depending upon image size
	if cv2.mean(blur) > (x, x, x, x):  # The range for a pixel's value in grayscale is (0-255), from black to white. 
		logger.debug("LED is working fine") # (x - 255) denotes there is some light in the image
	else:
		logger.debug("ERROR! LED is not working") # (0 - x) denotes there is no light in the image
		body = "ERROR! LED is not working"
		yag.send(to, subject, body)
		logger.debug("ERROR Email sent!")