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

    def get_is_leaf(self):
        return self.is_leaf

    def set_children(self, tl, tr, bl, br):
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br

    def get_children(self):
        return [self.tl, self.tr, self.bl, self.br]

    def set_parent(self, parent):
        self.parent = parent

    def __str__(self):
        return "(%d, %d, %d), is_leaf:%s" % (self.x, self.y, self.dim, self.is_leaf)


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
            node = node_stack.pop(-1)
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
        """
        Processes the tree by visiting each leaf node, and calling the given
        function.
        """
        node_stack = [self.root]
        while len(node_stack) != 0:
            node = node_stack.pop(0)
            if not node.get_is_leaf():
                children = node.get_children()
                node_stack.extend(children)
            else:
                # This a leaf node that we can process.
                print(node)
                process_node_fn(node.x, node.y, node.dim, node.dim)


class Rectangle:
    def __init__(self, x, y, w, h, colour):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour

    def get_area(self):
        return self.w * self.h

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
        self.rectangles = []
        # self.rectangles = self.create_rectangles()

    def create_rectangles(self):
        rectangles = [Rectangle(10, 10, 20, 30, (255, 0, 0)),
                      Rectangle(50, 20, 100, 50, (255, 255, 0)),]
        return rectangles

    def add_rectangle(self, r):
        self.rectangles.append(r)

    def cb_split_node(self, x, y, w, h):
        """
        Callback to determine if a node needs to be split, to create children
        Returns True, if the node should be split, False otherwise.
        """
        # In this renderer, we need to split if the node contains more than one
        # rectangle, or an edge of a rectangle.
        # Loop over the rectangles, and detect cases where we need to split.
        n_overlapping_rects = 0
        cell_area = w * h
        for rect in self.rectangles:
            intersection_area = rect.intersection_area(x, y, w, h)
            if intersection_area == 0:
                # Can ignore this rectangle.
                continue
            rect_area = rect.get_area()
            if intersection_area < cell_area and intersection_area < rect_area:
                # The rectangle is only partially inside this cell.
                return True
            # if rect_area < cell_area and intersection_area < rect_area:
            #     # The rectangle is only partially inside this cell.
            #     return True
            # The rectangle fully surrounds this cell, or the cell fully surrounds
            # the rectangle.
            n_overlapping_rects += 1

        if n_overlapping_rects > 1:
            return True

        return False

    def cb_process_node(self, x, y, w, h):
        """
        Callback to process the given node, to produce some output.
        """
        # In this renderer, we need to render the the intersection of the
        # rectangles with this node.
        # print("Processing node (%d, %d, %d, %d)" % (x, y, w, h))

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

    def test_rectangle_intersection(self):
        """ Tests the intersection of an area with a rectangle. """
        r = Rectangle(10, 10, 20, 30, (255, 0, 0))
        # A region that doesn't intersect the rectangle.
        self.assertEqual(r.intersection_area(10, 50, 10, 10), 0)
        self.assertEqual(r.intersection_area(40, 0, 10, 10), 0)
        self.assertEqual(r.intersection_area(0, 0, 5, 5), 0)
        # A region with an edge abutting the rectangle.
        self.assertEqual(r.intersection_area(30, 10, 5, 5), 0)
        self.assertEqual(r.intersection_area(10, 40, 5, 5), 0)
        # A region touching corners with the rectangle.
        self.assertEqual(r.intersection_area(0, 0, 10, 10), 0)
        self.assertEqual(r.intersection_area(30, 40, 5, 5), 0)
        # A region wholly inside the rectangle.
        self.assertEqual(r.intersection_area(15, 15, 5, 5), 5*5)
        # A region surrounding the rectangle.
        self.assertEqual(r.intersection_area(0, 0, 50, 50), 20*30)
        # A region intersecting from the side.
        self.assertEqual(r.intersection_area(0, 20, 20, 10), 10 * 10)
        # A region intersecting the corner.
        self.assertEqual(r.intersection_area(0, 0, 20, 20), 10 * 10)
        # A region cutting through the middle.
        self.assertEqual(r.intersection_area(0, 20, 100, 10), 20 * 10)

    def test_split_node(self):
        max_x = 500
        max_y = max_x
        min_cell_size = 10
        self.rr = RectangleRenderer(max_x, max_y)
        self.rr.add_rectangle(Rectangle(10, 10, 20, 30, (255, 0, 0)))
        # Rectangle inside the cell. No need to split.
        self.assertFalse(self.rr.cb_split_node(0, 0, 100, 100))
        # Rectangle surrounding the cell. No need to split.
        self.assertFalse(self.rr.cb_split_node(15, 15, 10, 10))
        # Rectangle intersecting the cell. Need to split.
        self.assertTrue(self.rr.cb_split_node(0, 0, 20, 20))

        # Two rectangles.
        self.rr = RectangleRenderer(max_x, max_y)
        # Two rectangles next to each other.
        self.rr.add_rectangle(Rectangle(10, 10, 20, 20, (255, 0, 0)))
        self.rr.add_rectangle(Rectangle(40, 10, 20, 20, (255, 255, 0)))
        # Both rectangles inside the cell. Need to split.
        self.assertTrue(self.rr.cb_split_node(0, 0, 100, 100))
        # Both rectangles separate from the cell. No need to split.
        self.assertFalse(self.rr.cb_split_node(0, 0, 10, 10))
        # Only one rectangle surrounding the cell. No need to split.
        self.assertFalse(self.rr.cb_split_node(15, 15, 5, 5))

    def test_create_process_tree(self):
        max_x = 500
        max_y = max_x
        min_cell_size = 10
        self.rr = RectangleRenderer(max_x, max_y)
        # Two rectangles next to each other.
        self.rr.add_rectangle(Rectangle(10, 10, 20, 20, (255, 0, 0)))
        self.rr.add_rectangle(Rectangle(40, 10, 20, 20, (255, 255, 0)))

        self.qt = QuadTree(max_x, max_y, min_cell_size)
        self.qt.create_tree(self.rr.cb_split_node)
        self.qt.process_tree(self.rr.cb_process_node)

if __name__ == '__main__':
    unittest.main()
    # main()






