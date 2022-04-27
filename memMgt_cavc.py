"""
Purpose:   Memory management on edge devices.
Licence:   This source code for Memory management on edge devices, is intellectual property of VaaaN infra Pvt. Ltd.
           Therefore, copying, modifying or distributing this source code without authorization is strictly prohibited.
Author:    Agam Damaraju
E-Mail:    agam.damaraju@vaaaninfra.com
Version:   1.0.0.0
Comments:  This source code is upgraded version of MM1.0.0.0, which was authored by Rinku Sharma.
           This project had been executed under the guidance of Mr. Manish Arya (manish.arya@vaaaninfra.com)
"""

####################################### Importing libraries, modules and files ##########################################
import os, shutil, logging, glob, time
from threading import Thread
import xml.etree.ElementTree as ET
from logging.handlers import TimedRotatingFileHandler
from configFetch import DBM

########################################### Getting root ############################
os.chdir(os.getcwd())
os.chdir("..")
os.chdir("..")

###-------------------------------------- Parsing data from web app --------------------------------------
config_db_path = r"./C-AVC_config/cavc.db"
man = DBM(config_db_path,'MAN')
manPage= man.DBFetch(['ImageBackup','LogBackup'])
days_backup = manPage[0]
days_backup_logs = manPage[1]
os.chdir("C-AVC")
media_path = "./Vehicle media"
log_path = "./Logs"

################################################# Logger initiallization #######################################################
MMSlog_dir = os.path.join("Logs","memMgt")
if not os.path.isdir(MMSlog_dir):
    os.makedirs(os.path.join(MMSlog_dir))
log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_level = 10
mmslog = logging.getLogger("Rotating Log")
mmslog.setLevel(logging.INFO)
file_handler = TimedRotatingFileHandler((MMSlog_dir + '//' + "MM" + '.log'), when="midnight", interval=1)
file_handler.setLevel(log_level)
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
mmslog.addHandler(file_handler)
file_handler.suffix = "%Y%m%d"
mmslog.addHandler(file_handler)

mmslog.info("########################## SUMMERY START #########################")
mmslog.info("Purpose:   Memory management on edge devices")
mmslog.info("Licence:   This application for Memory management on edge devices, is intellectual property of VaaaN infra Pvt. Ltd. Therefore, using or distributing this application without authorization is strictly prohibited.")
mmslog.info("Author:    Agam Damaraju")
mmslog.info("E-Mail:    agam.damaraju@vaaaninfra.com")
mmslog.info("Version:   1.0.0.0")
mmslog.info("Comments:  This application is upgraded version of MM1.0.0.0, which was authored by Rinku Sharma.")
mmslog.info("This project had been executed under the guidance of Mr. Manish Arya (manish.arya@vaaaninfra.com)")
mmslog.info("############################ SUMMERY END ##########################")
mmslog.info("############# CONFIG PARSED DATA START #############")
mmslog.info("MM config media file path  {} ".format(media_path))
mmslog.info("MM config days backup {} ".format(days_backup))
mmslog.info("MM config log file path  {} ".format(log_path))
mmslog.info("MM config log days backup  {} ".format(days_backup_logs))
mmslog.info("######################## CONFIG PARSED DATA END ###################")

####################################################### MemoryMgt class ##############################################
class MemoryMgt:
    def __init__(self, media_path, days_backup, log_path, days_backup_logs):
        self.media_path = media_path
        self.totalSeconds = days_backup * 86400
        self.log_path = log_path
        self.totalSeconds_logs = days_backup_logs * 86400
        Thread(target=self.deleteMedia, args=()).start()
        Thread(target=self.deleteLogs, args=()).start()
        Thread(target=self.sentFolders, args=()).start()

    def deleteMedia(self):
        while True:
            try:
                if os.path.isdir(self.media_path):
                    for date in os.listdir(self.media_path):
                        if date.find("sent") != -1:
                            for dir in os.listdir(os.path.join(self.media_path, date)):
                                if dir == "Profiles (temp)" or dir == "Videos (temp)":
                                    for file in os.listdir(os.path.join(self.media_path, date, dir)):
                                        if time.time() - os.path.getctime(os.path.join(self.media_path, date, dir, file)) >= self.totalSeconds and file != "temp.jpg":
                                            if len(glob.glob(os.path.join(self.media_path, date, dir, "*.mp4"))) == 1 or len(glob.glob(os.path.join(self.media_path, date, dir, "*.jpg"))) == 1:
                                                shutil.rmtree(os.path.join(self.media_path, date))
                                                mmslog.info(f"{os.path.join(self.media_path, date)} is last file in the folder. Hence, folder {os.path.join(self.media_path, dir)} has been deleted.")
                                            else:
                                                os.remove(os.path.join(self.media_path, date, dir, file))
                                                mmslog.info(f"File {os.path.join(self.media_path, date, dir, file)} has been deleted.")
            except Exception as e:
                mmslog.error(f"In deletMedia method: {e}")
    
    def deleteLogs(self):
        while True:
            try:
                if os.path.isdir(self.log_path):
                    for folder in os.listdir(self.log_path):
                        for log in os.listdir(os.path.join(self.log_path, folder)):
                            if time.time() - os.path.getctime(os.path.join(self.log_path, folder, log)) >= self.totalSeconds_logs and log[-3:] != "log":
                                os.remove(os.path.join(self.log_path, folder, log))
                                mmslog.info(f"Log {os.path.join(self.log_path, folder, log)} has been deleted.")
            except Exception as e:
                mmslog.error(f"In deletLogs method: {e}")

    def sentFolders(self):
        while True:
            try:
                if os.path.isdir(self.media_path):
                    for date in os.listdir(self.media_path):
                        if date != time.strftime('%d-%m-%y'):
                            total_sent = 0
                            for dir in os.listdir(os.path.join(self.media_path, date)):
                                if dir == "Profiles (temp)" or dir == "Videos (temp)":
                                    for file in os.listdir(os.path.join(self.media_path, date, dir)):
                                        if file.find("_sent") != -1:
                                            total_sent += 1
                            if total_sent == len(glob.glob(os.path.join(self.media_path, date, "Profiles (temp)", "*.jpg"))) + len(glob.glob(os.path.join(self.media_path, date, "Videos (temp)", "*.mp4"))) and date.find("sent") == -1:
                                date_sent = f"{date}_sent"
                                os.rename(os.path.join(self.media_path, date), os.path.join(self.media_path, date_sent))
                                mmslog.info(f"{date} folder renamed with sent.")
            except Exception as e:
                mmslog.error(f"In sentFolders method: {e}")

######################################################### Main function ##############################################
def main():
    global media_path, days_backup, log_path, days_backup_logs
    print("Memory management is running...")
    MemoryMgt(media_path, days_backup, log_path, days_backup_logs)

if __name__ == "__main__":
    main()