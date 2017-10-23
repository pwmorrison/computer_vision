import math
import unittest
import numpy as np
import cv2
import os
from PIL import Image, ImageDraw
from quad_tree import QuadTree
from gray_code import load_warp_map, determine_homography_errors

"""
Finds the planes in a camera-projector warp map.
Uses a quad tree and homographies to locate the planes.
"""


class PlaneFinder:

    def __init__(self, cam_proj_warp_map, cam_img_dim, proj_img_dim, out_dir,
                 min_cell_size=8,
                 split_homog_thresh=5, split_percent_thresh=0.9, ransac_thresh=0.5,
                 quad_tree_image_file=None):
        self.cam_proj_warp_map = cam_proj_warp_map
        self.cam_img_dim = cam_img_dim
        self.proj_img_dim = proj_img_dim
        self.split_homog_thresh = split_homog_thresh
        self.split_percent_thresh = split_percent_thresh
        self.ransac_thresh = ransac_thresh
        self.quad_tree_image_file = quad_tree_image_file
        self.out_dir = out_dir

        self.warp_map_arr_x, self.warp_map_arr_y = \
            self.create_cam_proj_warp_map_arrays(cam_proj_warp_map, cam_img_dim)

        self.qt = self.init_quad_tree(cam_img_dim, min_cell_size)
        self.init_processing()
        self.qt.process_tree(self.cb_process_node)
        self.processed_im.save(
            os.path.join(out_dir, "plane_finder_processed_im.png"))

    def init_quad_tree(self, cam_img_dim, min_cell_size):
        qt = QuadTree(cam_img_dim[0], cam_img_dim[1], min_cell_size)
        qt.create_tree(self.cb_split_node)
        return qt

    def find_planes(self):
        self.qt.process_tree(self.cb_process_node)

    def create_cam_proj_warp_map_arrays(self, cam_proj_warp_map, cam_img_dim):
        arr_x = np.empty(cam_img_dim)
        arr_y = np.empty(cam_img_dim)
        arr_x[:] = np.nan
        arr_y[:] = np.nan
        for cam_pt in cam_proj_warp_map.keys():
            proj_pt = cam_proj_warp_map[cam_pt]
            # Only keep the valid points.
            if (cam_pt[0] < 0 or cam_pt[0] >= self.cam_img_dim[0] or
                cam_pt[1] < 0 or cam_pt[1] >= self.cam_img_dim[1] or
                proj_pt[0] < 0 or proj_pt[0] >= self.proj_img_dim[0] or
                proj_pt[1] < 0 or proj_pt[1] >= self.proj_img_dim[1]):
                continue
            # Store the points, where the projector coordinates are indexed by
            # camera coordinates.
            arr_x[cam_pt[0], cam_pt[1]] = proj_pt[0]
            arr_y[cam_pt[0], cam_pt[1]] = proj_pt[1]
        return arr_x, arr_y

    def get_points_in_cell(self, x, y, w, h):
        """ Get the points that are within the given cell. """
        x = int(x); y = int(y); w = int(w); h = int(h)
        # These arrays index the projector points, where the indices are the camera
        # points. NaNs indicate missing points.
        arr_x_cell = self.warp_map_arr_x[x: x + w, y: y + h]
        arr_y_cell = self.warp_map_arr_y[x: x + w, y: y + h]
        # Get lists of coordinates that aren't NaNs.
        cam_pts_x, cam_pts_y = np.where(np.logical_not(np.isnan(arr_x_cell)))
        cam_pts = np.column_stack((cam_pts_x, cam_pts_y))
        proj_pts_x = arr_x_cell[cam_pts_x, cam_pts_y]
        proj_pts_y = arr_y_cell[cam_pts_x, cam_pts_y]
        proj_pts = np.column_stack((proj_pts_x, proj_pts_y))
        proj_pts = proj_pts.astype(int)
        # Shift the cam pts back, since they were shifted to (0, 0) by slicing above.
        cam_pts[:, 0] += x
        cam_pts[:, 1] += y
        return cam_pts, proj_pts

    def cb_split_node(self, x, y, w, h):
        """
        Determines where a node (2D spatial cell) should be split into 4 sub-cells.
        We split a node if we can't fit a certain proportion of the points
        within the cell with a single homography.
        """
        # Get the points that are within the given cell.
        cam_pts, proj_pts = self.get_points_in_cell(x, y, w, h)
        # We need 4 points to fit a homography.
        if cam_pts.shape[0] < 4:
            return False

        if 1:
            # Debug output of the cam points and projector points found in the cell.
            cam_cell_im = Image.new('RGB', self.cam_img_dim, color=(0, 0, 0))
            draw = ImageDraw.Draw(cam_cell_im)
            draw.rectangle((x, y, x+w, y+h), fill=None, outline=(255, 0, 0))
            for cam_pt in cam_pts:
                cam_cell_im.putpixel(cam_pt, (255, 255, 255))
            cam_cell_im.save(os.path.join(
                self.out_dir, "cam_cell_%d_%d_%d_%d.png" % (x, y, w, h)))
            proj_cell_im = Image.new('RGB', self.proj_img_dim, color=(0, 0, 0))
            for proj_pt in proj_pts:
                try:
                    proj_cell_im.putpixel(proj_pt, (255, 255, 255))
                except:
                    pass
            proj_cell_im.save(os.path.join(
                self.out_dir, "proj_cell_%d_%d_%d_%d.png" % (x, y, w, h)))

        # Fit a homography
        # PAUL: The returned matrix is different to the one in gray_code.py. It
        # looks similar though, so I'm not sure if it's just because the points
        # are in a different order or a different seed or something.
        # PAUL: Maybe don't use ransac, since we're trying to determine error.
        M, mask = cv2.findHomography(proj_pts, cam_pts, cv2.RANSAC,
                                     self.ransac_thresh)
        if M is None:
            # PAUL: I'm not sure what situation would trigger this exactly, but
            # we probably can't split any more.
            return False

        # Determine the error of all remaining points, with reference to the
        # found homography.
        errors = determine_homography_errors(M, proj_pts, cam_pts)

        cam_inliers_img = np.zeros((self.cam_img_dim[1], self.cam_img_dim[0]))
        cam_inliers = []
        proj_outliers = []
        cam_outliers = []
        for i, inlier_flag in enumerate(mask):
            proj_pt = proj_pts[i]
            cam_pt = cam_pts[i]
            error = errors[i]
            # Inliers are those used to calculate the homography, and those
            # within a tolerance of the homography.
            if inlier_flag == 1 or error <= self.split_homog_thresh:
                cam_inliers_img[int(cam_pt[1]), int(cam_pt[0])] = 255
                cam_inliers.append(cam_pt)
            else:
                proj_outliers.append(proj_pt)
                cam_outliers.append(cam_pt)

        # Determine whether to split the node, based on the number of low-error
        # points that were fit with the homography.
        n_cam_pts = cam_pts.shape[0]
        n_cam_inliers = len(cam_inliers)
        # print("Num cam pts: %d, num cam inliers: %d" % (n_cam_pts, n_cam_inliers))
        percent_inliers = n_cam_inliers / n_cam_pts
        if percent_inliers < self.split_percent_thresh:
            return True

        return False

    def init_processing(self):
        self.processed_im = Image.new('RGB', self.cam_img_dim)
        if self.quad_tree_image_file is not None:
            # Use the provided file to overlay the quad tree boundaries.
            im = Image.open(self.quad_tree_image_file)
            self.processed_im.paste(im)

    def cb_process_node(self, x, y, w, h):
        """
        Callback to process the given node, to produce some output.
        """
        assert (self.processed_im is not None)
        # # Take a square out of the pre-rendered image, and insert it in the
        # # image being rendered.
        # rendered_cell = self.im.crop((x, y, x+w, y+h))
        # self.rendered_im.paste(rendered_cell, (int(x), int(y)))
        if 1:
            # Draw a border around the cell, to indicate the cell boundaries.
            draw = ImageDraw.Draw(self.processed_im)
            draw.rectangle([x, y, x+w, y+h], fill=None, outline=(255, 0, 0))


