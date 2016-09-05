#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
#-------------------------------------------------------------------------------

# Import all the stuff
import os
# REMEMBER PIL WILL NOT FUNCTION CORRECTLY IF YOU SAVE AS 16 BIT .TIF!
from PIL import Image

# This lists all the files in the folder. Just made for convenince.
def folderlist(foldername):
    dirname = '.\\' + foldername
    return([f for f in os.listdir(dirname)])

# Originally meant to strip names, it became so much more
def namestrip(data, mode=0):
    if mode == 0 :
        # Gets the first 8 characters and adds a .JPG to the end of the file name
        return(data[:8] + '.JPG')
    if mode == 1 :
        # Used to remove the R or L in the ingested folder list. Also ensures you don't have duplicates.
        o = []
        for s in data:
            s2 = namestrip(s, 0)
            if s2 in o:
                None
            else:
                o.append(s2)
            None
        return o
    if mode == 2 :
        # Strips .tif file extensions.
        o = []
        for s in data:
            s3 = s2.replace('.tif', '')
            o.append(s3)
            # Returns the list WITH NO EXTENSIONS remember to add them back on
        return o
    if mode == 3 :
        o = []
        for s in data:
            # Strips .jpg file extensions
            s2 = s.replace('.jpg', '')
            s3 = s2.replace('.jpeg', '')
            o.append(s3)
            # Returns the list WITH NO EXTENSIONS remember to add them back on
        return o
    if mode == 4 :
        # Just incase you save your project file in the stitched directory.
        o = []
        for s in data:
            if s[-4:] == '.pts':
                None
            else:
                o.append(s)
        return o


# this splits the image into two halfs
def autoingest():
    inputFiles = folderlist('Ingest')
    outputFiles = folderlist('Ingested')
    outputFiles = namestrip(outputFiles, 1)
    todoFiles = list(set(inputFiles) - set(outputFiles))
    for F in todoFiles :
        print('Splitting ' + F + "\nProssesing Right...")
        FoutR = F[:8] + "R" + '.JPG'
        FoutL = F[:8] + "L" + '.JPG'
        # Offset of half the image
        os.system('convert "./Ingest/' + F + '" -crop 3888x3888+3888+0 "./Ingested/' + FoutR + '"')
        print('Right done...\nProssesing Left')
        # Image full size is 7776 wide and 3888 tall. (easy right?)
        os.system('convert "./Ingest/' + F + '" -crop 3888x3888+0+0 "./Ingested/' + FoutL + '"')
        print('Left done...')
    print('All files done')

# This rotates the panorama you made so you can edit the Nadir
def autoRotateToNadir():
    inputFiles = folderlist('Stitched')
    inputFiles2 = namestrip(inputFiles, 4)
    outputFiles = folderlist('Nadir')
    todoFiles = list(set(inputFiles2) - set(outputFiles))
    for F in todoFiles :
        print('Processing image ' + F + ' information...')
        origWidth, origHeight = Image.open(os.getcwd() + "\\Stitched\\" + F).size
        origHeight = str(origHeight)
        origWidth = str(origWidth)
        generate_script(0,F,origHeight,origWidth)
        print("Image info obtained. Rotating...")
        os.system('nona -o ".\\Nadir\\' + F + '" .\\TempScript.pto')
        print('Image ' + F + ' Rotated.')
    remove0000('Nadir')

# This removes the 0000.tif that is automaitcally added to the files when rotated
def remove0000(Folder):
    print('Renaming files so there is not a 0000.tif at the end')
    files = folderlist(Folder)
    for F in files:
        if F[-8:] == '0000.tif':
            newname = F.replace('0000.tif', '')
            os.rename('.\\' + Folder + '\\' + F,'.\\' + Folder + '\\' + newname)
    print('Files renamed.')

# This adds the logo, it does not always work correctly due to alignment issues.
def addLogo(LogoFile):
    print('Adding logos...')
    inputFiles = folderlist('Nadir')
    outputFiles = folderlist('Logo')
    todoFiles = list(set(inputFiles) - set(outputFiles))
    for F in todoFiles :
        print('Adding logo to center of ' + F + " ... ")
        os.system('convert -quiet ".\\Nadir\\' + F + '" ".\\Logos\\' + LogoFile + '" -gravity center -composite -matte ".\\Logo\\' + F + '"')
    print("Remember to check if the logo was positioned correctly, you may have to re-do one or two images...")

# This rotates the image after the logo is added.
def autoRotateFromNadir():
    inputFiles = folderlist('Logo')
    outputFiles = folderlist('Final\\tif')
    todoFiles = list(set(inputFiles) - set(outputFiles))
    for F in todoFiles :
        print('Processing image ' + F + ' information...')
        origWidth, origHeight = Image.open(os.getcwd() + "\\Logo\\" + F).size
        origHeight = str(origHeight)
        origWidth = str(origWidth)
        generate_script(1,F,origHeight,origWidth)
        print("Image info obtained. Rotating...")
        os.system('nona -o ".\\Final\\tif\\' + F + '" .\\TempScript.pto')
        print('Image ' + F + ' Rotated.')
    remove0000('Final\\tif')

# This converts the final tif file into a final jpg file.
# This is b/c I don't feel like re-writing the rotation function to *also* change the file format.
def convert():
    inputFiles = folderlist('Final\\tif')
    outputFiles = folderlist('Final\\jpg')
    inputFiles2 = namestrip(inputFiles, 2)
    outputFiles2 = namestrip(outputFiles, 3)
    todoFiles = list(set(inputFiles2) - set(outputFiles2))
    for F in todoFiles :
        print('Converting ' + F + " to .JPG ... ")
        # REMEMBER TO ADD ON THE FILE EXTENSIONS, THE LIST IS MISSING THEM!
        os.system('convert -quiet ".\\Final\\tif\\' + F + '.tif" ".\\final\\jpg\\' + F + '.jpg"')
    print("All Converts Complete...")

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
def generate_script(mode, filename, Height, Width):
    if mode == 0 :
        text = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p90 y0 n".\\Stitched\\' + filename +'"'
    elif mode == 1 :
        text = 'p f2 w' + Width + ' h' + Height + ' v360 E0 R0 n"TIFF_m c:NONE r:CROP"\nm g1 i0 f0 m2 p0.00784314\n\ni w' + Width + ' h' + Height + ' f4 v360 r0 p-90 y0 n".\\Logo\\' + filename +'"'
    wr = open('.\\TempScript.pto', 'w')
    wr.write(text)


# This just calls all the functions in order, I will eventually make a menu for this but for now, here you are.
autoingest()
autoRotateToNadir()
# You can change what the logo file name is here, I don't remember if I ever fixed the bug where you can't have spaces or not...
addLogo('Advanced_Nadir_small.tif')
autoRotateFromNadir()
convert()
# This is for if you just click on the program and it actually runs. (So it dosent just close out.) The wrapper is B/C I was debugging it and am still doing so.
input("Press enter to close")