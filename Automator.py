#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
#-------------------------------------------------------------------------------

# Import all the stuff
import os
# REMEMBER PIL WILL NOT FUNCTION CORRECTLY IF YOU SAVE AS 16 BIT .TIF!
from PIL import Image

class PanoAutomator :
    # Runs a command, if this breaks, I don't want to go looking for all of the calls.
    def command(self, cmd, dbg=0):
        if dbg == 1:
            self.log(cmd, 1)
        os.system(cmd)

    # Dysplays text to the user. Later if I ever add a gui this will become the text log function.
    def log(self, text, dbg=0):
        if dbg == 1:
            print("DEBUG: ", end='')
        print(text)

    def folderlist(self, foldername):
        dirname = './' + foldername
        return([f for f in os.listdir(dirname)])

    # Name stripping finction V2,
    def namestrip(self, data, mode=0):
        if mode == 0:
            return(data[:8] + '.JPG')
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
                s3 = s2.replace('.tif', '')
                o.append(s3)
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
            script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p90 y0 n".\\Stitched\\' + filename +'"'
        elif mode == 1 :
            script = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p-90 y0 n".\\Logo\\' + filename +'"'
        return script

    # File Saver
    # This is used so we can arbatrarally save files reletave to the program.
    # Eventually this will be replaced with a temporarry file interface where it returns the full path of the tempfile.
    def tempFile(self, data, filename):
        wr = open('.\\' + filename, 'w')
        wr.write(data)


    # Used to split a image in half using ImageMagick, To be upgraded in the near future.
    def autoingest(self):
        inputFiles = self.folderlist('Ingest')
        outputFiles = self.folderlist('Ingested')
        outputFiles = self.namestrip(outputFiles, 1)
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Splitting ' + F + "\nProssesing Right...")
            FoutR = F[:8] + "R" + '.TIF'
            FoutL = F[:8] + "L" + '.JPG'
            # Offset of half the image
            # TODO: Make a option for this read the image dimennsions from the metadata using PIL
            self.command('convert "./Ingest/' + F + '" -crop 3888x3888+3888+0 "./Ingested/' + FoutR + '"')
            self.log('Right done...\nProssesing Left')
            # Image full size is 7776 wide and 3888 tall. (easy right?)
            self.command('convert "./Ingest/' + F + '" -crop 3888x3888+0+0 "./Ingested/' + FoutL + '"')
            self.log('Left done...')
        self.log('All files done')

    # This rotates the panorama you made so you can edit the Nadir
    def autoRotateToNadir(self):
        inputFiles = self.folderlist('Stitched')
        inputFiles2 = self.namestrip(inputFiles, 4)
        outputFiles = self.folderlist('Nadir')
        todoFiles = list(set(inputFiles2) - set(outputFiles))
        for F in todoFiles :
            self.log('Processing image ' + F + ' information...')
            origWidth, origHeight = Image.open(os.getcwd() + "\\Stitched\\" + F).size
            origHeight = str(origHeight)
            origWidth = str(origWidth)
            scriptText = self.generate_script(0,F,origHeight,origWidth)
            # We now write the script in the function so we *should* never have them end up in diffrent places.
            self.tempFile(scriptText, 'TempScript.pto')
            self.log("Image info obtained. Rotating...")
            self.command('nona -o ".\\Nadir\\' + F + '" .\\TempScript.pto')
            self.log('Image ' + F + ' Rotated.')
        self.remove0000('Nadir')

    # This removes the 0000.tif that is automaitcally added to the files when rotated
    # Might want to move into namestrip (Since it is kinda striping the end of the name.)
    def remove0000(self, Folder):
        print('Renaming files so there is not a 0000.tif at the end')
        files = folderlist(Folder)
        for F in files:
            if F[-8:] == '0000.tif':
                newname = F.replace('0000.tif', '')
                os.rename('.\\' + Folder + '\\' + F,'.\\' + Folder + '\\' + newname)
        print('Files renamed.')

    # This adds the logo to the bottom of the image.
    # It only works well if the logo will cover the *pod / Nadir and the *pod / Nadir is actually at the very bottom.
    def addLogo(self, LogoFile):
        self.log('Adding logos...')
        inputFiles = self.folderlist('Nadir')
        outputFiles = self.folderlist('Logo')
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Adding logo to center of ' + F + " ... ")
            self.command('convert -quiet ".\\Nadir\\' + F + '" ".\\Logos\\' + LogoFile + '" -gravity center -composite -matte ".\\Logo\\' + F + '"')
        self.log("Remember to check if the logo was positioned correctly, you may have to re-do one or two images...")

    # This rotates the image after the logo is added.
    def autoRotateFromNadir(self):
        inputFiles = self.folderlist('Logo')
        outputFiles = self.folderlist('Final\\tif')
        todoFiles = list(set(inputFiles) - set(outputFiles))
        for F in todoFiles :
            self.log('Processing image ' + F + ' information...')
            origWidth, origHeight = Image.open(os.getcwd() + "\\Logo\\" + F).size
            origHeight = str(origHeight)
            origWidth = str(origWidth)
            scriptText = self.generate_script(1,F,origHeight,origWidth)
            self.tempFile(scriptText, 'TempScript.pto')
            self.log("Image info obtained. Rotating...")
            self.command('nona -o ".\\Final\\tif\\' + F + '" .\\TempScript.pto')
            self.log('Image ' + F + ' Rotated.')
        self.remove0000('Final\\tif')

    # This converts the final tif file into a final jpg file.
    # This is b/c I don't feel like re-writing the rotation function to *also* change the file format.
    def convert(self):
        inputFiles = self.folderlist('Final\\tif')
        outputFiles = self.folderlist('Final\\jpg')
        inputFiles2 = self.namestrip(inputFiles, 2)
        outputFiles2 = self.namestrip(outputFiles, 3)
        todoFiles = list(set(inputFiles2) - set(outputFiles2))
        for F in todoFiles :
            self.log('Converting ' + F + " to .JPG ... ")
            # REMEMBER TO ADD ON THE FILE EXTENSIONS, THE LIST IS MISSING THEM!
            self.command('convert -quiet ".\\Final\\tif\\' + F + '.tif" ".\\final\\jpg\\' + F + '.jpg"')
        self.log("All Converts Complete...")

# This just calls all the functions in order, I will eventually make a menu for this but for now, here you are.
#Let's see if the new object works...
PA = PanoAutomator()
PA.autoingest()
PA.autoRotateToNadir()
# You can change what the logo file name is here, I don't remember if I ever fixed the bug where you can't have spaces or not...
PA.addLogo('Advanced_Nadir_small.tif')
PA.autoRotateFromNadir()
PA.convert()
# This is for if you just click on the program and it actually runs. (So it dosent just close out.) The wrapper is B/C I was debugging it and am still doing so.
input("Press enter to close")