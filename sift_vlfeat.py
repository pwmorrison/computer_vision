from pylab import *
from numpy import *
from PIL import Image

from PCV.localdescriptors import sift

"""
This is the twosided SIFT feature matching example from Section 2.2 (p 44).
"""

# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/climbing_1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/climbing_2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/crans_1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/crans_2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small_corner.jpg'
imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small.jpg'
imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small_corner.jpg'

# process and save features to file
params="--edge-thresh 10 --peak-thresh 5 --verbose"
sift.process_image(imname1, imname1+'.sift', params=params)
sift.process_image(imname2, imname2+'.sift', params=params)

# read features and match
l1,d1 = sift.read_features_from_file(imname1+'.sift')
l2,d2 = sift.read_features_from_file(imname2+'.sift')
matchscores = sift.match_twosided(d1, d2)

# load images and plot
im1 = array(Image.open(imname1))
im2 = array(Image.open(imname2))

sift.plot_matches(im1,im2,l1,l2,matchscores,show_below=True)
show()
