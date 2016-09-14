#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
#-------------------------------------------------------------------------------

# Import the actual tool
import Code

# This just calls all the functions in order, I will eventually make a menu for this but for now, here you are.
FileExtentions = ["jpg","jpeg","png","tif","tiff"]
# File Extentions that will get prosessed, if it's not on this list it won't even get to the file splitters.
logLevel = 2
# Log Levels
# 0 = Silent, No text whats so ever
#     Eventually this will also surpress errors.
# 1 = Shows Every section it's prosessing
# 2 = Shows Every file it's prosessing
# 3 = Shows Every major step in the file it's prossesing
# 4 = Reserved for future use, acts like 3
# 5 = Shows Debug Text
PA = Code.PanoAutomator(0)
PA.splitLeftRight('Ingest', 'Ingested')
# Rotate the image so the nadir is in the center
PA.rotateEquirectangular('Stitched', 'Nadir', 0, 90, 0)
# You can change what the logo file name is here, I don't remember if I ever fixed the bug where you can't have spaces or not...
PA.addLogo('Nadir', 'Logo', 'Advanced_Nadir_small.tif')
# Rotate the image so the nadir we moved to the center is back where it belongs (@ the bottom).
PA.rotateEquirectangular('Logo', 'Final/tif', 0, -90, 0)
PA.convert('Final/tif', 'tif', 'Final/jpg', 'jpg')
# This is for if you just click on the program and it actually runs. (So it dosent just close out.) The wrapper is B/C I was debugging it and am still doing so.
if logLevel >= 1 :
    input("Press enter to close")
else:
    None