#!/usr/bin/env python3
import cv2
import numpy as np
import argparse
import time
import io
import os
import re

# Base folder for snapshots
base_folder = "snapshots"
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# Function to create a new session folder dynamically
def get_new_session_folder(base_folder):
    existing = os.listdir(base_folder)
    session_nums = []
    pattern = re.compile(r"session_(\d+)")
    for name in existing:
        match = pattern.match(name)
        if match:
            session_nums.append(int(match.group(1)))
    next_num = max(session_nums, default=-1) + 1
    new_folder = os.path.join(base_folder, f"session_{next_num}")
    os.makedirs(new_folder)
    return new_folder

# Create a new session folder and log file
snapshot_folder = get_new_session_folder(base_folder)
log_file_path = os.path.join(snapshot_folder, "snapshot_log.txt")
print(f"[INFO] Saving snapshots in: {snapshot_folder}")
print(f"[INFO] Log file: {log_file_path}")

snapshot_index = 1  # Initialize the snapshot index

# Function to take a snapshot and log the data
def snapshot(heatmap, maxtemp):
    global snapshot_index
    now = time.strftime("%Y%m%d-%H%M%S") 
    snaptime = time.strftime("%H:%M:%S")
    snapshot_name = f"img{snapshot_index}.png"
    snapshot_path = os.path.join(snapshot_folder, snapshot_name)
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{snapshot_index}, {snapshot_name}, {maxtemp} C\n")
    snapshot_index += 1
    cv2.imwrite(snapshot_path, heatmap)
    return snaptime

# Initialize video capture and other settings
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

isPi = is_raspberrypi()

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=2, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()

if args.device:
    dev = args.device
else:
    dev = 0

cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
if isPi == True:
    cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
else:
    cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)

# General settings
width = 256
height = 192
scale = 3
newWidth = width * scale
newHeight = height * scale
alpha = 1.0
colormap = 0
dispFullscreen = False
cv2.namedWindow('Thermal', cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', newWidth, newHeight)
rad = 0
threshold = 2
hud = True
recording = False
last_snapshot_time = None

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        imdata, thdata = np.array_split(frame, 2)
        lomax = thdata[..., 1].max()
        posmax = thdata[..., 1].argmax()
        mcol, mrow = divmod(posmax, width)
        himax = thdata[mcol][mrow][0]
        lomax = lomax * 256
        maxtemp = himax + lomax
        maxtemp = (maxtemp / 64) - 273.15
        maxtemp = round(maxtemp, 2)

        bgr = cv2.cvtColor(imdata, cv2.COLOR_YUV2BGR_YUYV)
        bgr = cv2.convertScaleAbs(bgr, alpha=alpha)
        bgr = cv2.resize(bgr, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)
        if rad > 0:
            bgr = cv2.blur(bgr, (rad, rad))

        heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)

        # # Draw crosshairs
        # cv2.line(heatmap, (int(newWidth / 2), int(newHeight / 2) + 20),
        #          (int(newWidth / 2), int(newHeight / 2) - 20), (255, 255, 255), 2)  # Vertical line
        # cv2.line(heatmap, (int(newWidth / 2) + 20, int(newHeight / 2)),
        #          (int(newWidth / 2) - 20, int(newHeight / 2)), (255, 255, 255), 2)  # Horizontal line

        # Display floating max temp
        if maxtemp > threshold:
            cv2.circle(heatmap, (mrow * scale, mcol * scale), 5, (0, 0, 0), 2)
            cv2.circle(heatmap, (mrow * scale, mcol * scale), 5, (0, 0, 255), -1)
            cv2.putText(heatmap, str(maxtemp) + ' C', ((mrow * scale) + 10, (mcol * scale) + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(heatmap, str(maxtemp) + ' C', ((mrow * scale) + 10, (mcol * scale) + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('Thermal', heatmap)

        if last_snapshot_time is None:
            last_snapshot_time = time.time()

        current_time = time.time()
        '''
        if current_time - last_snapshot_time >= 5:
            snaptime = snapshot(heatmap, maxtemp)
            last_snapshot_time = current_time
        '''
        keyPress = cv2.waitKey(1)
        if keyPress == ord('p'):  # Take a manual snapshot
            snaptime = snapshot(heatmap, maxtemp)
        if keyPress == ord('q'):  # Quit
            break

cap.release()
cv2.destroyAllWindows()