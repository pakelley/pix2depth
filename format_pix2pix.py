from PIL import Image, ImageOps as imop
from os import listdir, makedirs, walk
from os.path import isfile, join, exists
import numpy as np

RGB_DIR = "rgb"
DEPTH_DIR = "depth"
COMBINED_DIR = "train"


# Get Image file names
rgb_files = [join(RGB_DIR,pic) for pic in listdir(RGB_DIR) if not pic[0] == '.']
depth_files = [join(DEPTH_DIR,pic) for pic in listdir(DEPTH_DIR) if not pic[0] == '.']
im_files = zip(rgb_files, depth_files)
im_count = len(rgb_files)

# Get max/min values from depth images and remove 'special' max value
depth_maxs = []
depth_mins = []
depth_pixmaps = []
print "Preprocessing depth images..."
for file_index, depth_file in enumerate(depth_files):
    # Get depth file and remove 'special values
    depth_pixels = np.array( Image.open(depth_file) )
    depth_pixels[depth_pixels==65535] = 0
    depth_pixmaps.append(depth_pixels)
    
    # Get max/min values
    depth_vals = depth_pixels.flatten()
    depth_maxs.append( max( depth_vals ) )
    depth_mins.append( min( depth_vals ) )

    if file_index % 25 == 0:
        print "Proccesed %d of %d images" % (file_index, im_count)
    
    
# Get overall max/min
total_max = max(depth_maxs)
total_min = min(depth_mins)

# Make sure output dir exists
if not exists(COMBINED_DIR):
    makedirs(COMBINED_DIR)

# Concatenate and save images
combined_images = [] 
for file_index, im_file in enumerate(im_files):
    # Get images
    rgb_im = Image.open(im_file[0])
    depth_im = depth_pixmaps[file_index]
    # Normalize depth image between 0 and 255
    norm_depth_pixels = ((depth_im - total_min) * 255) / total_max
    norm_depth_im = Image.fromarray(norm_depth_pixels)

    # Get width/height from files. Assuming images are of same dimensions
    width, height = rgb_im.size
    total_width = width * 2

    # Concatenate images
    new_im = Image.new('RGB', (total_width, height))
    new_im.paste(norm_depth_im, (0,0))               # paste depth image on the left
    new_im.paste(rgb_im, (width,0))           # paste rgb image on the right
    combined_images.append(new_im)  # store combined image with filename

    # Save image
    save_dir = join(COMBINED_DIR, "combined_%d.png" % file_index)
    new_im.save(save_dir)
    if(file_index % 25 == 0):
        print "Wrote file %d out of %d" % (file_index, im_count)
