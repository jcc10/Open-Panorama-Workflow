#-------------------------------------------------------------------------------
# Name:        Automation Toolkit
# Purpose:     To automate stuff by running many commands.
#-------------------------------------------------------------------------------

# Import all the stuff
import os
# REMEMBER PIL WILL NOT FUNCTION CORRECTLY IF YOU SAVE AS 16 BIT .TIF!
from PIL import Image
import subprocess
import time
from random import Random

class AutomatorTools :
    # This is where all the common tools for PanoAutomator will go, this is so it's a sub-class.
    # This will be moved into a seprate file and subfolder later.

    def __init__(self, debugMode, max_processes):
        self.debug = debugMode
        self.__MaxProcesses = max_processes
        print('Running with ' + str(max_processes) + " processes")
        self.__processes = set()
        self.__RDG = Random()
        self.__TempFiles = set()

    # Runs a command if there is less than the Max currently running.
    # (See processWait)
    def command(self, cmd):
        self.processesWait(self.__MaxProcesses)
        if self.debug == True:
            self.log(cmd, 1)
        self.__processes.add(subprocess.Popen(cmd, shell=True))

    # Waits until the ammount of currently running commands is less than the count given
    # Give 0 for none.
    def processesWait(self, count='Max_Processes'):
        if count == "Max_Processes":
            count = self.__MaxProcesses
        count -= count
        while len(self.__processes) > count:
            time.sleep(.1)
            self.__processes.difference_update([
                p for p in self.__processes if p.poll() is not None])

    # Dysplays text to the user. Later if I ever add a gui this will become the text log function.
    def log(self, text, dbg=0):
        if dbg == 1:
            if self.debug == True:
                print("DEBUG: ", end='')
        print(text)

    # Name stripping finction V2
    # TODO: See about just writing a extension stripping function.
    def namestrip(self, data, mode=0):
        if mode == 0:
            return(data[:8] + data[-4:])
        elif mode == 1 :
            # used to remove the R or L in the ingested folder list. Also ensures you don't have duplicate entries in the output.
            out = []
            for s in data:
                s2 = self.namestrip(s, 0)
                if not(s2 in out):
                    out.append(s2)
            return out
        elif mode == 2 :
            # Strips .tif file extensions.
            o = []
            for s in data:
                s2 = s.replace('.tif', '')
                o.append(s2)
                # Returns the list WITH NO EXTENSIONS remember to add them back on
            return o
        elif mode == 3 :
            o = []
            for s in data:
                # Strips .jpg file extensions
                s2 = s.replace('.jpg', '')
                s3 = s2.replace('.jpeg', '')
                o.append(s3)
                # Returns the list WITH NO EXTENSIONS remember to add them back on
            return o
        elif mode == 4 :
            # Just incase you save your project file in the stitched directory.
            # This should be replaced with a ignore extnsion function in the future.
            o = []
            for s in data:
                if s[-4:] == '.pts':
                    None
                else:
                    o.append(s)
            return o

    # Lists all the files in a folder. Thats it.
    # (The folder is reletive to the program.)
    def folderlist(self, foldername):
        dirname = './' + foldername
        return([f for f in os.listdir(dirname)])

    # Temp File Saver
    # This will save a file in the temp directory under a garunteed unique filename and return the filename (Without the directory)
    def tempFile(self, data, extension='temp'):
        filename = str(self.__RDG.randint(0,99999999999)) + "." + extension
        while (filename in self.__TempFiles):
            filename = str(self.__RDG.randint(0,99999999999)) + "." + extension
        self.__TempFiles.add(filename)
        wr = open('./temp/' + filename, 'w+')
        wr.write(data)
        return(filename)

    # Temp File Purger
    # This runs through the list of temp files and will delete all of them.
    # Then it resets the temp file list.
    def prugeTemps(self):
        for file in self.__TempFiles :
            os.remove('./temp/' + file)
        self.__TempFiles = set()
