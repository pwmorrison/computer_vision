from pylab import *
from numpy import *
from PIL import Image
import os
print os.environ['HOME']

from PCV.localdescriptors import sift

"""
This is the twosided SIFT feature matching example from Section 2.2 (p 44).
"""


def appendimages(im1, im2):
    """ Return a new image that appends the two images side-by-side. """

    # select the image with the fewest rows and fill in enough empty rows
    rows1 = im1.shape[0]
    rows2 = im2.shape[0]

    if rows1 < rows2:
        im1 = concatenate((im1, zeros((rows2 - rows1, im1.shape[1]))), axis=0)
    elif rows1 > rows2:
        im2 = concatenate((im2, zeros((rows1 - rows2, im2.shape[1], im2.shape[2]))), axis=0)
    # if none of these cases they are equal, no filling needed.

    return concatenate((im1, im2), axis=1)

def plot_matches(im1, im2, locs1, locs2, matchscores, show_below=True):
    """ Show a figure with lines joining the accepted matches
        input: im1,im2 (images as arrays), locs1,locs2 (location of features), 
        matchscores (as output from 'match'), show_below (if images should be shown below). """

    im3 = appendimages(im1, im2)
    if show_below:
        im3 = vstack((im3, im3))

    # show image
    imshow(im3)

    # draw lines for matches
    cols1 = im1.shape[1]
    for i, m in enumerate(matchscores):
        if m > 0:
            # Plot a line between the im1 position and the im2 position.
            # Offset the im2.x position by the width of im1, since the images are displayed side-by-side.
            # plot([x_coords], [y_coords])
            plot([locs1[i][0], locs2[m][0] + cols1], [locs1[i][1], locs2[m][1]], 'c')
    axis('off')

def get_matches(locs1, locs2, matchscores):
    for i, m in enumerate(matchscores):
        if m > 0:
            print("%d:(%d, %d) -> %d:(%d, %d)" % (i, locs1[i][0], locs1[i][1], m, locs2[m][0], locs2[m][1]))

# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/climbing_1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/climbing_2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/crans_1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/crans_2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house2_small.jpg'
# imname1 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small.jpg'
# imname2 = 'C:/Users/Paul/programming-computer-vision-git/PCV/data/house1_small_corner.jpg'
imname1 = '/home/paul/computer_vision/images/house1_small.jpg'
imname2 = '/home/paul/computer_vision/images/house1_small_corner.jpg'

# process and save features to file
params="--edge-thresh 10 --peak-thresh 5 --verbose"
sift.process_image(imname1, imname1+'.sift', params=params)
sift.process_image(imname2, imname2+'.sift', params=params)

# read features and match
l1,d1 = sift.read_features_from_file(imname1+'.sift')
l2,d2 = sift.read_features_from_file(imname2+'.sift')
matchscores = sift.match_twosided(d1, d2)

# matchscores will have an entry for each feature in im1.
# The entry will be 0 if there is not a match.
# If there is a match, the entry will be the index of the matching feature in im2.
# matchscores[im1_feat_index] = im2_feat_index, if matchscores[im1_feat_index] != 0

# load images and plot
im1 = array(Image.open(imname1))
im2 = array(Image.open(imname2))

get_matches(l1, l2, matchscores)

plot_matches(im1,im2,l1,l2,matchscores,show_below=True)
show()
