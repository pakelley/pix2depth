from PIL import Image
from os import listdir, makedirs
from os.path import join, exists
import numpy as np

# Directories to read/save from/to
RGB_DIR = "rgb"
DEPTH_DIR = "depth"
COMBINED_DIR = "combined"

# Make sure output dir exists
if not exists(COMBINED_DIR):
    makedirs(COMBINED_DIR)

# Max/min depth values
MAX_VAL = 5000
MIN_VAL = 300

###################################################################
############################ FUNCTIONS ############################
###################################################################
def normalize_depth(im):
    pixels = np.array( im )
    pixels[pixels==65535] = 0 # Remove placeholder value
    norm_pixels = ( ((pixels - MIN_VAL) * 255) / MAX_VAL ) * (pixels>MIN_VAL)
    return Image.fromarray(norm_pixels)

def concat_images(im_left, im_right):
    # Get width/height from files. Assuming images are of same dimensions
    width, height = rgb_im.size
    total_width = width * 2

    # Concatenate images
    new_im = Image.new('RGB', (total_width, height))
    new_im.paste(im_left, (0,0))       # paste depth image on the left
    new_im.paste(im_right, (width,0))  # paste rgb image on the right
    return new_im

##################################################################
############################## MAIN ##############################
##################################################################
# Get Image file names
rgb_files = [join(RGB_DIR,pic) for pic in listdir(RGB_DIR) if not pic[0] == '.']
depth_files = [join(DEPTH_DIR,pic) for pic in listdir(DEPTH_DIR) if not pic[0] == '.']
im_files = zip(rgb_files, depth_files)
im_count = len(rgb_files)

# Concatenate and save images
combined_images = [] 
for file_index, im_file in enumerate(im_files):
    # Get images
    rgb_im = Image.open(im_file[0])
    depth_im = Image.open(im_file[1])
    
    # Normalize depth image between 0 and 255 and remove placeholder value
    norm_depth_im = normalize_depth(depth_im)

    # Concatenate images
    new_im = concat_images(norm_depth_im, rgb_im)

    # Save combined image
    save_dir = join(COMBINED_DIR, "combined_%d.png" % file_index)
    new_im.save(save_dir)
    if(file_index % 100 == 0):
        print "Wrote file %d out of %d" % (file_index, im_count)
