import glob
import os
import shutil

def last_logfile_drive():
    #Find last LogFile from Pi Recorder folder
    list_of_files = glob.glob("/home/pi/pirecorder/logs/*") # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print("Latest LogFile is " + latest_file)

    #Save it to the Google Drive mounted folder
    shutil.copy2(latest_file, "/home/pi/mnt/Drive/Marçal's PhD/LogJackdaw/PiRecorder LogFiles")

def last_picture_drive():
    #Find the last picture captured by Pi Recorder
    list_of_recs = glob.glob("/home/pi/pirecorder/recordings/*") # * means all if need specific format then *.csv
    latest_rec = max(list_of_recs, key=os.path.getmtime)
    print("Latest_rec is " + latest_rec)
    latest_pic = max(glob.glob(latest_rec + "/*"), key=os.path.getmtime)
    print("Latest picture captured is " + latest_pic)

    #Save it to the Google Drive mounted folder
    shutil.copy2(latest_pic, "/home/pi/mnt/Drive/Marçal's PhD/LogJackdaw/PiRecorder pictures")

if __name__ == "__main__":
    last_logfile_drive()
    last_picture_drive()