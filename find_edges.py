from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt



def find_edges(filename):
    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    print(img.shape)
    edges = cv2.Canny(img, 100, 200, 13)

    plt.subplot(121), plt.imshow(img, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(edges, cmap='gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

    plt.show()

if __name__ == '__main__':
    find_edges("warp_map_horiz.png")
    # find_edges("warp_map_vert.png")