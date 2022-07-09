# How to use

1. Install [OBS-VirtualCam](https://github.com/Fenrirthviti/obs-virtual-cam/releases) and enable it.
2. Run this program and from settings select "OBS-Camera" as the video device.
3. Crop if you have other stuff around the game, protip: -/+ to resize the window.
4. Calibrate template scale, this takes a little bit.
5. Test if the last Val text is detected, if yes skip to step: 9
6. Record a statue run
7. Save a frame directly from the recording, that has the last Val text on screen (for example VLC lets you to save currect frame under the "Video" menu)
8. Open the image in editor of your choice and then crop the image, make everything else transparent but the text and save the image as templateimageYOURTEXTHERE.png to the data folder.
9.  Fiddle with the settings, set the delay and leave timing adjustment to your liking, match the max fps with the video feed fps.
10. Play & enjoy perfect val leaves everytime.

# Cropping
Cropping works by selecting two points which create a rectangle. Left click for point 1 and right click for point 2. Space Confirms selection. R to reset the selection. -/+ to scale the window.

# Calibration
Play statue until the Valentin last message is visible on screen and then press space. Calibration does multi-scale template matching using all the provided template images (You can add more to data folder, needs to have templateimage in the beginning of the file name). For best results provide template image taken from your capture setup. Matching value 0.9 or better should be good enough.