# How to use

1. Install [OBS-VirtualCam](https://github.com/Fenrirthviti/obs-virtual-cam/releases) and enable it.
2. Run this program and from settings select "OBS-Camera" as the video device.
3. Set the OBS output resolution to match with your actual OBS output resolution.
4. Crop if you have other stuff around the game, protip: -/+ to resize the window.
5. Calibrate template scale, this takes a little bit.
6. Test if the last Val text is detected, if yes skip to step: 10
7. Record a statue run
8. Save a frame directly from the recording, that has the last Val text on screen (for example VLC lets you to save currect frame under the "Video" menu)
9. Open the image in editor of your choice and then crop the image, make everything else transparent but the text and save the image as templateimageYOURTEXTHERE.png to the data folder.
10. Fiddle with the settings, set the delay and leave timing adjustment to your liking, match the max fps with the video feed fps.
11. Play & enjoy perfect val leaves everytime.

# Cropping
Cropping works by selecting two points which create a rectangle. Left click for point 1 and right click for point 2. Space Confirms selection. Esc and C cancel the selection and no cropping is applied. -/+ to scale the window.

# Calibration
Play statue until the Valentin last message is visible on screen and then press space. Calibration does multi-scale template matching using all the provided template images (You can add more to data folder, needs to have templateimage in the beginning of the file name). For best results provide template image taken from your capture setup. Matching value 0.9 or better should be good enough.