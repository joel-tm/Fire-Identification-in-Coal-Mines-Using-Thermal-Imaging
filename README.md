# Fire-ldentification-in-Coal-Mines-Using-Thermal-Imaging
uses topdon tc001 thermal camera


The code can be run in ubuntu directly with camera connected to the laptops usb port or connect the camera to the raspberry pi and use rnc viewer to execute this code inside it

## step 1
### IN UBUNTU 
- after the camera is connected. check if its getting detected in the system by using following command
  `v4l2-ctl --list-devices`

  you should get something like this
  `USB Camera: USB Camera (usb-0000:00:14.0-1):
	/dev/video2
	/dev/video3
	/dev/media1`

`python3 snapshot4.py` directly from terminal. or python3 snapshot4.py --device {find the number its getting detected as and put it here}

#### running snapshot4.py
- should give you a live feed from the camera with the maximum temperature displayed on it.
- currently it is set to manually take a snapshot when you press 'p' in keyboard.
This can be made to take a snapshot at every time interaval you decide

- when the snapshots are taken it is always started in a new folder named session{no}. Inside the session{no} the snapshots are saved along with log file containing the image number and temperature associated with it

### IF RUNNING IN RASPBERRY PI OS(via hdmi or remotely using rnc viewer)

- install opencv
- run directly from the cmd in pi always mention the device no of the camera while running eg: python3 snapshot4.py --device 0

## STEP 2
### run ic3.py
Make sure to change the session_{no} in the file.
run the file named ic3.py. 
eg in code:
```python
# Configss
image_folder = './snapshots/session_31'   # Change this to your image directory
log_file = './snapshots/session_31/snapshot_log.txt'
```

successfully running this image will create a grid with images produced
output from running this shown below!
![ic3grid_combined_grid](https://github.com/user-attachments/assets/6a8e474d-7181-4b95-a3ac-b09bd13ffdf8)


- the images that are set the above threshold value are marked with caution along with their temperature in red
-  below threshold are given in green