def main():
    cam_img_dim = (640, 480)
    proj_img_dim = (800, 600)

    # Load the warp map from a file.
    warp_map_file = r"gray_code_garagenight2\warp_map.csv"
    cam_proj_warp_map, proj_cam_warp_map = load_warp_map(warp_map_file)

    # We create a quad tree in the camera image.

    pf = PlaneFinder(cam_proj_warp_map, cam_img_dim)


    # max_x = 500
    # max_y = max_x
    # min_cell_size = 10
    #
    # rr = RectangleRenderer(max_x, max_y)
    # qt = QuadTree(max_x, max_y, min_cell_size)

class TestFindPlanes(unittest.TestCase):

    def test_split(self):
        cam_img_dim = (640, 480)
        proj_img_dim = (800, 600)
        warp_map_file = r"gray_code_garagenight2\warp_map.csv"
        quad_tree_image_file = r"gray_code_garagenight2\graycode_00_horiz.png"
        out_dir = "output"
        cam_proj_warp_map, proj_cam_warp_map = load_warp_map(warp_map_file)
        pf = PlaneFinder(
            cam_proj_warp_map, cam_img_dim, proj_img_dim, out_dir,
            quad_tree_image_file=quad_tree_image_file)
        # pf.cb_split_node(100, 100, 128, 128)

if __name__ == '__main__':
    unittest.main()
    # main()







