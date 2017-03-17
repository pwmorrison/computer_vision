import numpy as np
from PIL import Image
import sys
import cv2

def number_to_gray_code_array(num, num_bits):
    # The equivalent gray code number.
    gray_num = num ^ (num >> 1)
    # Binary string.
    binary_str = format(gray_num, '0%db' % (num_bits))
    # Array of binary ints.
    arr = list(binary_str)
    arr = map(int, arr)
    return arr

def gray_code_to_binary(num):
    # print("Initial num", num)
    mask = num >> 1
    # print("Initial mask", mask)
    while mask != 0:
        num = num ^ mask
        mask = mask >> 1
        # print(num, mask)
    return num
# unsigned int grayToBinary(unsigned int num)
# {
#     unsigned int mask;
#     for (mask = num >> 1; mask != 0; mask = mask >> 1)
#     {
#         num = num ^ mask;
#     }
#     return num;
# }

def generate_gray_code_sequence(upper):
    """
    Generates a sequence of gray code numbers between 0 and the given upper values (not inclusive).
    """
    # The numbers we want to generate gray code sequences for.
    numbers = range(upper)
    # print(numbers)

    # The number of bits we need to represent all numbers.
    largest_number = numbers[-1]
    max_gray = largest_number ^ (largest_number >> 1)
    binary_str = "{0:b}".format(max_gray)
    num_bits = len(binary_str)
    # print("%d bits needed to represent maximum number %d" % (num_bits, largest_number))

    # Generate gray code sequences.
    # gray_code_arrays = map(number_to_gray_code_array, numbers)
    gray_code_arrays = [number_to_gray_code_array(num, num_bits) for num in numbers]
    # print(gray_code_arrays)

    return gray_code_arrays

def generate_gray_code_bit_planes(gray_code_sequences):
    """
    Generates bit planes that can be projected in sequence, to encode each position as gray code.
    """
    arr = np.asarray(gray_code_sequences)
    # print(arr)
    # print(arr.shape)
    bit_planes = arr.transpose()
    # print(bit_planes)
    # print(bit_planes.shape)
    return bit_planes

def generate_bit_plane_image(bit_plane, is_horizontal, width, height):
    """
    Generates bit planes, from MSB to LSB.
    """
    im_arr = np.zeros((height, width))

    # print(bit_plane)

    if is_horizontal:
        for x in range(width):
            im_arr[:, x] = bit_plane[x]
    else:
        for y in range(height):
            im_arr[y, :] = bit_plane[y]

    im_arr = im_arr * 255
    im_arr = im_arr.astype(np.uint8)
    im = Image.fromarray(im_arr)
    return im

def decode_gray_code_bit_planes(bit_planes):
    print(bit_planes.shape)

def decode_bit_plane_images(bit_plane_images, threshold):
    """
    intensity_range -- the range of valid intensities. The input images are rescaled

    For now, we simply threshold the grayscale data, half way between the minimum and maximum intensity in the images.
    """
    print("Decoding bit plane images.")
    print("Bit plane images:", bit_plane_images)

    # Prepare the images.
    all_data = None
    bit_planes = []
    for image in bit_plane_images:
        im = Image.open(image)
        w, h = im.size
        im_data = list(im.getdata())
        im_data = np.asarray(im_data)
        im_data = im_data.reshape((h, w))

        # Threshold the data.
        im_data[im_data <= threshold] = 0
        im_data[im_data > threshold] = 1

        bit_planes.append(im_data)

        # print(image, im_data)


    all_data = np.asarray(bit_planes)
    print("all_data(depth, width, height):", all_data.shape)
    print("all_data:", all_data)

    depth, height, width = all_data.shape
    print(depth, width, height)
    for y in range(height):
        for x in range(width):
            # Decode this position.
            bits = []
            for d in range(depth):
                bit = all_data[d, y, x]
                bits.append(str(bit))
            # We appended to the list in order of increasing bit planes, so we need to reverse it.
            bits = list(reversed(bits))
            # print("Bits at position %d: %s" % (x, tuple(bits)))
            gray_code_num = int(''.join(bits), 2)
            binary_num = gray_code_to_binary(gray_code_num)
            print("(x:%d, y:%d): bits: %s, gray code num: %d, binary num: %d" % (x, y, bits, gray_code_num, binary_num))

        # return

if __name__ == "__main__":
    width = 4
    height = 1

    # Generate the gray code sequences to cover the largest possible coordinate.
    gray_code_arrays = generate_gray_code_sequence(max(width, height))

    # Convert the sequence to bit planes.
    bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

    # Render the bit planes to images.
    bit_plane_images = []
    for bit_plane_num in range(bit_planes.shape[0]):
        index = bit_planes.shape[0] - bit_plane_num - 1
        bit_plane = bit_planes[index, :]
        im = generate_bit_plane_image(bit_plane, True, width, height)
        image_name = "horizontal_%d.png" % (bit_plane_num)
        im.save(image_name)
        bit_plane_images.append(image_name)

    # Decode the bit planes.
    # decode_gray_code_bit_planes(bit_planes)
    decode_bit_plane_images(bit_plane_images, 128)

    sys.exit(0)

    for bit_plane_num in range(bit_planes.shape[0]):
        bit_plane = bit_planes[bit_plane_num, :]
        im = generate_bit_plane_image(bit_plane, False, width, height)
        im.save("vertical_%d.png" % (bit_plane_num))
