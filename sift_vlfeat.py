from pylab import *
from numpy import *
from PIL import Image
import cv2

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
    pts1 = []
    pts2 = []
    for i, m in enumerate(matchscores):
        if m > 0:
            pt1 = (locs1[i][0], locs1[i][1])
            pt2 = (locs1[m][0], locs1[m][1])
            print("%d:(%d, %d) -> %d:(%d, %d)" % (i, pt1[0], pt1[1], m, pt2[0], pt2[1]))
            pts1.append(pt1)
            pts2.append(pt2)
    return pts1, pts2

def get_homography(pts1, pts2):

    src_pts = np.array(pts1)
    dst_pts = np.array(pts2)

    # I think M is the homography matrix, and mask indicates the inlying matches.
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()

    # print(H)
    # print(mask)

    return H, matchesMask

def apply_homography_to_pts(H, pts):
    src_pts = np.array(pts)
    # Not sure why, but we need to add an extra dimension to call perspectiveTransform.
    src_pts = src_pts.reshape(-1, 1, 2)
    transformed_pts = cv2.perspectiveTransform(src_pts, H)
    transformed_pts = transformed_pts.reshape(-1, 2)
    return transformed_pts

def main():

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

    pts1, pts2 = get_matches(l1, l2, matchscores)

    H, matches_mask = get_homography(pts1, pts2)

    # Apply the homography, to see if we get similar points.
    transformed_src_pts = apply_homography_to_pts(H, pts1)
    print("(Im1 pt) -> (Transformed Im1 pt), [Im2 SIFT pt] - IsInlier")
    for i in range(len(pts1)):
        print("(%d, %d) -> (%d, %d), [%d, %d] - %d" % (pts1[i][0], pts1[i][1],
                                                  transformed_src_pts[i][0], transformed_src_pts[i][1],
                                                  pts2[i][0], pts2[i][1], matches_mask[i]))

    plot_matches(im1,im2,l1,l2,matchscores,show_below=True)
    show()

if __name__ == "__main__":
    main()
