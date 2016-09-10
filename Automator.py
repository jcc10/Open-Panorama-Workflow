#-------------------------------------------------------------------------------
# Name:        Panorama Automation Tool
# Purpose:     To automate the editing of panoramas.
#              This was made for windows, your main issue will be with slashes.
#-------------------------------------------------------------------------------

# Import the actual tool
import Code

# This just calls all the functions in order, I will eventually make a menu for this but for now, here you are.
#Let's see if the new object works...
PA = Code.PanoAutomator()
PA.splitLeftRight('Ingest', 'Ingested')
PA.rotateEquirectangular('Stitched', 'Nadir', 0, 90, 0)
# You can change what the logo file name is here, I don't remember if I ever fixed the bug where you can't have spaces or not...
PA.addLogo('Advanced_Nadir_small.tif')
PA.rotateEquirectangular('Logo', 'Final/tif', 0, -90, 0)
PA.convert()
# This is for if you just click on the program and it actually runs. (So it dosent just close out.) The wrapper is B/C I was debugging it and am still doing so.
input("Press enter to close")