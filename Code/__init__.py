#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
#-------------------------------------------------------------------------------

# Import all the stuff
import os
# REMEMBER PIL WILL NOT FUNCTION CORRECTLY IF YOU SAVE AS 16 BIT .TIF!
from PIL import Image
# Import Custom Tools
import __Toolkit__

class PanoAutomator :

    # For now all debug is disabled.
    def __init__(self):
        self.debug = False
        self.AutoTools = __Toolkit__.AutomatorTools(self.debug, 5)
        self.cwd = os.getcwd()

    # Separate function so I can chage the logging seprate to the main tool (IE: add a prefix to all messages.)
    def log(self, text, dbg=0):
        self.AutoTools.log(text, dbg)

    # This generates the rotation script used by nona and returns the text. Breakdown below...
    #
    # p f2 w#Width h#Height v360 E0 R0 n"TIFF_m c:NONE r:CROP"
    # This is the output format. #Width and #Height are obtained from the source image (We are just rotating the pre-exsisting image, so this works)
    # m g1 i0 f0 m2 p0.00784314
    # I honestly don't know what this does but I'm too afraid to remove it, so it stays.
    #
    # i w#Width h#Height f4 v360 r#Roll p#Pitch y#Yaw n"#SourceImage"
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

    # Advanced version of the generate script option, this one has dynamic roll values.
    # This is to replace the old generate Script version. This one is more dynamic.
    # TODO: Add more output format optons, Add more input options.
    #
    # p f2 w#Width h#Height v360 E0 R0 n"TIFF_m c:NONE r:CROP"
    # This is the output format. #Width and #Height are obtained from the source image (We are just rotating the pre-exsisting image, so this works)
    # m g1 i0 f0 m2 p0.00784314
    # I honestly don't know what this does but I'm too afraid to remove it, so it stays.
    #
    # i w#Width h#Height f4 v360 r#Roll p#Pitch y#Yaw n"#SourceImage"
    # This is the source image values #Width and # Height should be obvious
    # #Rotation, #Pitch, and #Yaw are how the image will be rotated in the final product.
    def __generateScript__(self, filenameInput, Height, Width, Roll, Pitch, Yaw) :
        script = 'p f2 w' + str(Width) + ' h' + str(Height) + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\n'
        script = script + 'm g1 i0 f0 m2 p0.00784314\n\n'
        script = script + 'i w' + str(Width) + ' h' + str(Height) + ' f4 v360 r' + str(Roll) + ' p' + str(Pitch) + ' y' + str(Yaw) + ' n"./../' + filenameInput +'"'
        return script

    # Used to split a image in half using ImageMagick, To be upgraded in the near future.
    def splitLeftRight(self, FolderIN, FolderOUT):
        inputFiles = self.AutoTools.folderlist(FolderIN)
        outputFiles = self.AutoTools.folderlist(FolderOUT)
        outputFiles = self.AutoTools.namestrip(outputFiles, 1)
        todoFiles = list(set(inputFiles) - set(outputFiles))
        processes = set()
        for F in todoFiles :
            # Now reads image metadata to get the dimensions.
            origWidth, origHeight = Image.open("./Ingest/" + F).size
            if (origWidth == (origHeight * 2)):
                origHeight = str(origHeight)
                origWidth = str(origWidth)
                self.log('Splitting ' + F + ":\nProssesing Right...")
                FoutR = F[:8] + "R" + F[-4:]
                FoutL = F[:8] + "L" + F[-4:]
                crop = origHeight + 'x' + origHeight + '+0+0'
                args = 'convert "' + './Ingest/' + F + '" -crop ' + crop + ' "' + './' + FolderIN + '/' + FoutR + '"'
                self.AutoTools.command(args)
                self.log('Prossesing Left...')
                # Offset of half the image
                crop = origHeight + 'x' + origHeight + '+' + origHeight + '+0'
                args = 'convert "' + './Ingest/' + F + '" -crop ' + crop + ' "' + './' + FolderOUT + '/' + FoutL + '"'
                self.AutoTools.command(args)
            else:
                self.log("Image '" + F + "' is not 2:1 aspect ratio, Skipping.")
        self.AutoTools.processesWait(0)
        self.log('All files split.')

    def rotateEquirectangular(self, FolderIN, FolderOut, Roll, Pitch, Yaw):
        inputFiles = self.AutoTools.folderlist(FolderIN)
        inputFiles2 = self.AutoTools.namestrip(inputFiles, 4)
        outputFiles = self.AutoTools.folderlist(FolderOut)
        todoFiles = list(set(inputFiles2) - set(outputFiles))
        for F in todoFiles :
            self.log('Processing image ' + F + ' information...')
            FQURI = "./" + FolderIN + "/" + F
            origWidth, origHeight = Image.open(FQURI).size
            origHeight = str(origHeight)
            origWidth = str(origWidth)
            scriptText = self.__generateScript__(FQURI, origHeight, origWidth, Roll, Pitch, Yaw)
            # We now write the script in the function so we *should* never have them end up in diffrent places.
            filename = self.AutoTools.tempFile(scriptText, 'pto')
            self.log("Image info obtained. Rotating...")
            args ='nona -o "' + './' + FolderOut + '/' + F + '" "./temp/' + filename + '"'
            self.AutoTools.command(args)
        self.AutoTools.processesWait(0)
        self.AutoTools.prugeTemps()
        self.remove0000(FolderOut)

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
    def addLogo(self, FolderIN, FolderOUT, LogoFile):
        self.log('Adding logos...')
        inputFiles = self.AutoTools.folderlist(FolderIN)
        outputFiles = self.AutoTools.folderlist(FolderOUT)
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Adding logo to center of ' + F + " ... ")
            args ='convert -quiet "./' + FolderIN + '/' + F + '" "./Logos/' + LogoFile + '" -gravity center -composite -matte "./' + FolderOUT + '/' + F + '"'
            self.AutoTools.command(args)
        self.log("Remember to check if the logo was positioned correctly, you may have to re-do one or two images...")

    # This converts the final tif file into a final jpg file.
    # This is b/c I don't feel like re-writing the rotation function to *also* change the file format.
    def convert(self, FolderIN, ExtensionIN, FolderOUT, ExtensionOUT):
        inputFiles = self.AutoTools.folderlist(FolderIN)
        outputFiles = self.AutoTools.folderlist(FolderOUT)
        inputFiles2 = self.AutoTools.namestrip(inputFiles, 2)
        outputFiles2 = self.AutoTools.namestrip(outputFiles, 3)
        todoFiles = list(set(inputFiles2) - set(outputFiles2))
        for F in todoFiles :
            self.log('Converting ' + F + " to ." + ExtensionOUT + " ... ")
            # REMEMBER TO ADD ON THE FILE EXTENSIONS, THE LIST IS MISSING THEM!
            args = 'convert -quiet "./' + FolderIN + '/' + F + '.' + ExtensionIN + '" "./' + FolderOUT + '/' + F + '.' + ExtensionOUT + '"'
            self.AutoTools.command(args)
        self.log("All Converts Complete...")