import numpy as np
from PIL import Image
import cv2

print cv2.__version__

def number_to_gray_code_array(num):
    # The equivalent gray code number.
    gray_num = num ^ (num >> 1)
    # Binary string.
    binary_str = format(gray_num, '08b')
    # Array of binary ints.
    arr = list(binary_str)
    arr = map(int, arr)
    return arr

def generate_gray_code_sequence(upper):
    """
    Generates a sequence of gray code numbers between 0 and the given upper values (not inclusive).
    """
    # The numbers we want to generate gray code sequences for.
    numbers = range(upper)
    print(numbers)

    # Generate gray code sequences.
    gray_code_arrays = map(number_to_gray_code_array, numbers)
    print(gray_code_arrays)

    return gray_code_arrays

def generate_gray_code_bit_planes(gray_code_sequences):
    """
    Generates bit planes that can be projected in sequence, to encode each position as gray code.
    """
    arr = np.asarray(gray_code_sequences)
    print(arr)
    print(arr.shape)
    bit_planes = arr.transpose()
    print(bit_planes)
    print(bit_planes.shape)
    return bit_planes

def generate_bit_plane_image(bit_plane, is_horizontal, width, height):
    im_arr = np.zeros((height, width))

    print(bit_plane)

    if is_horizontal:
        for x in range(width):
            im_arr[:, x] = bit_plane[x]

    im_arr = im_arr * 255
    im_arr = im_arr.astype(np.uint8)

    # print(im_arr)
    # im_arr = im_arr[:, :, np.newaxis]
    # print(im_arr)
    im = Image.fromarray(im_arr)
    return im

if __name__ == "__main__":
    width = 12
    height = 8

    # Generate the gray code sequences to cover the largest possible coordinate.
    gray_code_arrays = generate_gray_code_sequence(max(width, height))

    # Convert the sequence to bit planes.
    bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

    # Render the bit planes to images.
    for bit_plane_num in range(bit_planes.shape[0]):

        bit_plane = bit_planes[bit_plane_num, :]
        im = generate_bit_plane_image(bit_plane, True, width, height)
        im.save("horizontal_%d.png" % (bit_plane_num))
