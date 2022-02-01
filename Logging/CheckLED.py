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
yag = yagmail.SMTP(FROM, "jackdaw1234")

# define the variables
to = "mpourossell@gmail.com"
subject = "ERROR in your Raspberry Pi!"

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

#Find the last picture captured by Pi Recorder
list_of_recs = glob.glob("/home/pi/pirecorder/recordings/*") # * means all if need specific format then *.jpg...
latest_rec = max(list_of_recs, key=os.path.getmtime)
logger.debug("Latest_rec is " + latest_rec)
latest_pic = max(glob.glob(latest_rec + "/*"), key=os.path.getmtime)
logger.debug("Latest picture captured is " + latest_pic)

#Load the picture in PIL_Image
file_size = os.path.getsize(latest_pic)

#Check if image size is 0
if file_size == 0:
	logger.debug("Image damaged! Byte = 0")
	# send the email
	body = "ERROR! Capturing damaged images! File size = 0bytes"
	yag.send(to, subject, body)
	logger.debug("ERROR Email sent!")
else:
	logger.debug ("image size using os.path is: " + str(file_size/1000) + " Kb")
	image = cv2.imread(latest_pic, 0)
	blur = cv2.blur(image, (5, 5))  # With kernel size depending upon image size
	if cv2.mean(blur) > (20, 20, 20, 20):  # The range for a pixel's value in grayscale is (0-255), 127 lies midway
		logger.debug("LED is working fine") # (127 - 255) denotes light image
	else:
		logger.debug("ERROR! LED is not working") # (0 - 127) denotes dark image
		body = "ERROR! LED is not working"
		yag.send(to, subject, body)
		logger.debug("ERROR Email sent!")