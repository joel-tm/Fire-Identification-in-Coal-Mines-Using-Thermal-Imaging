import cv2
import numpy as np
import os
import glob

# Function to ensure images have the same height by padding
def resize_to_same_height(images):
    # Get the maximum height
    max_height = max(img.shape[0] for img in images)
    resized = []
    for img in images:
        h, w = img.shape[:2]
        if h != max_height:
            pad = max_height - h
            img = cv2.copyMakeBorder(img, 0, pad, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        resized.append(img)
    return resized

# Configss
image_folder = './snapshots/session_31'   # Change this to your image directory
log_file = './snapshots/session_31/snapshot_log.txt'
banner_threshold = 70.0
image_size = (300, 300)

# Read all image filenames in sorted order
image_paths = sorted([
    os.path.join(image_folder, f)
    for f in os.listdir(image_folder)
    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
])

# Read temperature log
with open(log_file, 'r') as file:
    temperatures = [float(line.strip().split(',')[2].replace(' C', '').strip()) for line in file]

# Sanity check: Match image count with log lines
num_images = min(len(image_paths), len(temperatures))
output_images = []

for i in range(num_images):
    img = cv2.imread(image_paths[i])
    if img is None:
        continue
    img = cv2.resize(img, image_size)
    temp = temperatures[i]

    # Add frame number
    cv2.putText(img, str(i + 1), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Add temperature banner (red with caution or green with temp)
    if temp > banner_threshold:
        # Red banner with caution
        banner = np.full((50, image_size[0], 3), (0, 0, 255), dtype=np.uint8)
        cv2.putText(banner, f"CAUTION: {temp}C", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        # Green banner with temperature
        banner = np.full((50, image_size[0], 3), (0, 200, 0), dtype=np.uint8)
        cv2.putText(banner, f"Temp: {temp}C", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Stack banner on top of image
    img_with_banner = np.vstack((banner, img))

    # Add border
    if temp > banner_threshold:
        border_color = (0, 0, 255)  # Red
    else:
        border_color = (200, 200, 200)  # Light gray for normal

    img_with_banner = cv2.copyMakeBorder(
        img_with_banner,
        top=5, bottom=5, left=5, right=5,
        borderType=cv2.BORDER_CONSTANT,
        value=border_color
    )
    
    output_images.append(img_with_banner)

# Resize all images in chunks to the same height
for i in range(0, len(output_images), 4):
    chunk = output_images[i:i + 4]
    if len(chunk) == 0:
        continue

    # Ensure all chunks in the grid have the same height
    chunk = resize_to_same_height(chunk)

    # Horizontally stack all images in the chunk
    grid = np.hstack(chunk)

    out_path = f'grid_{i // 4 + 1}.jpg'
    cv2.imwrite(out_path, grid)
    print(f"[+] Saved: {out_path}")

# === Combine all grid images into one final large grid ===

# Load all the saved grid images
grid_paths = sorted(glob.glob("grid_*.jpg"))
grids = [cv2.imread(path) for path in grid_paths if cv2.imread(path) is not None]

# Ensure all have the same height by resizing if needed
max_height = max(g.shape[0] for g in grids)
resized_grids = []
for g in grids:
    h, w = g.shape[:2]
    if h != max_height:
        pad = max_height - h
        g = cv2.copyMakeBorder(g, 0, pad, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    resized_grids.append(g)

# Stack horizontally
final_combined = np.hstack(resized_grids)

# Save final combined image
cv2.imwrite("ic3grid_combined_grid.jpg", final_combined)
print("[+] Saved: ic3grid_combined_grid.jpg")
