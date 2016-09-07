Welcome to the Open Panorama Workflow!

The aim of this kit is to assist you in working with 360 cameras and panoramas in a Amature or Professional method. This kit includes a script (Automator.py) that can do the following:

  * Split images in half for ingesting most 360 cameras raw photos
  * Rotate stitched panoramas so the Nadir is visible
  * Add a logo to the center of a nadir images (You may sometimes wish to do this manually)
  * Rotate a image that has a logo in the center so it returns to the Nadir
  * Convert the un-compressed images to .jpg format for uploading or re-converting.
  
Please note that the script expects the stitched images to be a 8 Bit .tif file. Any other file and IT WILL BREAK. We will eventually work on that.

Requirements:

  * Python3 (This program was writen for python 3.4)
  * Pillow (Get this through PIP the python package manager)
  * Hugin (This provides the nona program, the nona program must be in the system path for now)
  * ImageMagick (Again, must be in the system path for now)

Recomended partner programs:

  * GIMP 2 (Image editor, High end.)
  * Paint.Net (Image editor, Fast editor, Simple edits.)
  * ptGui (Expensive, but very good at what it does.)
  * Hugin (Free version of ptGui, havent tried it yet.)
  
How to use:

Dump raw images that need to be split down the middle (as in a left lens and a right lens) from a gear 360 format into the ingest folder.  
This will output into the Ingested folder.  
(Image must be 7776 pixels wide and 3888 pixels tall or stuff will break, will fix soon)

Put your final stitched images into the sitiched folder (or just put all stitched images into the stitched folder)  
Expected size is ~(7200x3600) it must be a 2:1 image though.  
All images in the sitiched folder will then:

  * Be rotated so the Nadir is in the center.
  * Have a logo added to the center of the previous edit.
  * Be rotated so it is normal again.
  * Be converted to .jpg format.
  
Between each step a copy will be saved, if you edit the copy and save under a diffrent name it will prosess that image like it would a auto-generated image. (This is usefull for the logo adder since the tripod may not be in the exact nadir)

The logo is in the logos folder. Included is a template file for editing. (It also has paths so you can stroke the circle or make it into a selection.)
