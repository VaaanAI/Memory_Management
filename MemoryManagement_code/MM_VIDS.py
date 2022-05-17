# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 10:14:30 2022

@author: Tsingh
"""

import os
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler

MMSlog_dir = os.path.join("Logs")
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

def drop_empty_folders(directory):
    """Verify that every empty folder removed in local storage."""

    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)
            mmslog.info('Folder Deleted - %s',dirpath)
            


def walk_dir(ImageBackupDays,ImagePath):
    while True:
        try :
        #global ImageBackupDays,ImagePath
            now = time.time()
            filecompare = now - ImageBackupDays * 86400
            for i in ImagePath.split(','):
                drop_empty_folders(i)
                
                #print(i)
                for root, dirs, files in os.walk(i, topdown=False):
                    # if not dirs and not files :
                    #     os.rmdir(root)
                    # else:
                    #     continue
                    for name in files:
                        xx = os.path.join(root, name)
                        ft=os.stat(xx).st_mtime
                
        #         print(xx ,ft)
                        try:
                            if ft<filecompare:
                                #shutil.rmtree(folder)
                                os.remove(xx)
                                mmslog.info('Files Deleted - %s',xx)
                               # print(xx)
                            else:
                                continue
                    
                    
                        except Exception as e:
                            mmslog.error('Error in File deletion',e )
                        #print(e)
        except Exception as e:
            mmslog.error('Exception in BackupDays comparison or File Deletion',e)
            pass
            
def main():
    #global media_path, days_backup
    mmslog.info('Memory Management is running.')
    
    try:
    
        with open('MM.json', 'r') as file_reader:
            MM = json.load(file_reader)
            
        day=MM["BackupDays"]
        paths=MM["Paths"]
        
        mmslog.info("Configuration file imported succesfully.")
    except Exception as e:
        mmslog.error('Error in reading Configuration file (MM.json) - ',e)
    try:
        for i in paths.split(','):
                drop_empty_folders(i)
                
    except :
        mmslog.error('Error in Deleting empty Folders')
        pass
        #print(e)
    
    #print("Memory management is running...")
    walk_dir(day,paths)
    #print('Printed')

if __name__ == "__main__":
    main()