#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
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
        self.__processes = set()
        self.__RDG = Random()
        self.__TempFiles = set()

    # Runs a command, if this breaks, I don't want to go looking for all of the calls.
    def command(self, cmd):
        self.processesWait(self.__MaxProcesses)
        if self.debug == True:
            self.log(cmd, 1)
        self.__processes.add(subprocess.Popen(cmd, shell=True))

    def processesWait(self, count='Max_Processes'):
        if count == "Max_Processes":
            count = self.__MaxProcesses
        count -= count
        while len(self.__processes) > count:
            time.sleep(.1)
            self.__processes.difference_update([
                p for p in self.__processes if p.poll() is not None])


    def sanitize_dir(self, string):
        return(
            string.translate(
                str.maketrans(
                    {"-":  r"\-",
                    " ": r"\ ",
                    "]":  r"\]",
                    "\\": r"\\",
                    "^":  r"\^",
                    "$":  r"\$",
                    "*":  r"\*"}
                )
            )
        )

    # Dysplays text to the user. Later if I ever add a gui this will become the text log function.
    def log(self, text, dbg=0):
        if dbg == 1:
            if self.debug == True:
                print("DEBUG: ", end='')
        print(text)
    # Name stripping finction V2,
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

    def folderlist(self, foldername):
        dirname = './' + foldername
        return([f for f in os.listdir(dirname)])

    # File Saver
    # This is used so we can arbatrarally save files reletave to the program.
    # Eventually this will be replaced with a temporarry file interface where it returns the full path of the tempfile.
    def tempFile(self, data, extension='temp'):
        filename = str(self.__RDG.randint(0,99999999999)) + extension
        while (filename in self.__TempFiles):
            filename = str(self.__RDG.randint(0,99999999999)) + extension
        self.__TempFiles.add(filename)
        wr = open('./temp/' + filename, 'w+')
        wr.write(data)
        return(filename)

    def prugeTemps(self):
        for file in self.__TempFiles :
            os.remove('./temp/' + file)

