import math
import unittest

class QuadTreeNode:
    """
    Represents a node in the quad tree.
    """

    def __init__(self, x, y, dim, parent, is_leaf):
        self.x = x
        self.y = y
        self.dim = dim
        self.parent = parent
        self.is_leaf = is_leaf
        self.tl = self.tr = self.bl = self.br = None

    def set_is_leaf(self, is_leaf):
        self.is_leaf = is_leaf

    def set_children(self, tl, tr, bl, br):
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br

    def set_parent(self, parent):
        self.parent = parent


class QuadTree:
    """
    A generic quad tree.
    """

    def __init__(self, max_x, max_y, min_cell_size):
        self.max_x = max_x
        self.max_y = max_y
        self.min_cell_size = min_cell_size

        max_node_dim = int(math.pow(2, math.ceil(math.log(max([max_x, max_y]), 2))))
        self.min_node_dim = int(math.pow(2, math.floor(math.log(min_cell_size, 2))))

        # Create a root node that encloses the entire area.
        # The root node covers the smallest power-of-2 area that encloses the
        # given area.
        self.root = QuadTreeNode(0, 0, max_node_dim, None, True)

    def calculate_n_top_cells(self, max_x, max_y):
        max_dim = max(max_x, max_y)

    def create_tree(self, split_node_fn):
        """Creates the quad tree."""
        # A list of nodes that need to be evaluated.
        node_stack = [self.root]

        while len(node_stack) != 0:
            node = node_stack[-1]
            split = split_node_fn(node.x, node.y, node.dim, node.dim)
            if split and node.dim != self.min_node_dim:
                # Split the node into 4 children.
                split_dim = node.dim / 2
                tl_node = QuadTreeNode(
                    node.x, node.y, split_dim, node, True)
                tr_node = QuadTreeNode(
                    node.x + split_dim, node.y, split_dim, node, True)
                bl_node = QuadTreeNode(
                    node.x, node.y + split_dim, split_dim, node, True)
                br_node = QuadTreeNode(
                    node.x + split_dim, node.y + split_dim, split_dim, node, True)
                # Update the node being evaluated.
                node.set_children(tl_node, tr_node, bl_node, br_node)
                node.set_is_leaf(False)
                # Evaluate the split nodes soon.
                node_stack.append(tl_node)
                node_stack.append(tr_node)
                node_stack.append(bl_node)
                node_stack.append(br_node)

    def process_tree(self, process_node_fn):
        pass


class Rectangle:
    def __init__(self, x, y, w, h, colour):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour

    def intersection_area(self, x, y, w, h):
        """Calculates the intersection with the given square."""
        # Go through the cases where there is no intersection.
        if self.x > (x + w):
            return 0
        if (self.x + self.w) < x:
            return 0
        if self.y > (y + h):
            return 0
        if (self.y + self.h) < y:
            return 0
        # There is some intersection.
        # Compute the area.
        min_x = max([x, self.x])
        max_x = min([x + w, self.x + self.w])
        min_y = max([y, self.y])
        max_y = min([y + h, self.y + self.h])
        area = (max_x - min_x) * (max_y - min_y)
        return area

class RectangleRenderer:
    """
    Renders an area containing rectangles, using the QuadTree.
    Used for testing the QuadTree.
    """
    def __init__(self, max_x, max_y):
        self.max_x = max_x
        self.max_y = max_y
        self.rectangles = self.create_rectangles()

    def create_rectangles(self):
        rectangles = [Rectangle(10, 10, 20, 30, (255, 0, 0)),
                      Rectangle(50, 20, 100, 50, (255, 255, 0)),]
        return rectangles

    def cb_split_node(self, x, y, w, h):
        """
        Callback to determine if a node needs to be split, to create children
        Returns True, if the node should be split, False otherwise.
        """
        # In this renderer, we need to split if the node contains more than one
        # rectangle, or an edge or a rectangle.
        n_overlapping_rects = 0
        for rect in self.rectangles:
            pass

    def cb_process_node(self):
        """
        Callback to process the given node, to produce some output.
        """
        # In this renderer, we need to render the the intersection of the
        # rectangles with this node.
        pass


def main():
    max_x = 500
    max_y = max_x
    min_cell_size = 10

    rr = RectangleRenderer(max_x, max_y)
    qt = QuadTree(max_x, max_y, min_cell_size)


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

class TestRectangleMethods(unittest.TestCase):

    def setUp(self):
        max_x = 500
        max_y = max_x
        min_cell_size = 10
        self.rr = RectangleRenderer(max_x, max_y)
        self.qt = QuadTree(max_x, max_y, min_cell_size)

    def test_rectangle_intersection(self):
        # Tests the intersection of an area with a rectangle.
        r = Rectangle(10, 10, 20, 30, (255, 0, 0))
        # A region that doesn't intersect the rectangle.
        self.assertEqual(r.intersection_area(10, 50, 10, 10), 0)
        self.assertEqual(r.intersection_area(40, 0, 10, 10), 0)
        self.assertEqual(r.intersection_area(0, 0, 5, 5), 0)
        # A region with an edge abutting the rectangle.
        # A region touching corners with the rectangle.
        # A region wholly inside the rectangle.
        # A region surrounding the rectangle.
        # A region intersecting from the side.
        # A regin intersecting the corner.

    def test_create_tree(self):
        # self.qt.create_tree(self.rr.cb_split_node)
        # PAUL: Implement this later.
        pass

if __name__ == '__main__':
    unittest.main()
    # main()






