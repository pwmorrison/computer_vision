import math
import unittest
import numpy as np
import cv2
from PIL import Image, ImageDraw
from quad_tree import QuadTree
from gray_code import load_warp_map

"""
Finds the planes in a camera-projector warp map.
Uses a quad tree and homographies to locate the planes.
"""


class PlaneFinder:

    def __init__(self, cam_proj_warp_map, cam_img_dim, min_cell_size=32,
                 split_thresh=0.8, ransac_thresh=0.5):
        self.cam_proj_warp_map = cam_proj_warp_map
        self.cam_img_dim = cam_img_dim
        self.split_thresh = split_thresh
        self.ransac_thresh = ransac_thresh

        self.warp_map_arr_x, self.warp_map_arr_y = \
            self.create_cam_proj_warp_map_arrays(cam_proj_warp_map, cam_img_dim)

        self.qt = self.init_quad_tree(cam_img_dim, min_cell_size)

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
            arr_x[cam_pt[0], cam_pt[1]] = proj_pt[0]
            arr_y[cam_pt[0], cam_pt[1]] = proj_pt[1]
        print(np.unique(arr_x))
        return arr_x, arr_y

    def get_points_in_cell(self, x, y, w, h):
        """ Get the points that are within the given cell. """
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
        return cam_pts, proj_pts

    def cb_split_node(self, x, y, w, h):
        """
        Determines where a node (2D spatial cell) should be split into 4 sub-cells.
        We split a node if we can't fit a certain proportion of the points
        within the cell with a single homography.
        """
        # Get the points that are within the given cell.
        cam_pts, proj_pts = self.get_points_in_cell(x, y, w, h)
        # Fit a homography
        # PAUL: The returned matrix is different to the one in gray_code.py. It
        # looks similar though, so I'm not sure if it's just because the points
        # are in a different order or a different seed or something.
        M, mask = cv2.findHomography(proj_pts, cam_pts, cv2.RANSAC,
                                     self.ransac_thresh)
        print(M)
        return


    def cp_process_node(self, x, y, w, h):
        pass


def main():
    cam_img_dim = (640, 480)
    proj_img_dim = (800, 600)

    # Load the warp map from a file.
    warp_map_file = "warp_map.csv"
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
        warp_map_file = "warp_map_test.csv"
        cam_proj_warp_map, proj_cam_warp_map = load_warp_map(warp_map_file)
        pf = PlaneFinder(cam_proj_warp_map, cam_img_dim)
        pf.cb_split_node(100, 100, 128, 128)

if __name__ == '__main__':
    unittest.main()
    # main()