class PanoAutomator :
    debug = False

    # For now all debug is disabled.
    def __init__(self):
        self.debug = True
        self.AutoTools = AutomatorTools(self.debug, 0)
        self.cwd = os.getcwd()

    # Separate function so I can chage the logging seprate to the main tool (IE: add a prefix to all messages.)
    def log(self, text, dbg=0):
        self.AutoTools.log(text, dbg)

    # This generates the rotation script used by nona and saves it to TepScript.pto so the program can use it. Breakdown below...
    #
    # p f2 w#Width h#Height v360 E0 R0 n"TIFF_m c:NONE r:CROP"
    # This is the output format. #Width and #Height are obtained from the source image (We are just rotating the pre-exsisting image, so this works)
    # m g1 i0 f0 m2 p0.00784314
    # I honestly don't know what this does but I'm too afraid to remove it, so it stays.
    #
    # i w#Width h#Height f4 v360 r#Rotation p#Pitch y#Yaw n".\Logo\360_0162 Auto-CP.1-2.tif"
    # This is the source image values #Width and # Height should be obvious
    # #Rotation, #Pitch, and #Yaw are how the image will be rotated in the final product.
    # (To get both top and bottom of the image visable use 90, 0, 90 repectivly)
    def generate_script(self, mode, filename, Height, Width):
        if mode == 0 :
            # Rotates image so nadir is in the center (Reverses 1)
            script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p90 y0 n"./../Stitched/' + filename +'"'
        elif mode == 1 :
            # Rotates image so top is in the center (Reverses 0)
            script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p-90 y0 n"./../Logo/' + filename +'"'
        #elif mode == 2 :
            # Rotates image so nadir is on the left and top is on the right (Reverses 3)
            #script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p-90 y0 n".\\Logo\\' + filename +'"'
        #elif mode == 3 :
            # Reverses 2
            #script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p-90 y0 n".\\Logo\\' + filename +'"'
        return script

    # Used to split a image in half using ImageMagick, To be upgraded in the near future.
    def autoingest(self):
        inputFiles = self.AutoTools.folderlist('Ingest')
        outputFiles = self.AutoTools.folderlist('Ingested')
        outputFiles = self.AutoTools.namestrip(outputFiles, 1)
        self.log(outputFiles,1)
        todoFiles = list(set(inputFiles) - set(outputFiles))
        self.log(todoFiles, 1)
        processes = set()
        max_processes = 4
        for F in todoFiles :
            self.log('Splitting ' + F + ":\nProssesing Right...")
            FoutR = F[:8] + "R" + F[-4:]
            FoutL = F[:8] + "L" + F[-4:]
            # Offset of half the image
            # TODO: Make a option for this read the image dimennsions from the metadata using PIL
            args = 'convert "' + self.AutoTools.sanitize_dir('./Ingest/' + F) + '"' + " -crop 3888x3888+0+0 " +'"' + self.AutoTools.sanitize_dir('./Ingested/' + FoutR) + '"'
            self.AutoTools.command(args)
            self.log('Prossesing Left...')
            # Image full size is 7776 wide and 3888 tall. (easy right?)
            args = 'convert "' + self.AutoTools.sanitize_dir('./Ingest/' + F) + '"' + " -crop 3888x3888+3888+0 " +'"' + self.AutoTools.sanitize_dir('./Ingested/' + FoutL) + '"'
            self.AutoTools.command(args)
        self.AutoTools.processesWait(0)
        self.log('All files split.')

    # This rotates the panorama you made so you can edit the Nadir
    def autoRotateToNadir(self):
        inputFiles = self.AutoTools.folderlist('Stitched')
        inputFiles2 = self.AutoTools.namestrip(inputFiles, 4)
        outputFiles = self.AutoTools.folderlist('Nadir')
        todoFiles = list(set(inputFiles2) - set(outputFiles))
        start = time.time()
        for F in todoFiles :
            self.log('Processing image ' + F + ' information...')
            origWidth, origHeight = Image.open("./Stitched/" + F).size
            origHeight = str(origHeight)
            origWidth = str(origWidth)
            scriptText = self.generate_script(0,F,origHeight,origWidth)
            # We now write the script in the function so we *should* never have them end up in diffrent places.
            filename = self.AutoTools.tempFile(scriptText, 'pto')
            self.log("Image info obtained. Rotating...")
            args ='nona -o "' + './Nadir/' + F + '" "' + './temp/' + filename + '"'
            self.AutoTools.command(args)
        self.AutoTools.processesWait(0)
        self.AutoTools.prugeTemps()
        end = time.time()
        print("!! IMPORTANT !! : " + str(end - start))
        self.remove0000('Nadir')

    # This removes the 0000.tif that is automaitcally added to the files when rotated
    # Might want to move into namestrip (Since it is kinda striping the end of the name.)
    def remove0000(self, Folder):
        print('Renaming files so there is not a 0000.tif at the end')
        files = self.AutoTools.folderlist(Folder)
        for F in files:
            if F[-8:] == '0000.tif':
                newname = F.replace('0000.tif', '')
                os.rename('./' + Folder + '/' + F,'./' + Folder + '/' + newname)
        print('Files renamed.')

    # This adds the logo to the bottom of the image.
    # It only works well if the logo will cover the *pod / Nadir and the *pod / Nadir is actually at the very bottom.
    def addLogo(self, LogoFile):
        self.log('Adding logos...')
        inputFiles = self.AutoTools.folderlist('Nadir')
        outputFiles = self.AutoTools.folderlist('Logo')
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Adding logo to center of ' + F + " ... ")
            self.AutoTools.command('convert -quiet ".\\Nadir\\' + F + '" ".\\Logos\\' + LogoFile + '" -gravity center -composite -matte ".\\Logo\\' + F + '"')
        self.log("Remember to check if the logo was positioned correctly, you may have to re-do one or two images...")

    # This rotates the image after the logo is added.
    def autoRotateFromNadir(self):
        inputFiles = self.AutoTools.folderlist('Logo')
        outputFiles = self.AutoTools.folderlist('Final\\tif')
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Processing image ' + F + ' information...')
            origWidth, origHeight = Image.open(os.getcwd() + "\\Logo\\" + F).size
            origHeight = str(origHeight)
            origWidth = str(origWidth)
            scriptText = self.generate_script(1,F,origHeight,origWidth)
            self.AutoTools.tempFile(scriptText, 'TempScript.pto')
            self.log("Image info obtained. Rotating...")
            self.AutoTools.command('nona -o ".\\Final\\tif\\' + F + '" .\\TempScript.pto')
            self.log('Image ' + F + ' Rotated.')
        self.remove0000('Final\\tif')

    # This converts the final tif file into a final jpg file.
    # This is b/c I don't feel like re-writing the rotation function to *also* change the file format.
    def convert(self):
        inputFiles = self.AutoTools.folderlist('Final\\tif')
        outputFiles = self.AutoTools.folderlist('Final\\jpg')
        inputFiles2 = self.AutoTools.namestrip(inputFiles, 2)
        outputFiles2 = self.AutoTools.namestrip(outputFiles, 3)
        todoFiles = list(set(inputFiles2) - set(outputFiles2))
        for F in todoFiles :
            self.log('Converting ' + F + " to .JPG ... ")
            # REMEMBER TO ADD ON THE FILE EXTENSIONS, THE LIST IS MISSING THEM!
            self.AutoTools.command('convert -quiet ".\\Final\\tif\\' + F + '.tif" ".\\final\\jpg\\' + F + '.jpg"')
        self.log("All Converts Complete...")

# This just calls all the functions in order, I will eventually make a menu for this but for now, here you are.
#Let's see if the new object works...
PA = PanoAutomator()
PA.autoingest()
PA.autoRotateToNadir()
# You can change what the logo file name is here, I don't remember if I ever fixed the bug where you can't have spaces or not...
#PA.addLogo('Advanced_Nadir_small.tif')
#PA.autoRotateFromNadir()
#PA.convert()
# This is for if you just click on the program and it actually runs. (So it dosent just close out.) The wrapper is B/C I was debugging it and am still doing so.
input("Press enter to close")