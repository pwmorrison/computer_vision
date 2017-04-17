from pylab import *
from numpy import *
from PIL import Image, ImageDraw
import cv2

from PCV.localdescriptors import sift

"""
This is the two-sided SIFT feature matching example from Section 2.2 (p 44).
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

def merge_images(im_1, im_2):

    total_width = im_1.width + im_2.width
    total_height = max([im_1.height, im_2.height])

    new_im = Image.new('RGB', (total_width, total_height))

    new_im.paste(im_1, (0, 0))
    new_im.paste(im_2, (im_1.width, 0))

    return new_im

def plot_matches(im_path_1, im_path_2, pts1, pts2, show_below=True):
    im1 = array(Image.open(im_path_1))
    im2 = array(Image.open(im_path_2))

    im3 = appendimages(im1, im2)
    if show_below:
        im3 = vstack((im3, im3))

    # show image
    imshow(im3)

    # draw lines for matches
    cols1 = im1.shape[1]
    for i in range(len(pts1)):
        plot([pts1[i][0], pts2[i][0] + cols1], [pts1[i][1], pts2[i][1]], 'c')
    axis('off')


def plot_matches_pil(im_path_1, im_path_2, pts1, pts2, show_below=True):
    """
    Merge and draw matches with PIL. 
    """
    im_1 = Image.open(im_path_1)
    im_2 = Image.open(im_path_2)

    merged_im = merge_images(im_1, im_2)
    draw = ImageDraw.Draw(merged_im)

    # Draw lines for matches
    for i in range(len(pts1)):
        draw.line((pts1[i][0], pts1[i][1], pts2[i][0] + im_1.width, pts2[i][1]), fill='red', width=5)

    return merged_im

def get_matches(locs1, locs2, matchscores):
    pts1 = []
    pts2 = []
    for i, m in enumerate(matchscores):
        if m > 0:
            pt1 = (locs1[i][0], locs1[i][1])
            pt2 = (locs2[m][0], locs2[m][1])
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

    return H, matchesMask

def apply_homography_to_pts(H, pts):
    src_pts = np.array(pts)
    # Not sure why, but we need to add an extra dimension to call perspectiveTransform.
    src_pts = src_pts.reshape(-1, 1, 2)
    transformed_pts = cv2.perspectiveTransform(src_pts, H)
    transformed_pts = transformed_pts.reshape(-1, 2)
    return transformed_pts

def get_matching_pts_sift(im_path_1, im_path_2):
    """
    Gets the matching points in the two images, using SIFT features.
    """
    # Process and save features to file
    params = "--edge-thresh 10 --peak-thresh 5 --verbose"
    sift.process_image(im_path_1, im_path_1 + '.sift', params=params)
    sift.process_image(im_path_2, im_path_2 + '.sift', params=params)

    # Read features from the two images.
    l1, d1 = sift.read_features_from_file(im_path_1 + '.sift')
    l2, d2 = sift.read_features_from_file(im_path_2 + '.sift')

    # matchscores will have an entry for each feature in im1.
    # The entry will be 0 if there is not a match.
    # If there is a match, the entry will be the index of the matching feature in im2.
    matchscores = sift.match_twosided(d1, d2)

    pts1, pts2 = get_matches(l1, l2, matchscores)

    return pts1, pts2

def match_and_plot_images(im_path_1, im_path_2):
    """
    Determines matching positions in the two images, and creates an image showing the matches. 
    """
    # Get matching points in the two images.
    pts1, pts2 = get_matching_pts_sift(im_path_1, im_path_2)

    # Determine a homography that maps from positions in the first image, to positions in the second image.
    H, matches_mask = get_homography(pts1, pts2)

    # Apply the homography, to see if we get similar points.
    transformed_src_pts = apply_homography_to_pts(H, pts1)
    print("(Im1 pt) -> (Transformed Im1 pt), [Im2 SIFT pt] - IsInlier")
    for i in range(len(pts1)):
        print("(%d, %d) -> (%d, %d), [%d, %d] - %d" % (pts1[i][0], pts1[i][1],
                                                       transformed_src_pts[i][0], transformed_src_pts[i][1],
                                                       pts2[i][0], pts2[i][1], matches_mask[i]))

    # load images and plot
    plot_im = plot_matches_pil(im_path_1, im_path_2, pts1, pts2, show_below=False)

    return plot_im

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

    plot_im = match_and_plot_images(imname1, imname2)

    imshow(plot_im)
    axis('off')
    show()

if __name__ == "__main__":
    main()
