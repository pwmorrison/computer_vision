import numpy as np
from PIL import Image
from glob import glob
import matplotlib.pyplot as plt


def number_to_gray_code_array(num, num_bits):
    # The equivalent gray code number.
    gray_num = num ^ (num >> 1)
    # Binary string.
    binary_str = format(gray_num, '0%db' % (num_bits))
    # Array of binary ints.
    arr = list(binary_str)
    arr = list(map(int, arr))
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
    Generates a sequence of gray code numbers between 0 and the given upper 
    values (not inclusive).
    """
    # The numbers we want to generate gray code sequences for.
    numbers = range(upper)
    # print(numbers)

    # The number of bits we need to represent all numbers.
    largest_number = numbers[-1]
    max_gray = largest_number ^ (largest_number >> 1)
    binary_str = "{0:b}".format(max_gray)
    num_bits = len(binary_str)
    # print("%d bits needed to represent maximum number %d" % (num_bits, 
    # largest_number))

    # Generate gray code sequences.
    # gray_code_arrays = map(number_to_gray_code_array, numbers)
    gray_code_arrays = [
        number_to_gray_code_array(num, num_bits) for num in numbers]
    # print(gray_code_arrays)

    return gray_code_arrays


def generate_gray_code_bit_planes(gray_code_sequences):
    """
    Generates bit planes that can be projected in sequence, to encode each 
    position as gray code.
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


def decode_bit_plane_images(bit_plane_images, black_image, white_image, threshold):
    """
    intensity_range -- the range of valid intensities. The input images are 
    rescaled

    For now, we simply threshold the grayscale data, half way between the 
    minimum and maximum intensity in the images.
    """
    print("Decoding bit plane images.")
    print("Bit plane images:", bit_plane_images)

    if black_image is not None:
        black_im = Image.open(black_image)
        black_im_data = list(black_im.getdata())
        black_im_data = np.asarray(black_im_data)
        black_im_data = black_im_data.reshape((black_im.size[1], black_im.size[0]))
    if white_image is not None:
        white_im = Image.open(white_image)
        white_im_data = list(white_im.getdata())
        white_im_data = np.asarray(white_im_data)
        white_im_data = white_im_data.reshape((white_im.size[1], white_im.size[0]))

    # Prepare the images.
    all_data = None
    bit_planes = []
    for image in bit_plane_images:
        im = Image.open(image)
        w, h = im.size
        im_data = list(im.getdata())
        im_data = np.asarray(im_data)
        print(im_data.shape)
        im_data = im_data.reshape((h, w))

        # Threshold the data.
        # im_data[im_data <= threshold] = 0
        # im_data[im_data > threshold] = 1

        bit_planes.append(im_data)
        # print(image, im_data)

    all_data = np.asarray(bit_planes)
    # print("all_data(depth, width, height):", all_data.shape)
    # print("all_data:", all_data)

    # A warp map, from camera image pixel to decoded projector pixel.
    warp_map_dict = {}

    depth, height, width = all_data.shape
    print(depth, width, height)
    print('')
    for y in range(height):
        for x in range(width):
            if black_image is not None:
                if black_im_data[y, x] > threshold or white_im_data[y, x] < threshold:
                    continue

            # Decode this position.
            bits = []
            for d in range(depth):
                bit = all_data[d, y, x]
                if bit >= threshold:
                    bit = 1
                else:
                    bit = 0
                bits.append(str(bit))
            # We appended to the list in order of increasing bit planes, so 
            # we need to reverse it.
            bits = list(reversed(bits))
            # print("Bits at position %d: %s" % (x, tuple(bits)))
            gray_code_num = int(''.join(bits), 2)
            binary_num = gray_code_to_binary(gray_code_num)
            # print("(x:%d, y:%d): bits: %s, gray code num: %d, 
            # binary num: %d" % (x, y, bits, gray_code_num, binary_num))

            warp_map_dict[(x, y)] = binary_num
        # print('')

    return warp_map_dict


def write_warp_map_to_images(
        warp_map_dict_horiz, warp_map_dict_vert, image_dim, proj_img_dim):
    """
    Output the warp map to a csv file and an image (for debugging).
    """
    # Form a list of camera positions that are in both the horizontal and
    # vertical warp maps.
    horiz_cam_positions = []
    if warp_map_dict_horiz is not None:
        horiz_cam_positions = list(warp_map_dict_horiz.keys())
    vert_cam_positions = []
    if warp_map_dict_vert is not None:
        vert_cam_positions = list(warp_map_dict_vert.keys())
    camera_positions = list(set(horiz_cam_positions + vert_cam_positions))
    camera_positions.sort()

    filename = "warp_map.csv"
    print("Outputting file to %s" % (filename))
    csv_file = open(filename, "w")
    row_str = "cam_x, cam_y, proj_x, proj_y\n"
    csv_file.write(row_str)

    if warp_map_dict_horiz is not None:
        im_horiz = Image.new("RGB", image_dim)
    if warp_map_dict_vert is not None:
        im_vert = Image.new("RGB", image_dim)

    for camera_position in camera_positions:
        # print(camera_position)

        # Get the projector position.
        projector_x = ""
        if warp_map_dict_horiz is not None:
            projector_x = warp_map_dict_horiz[camera_position]
        projector_y = ""
        if warp_map_dict_vert is not None:
            projector_y = warp_map_dict_vert[camera_position]

        row_str = "%s, %s, %s, %s\n" % (camera_position[0], camera_position[1], projector_x, projector_y)
        csv_file.write(row_str)

        if warp_map_dict_horiz is not None:
            if projector_x > proj_img_dim[0]:
                # The decoded position being too large is an error.
                im_horiz.putpixel((int(camera_position[0]), int(camera_position[1])), (255, 0, 0))
            else:
                val = float(projector_x) / proj_img_dim[0] * 255
                im_horiz.putpixel((int(camera_position[0]), int(camera_position[1])), (0, int(val), 0))

    csv_file.close()
    # if warp_map_dict_horiz is not None:
    #     im_horiz.save("warp_map_horiz.png")

    return im_horiz


def generate_gray_code_images(is_horizontal, image_dim, image_file_prefix):
    """
    Generate the gray code sequences to cover the largest possible coordinate.
    """
    if is_horizontal:
        max_value = image_dim[0]
    else:
        max_value = image_dim[1]
    gray_code_arrays = generate_gray_code_sequence(max_value)

    # Convert the sequence to bit planes.
    bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

    # Render the bit planes to images.
    bit_plane_images = []
    for bit_plane_num in range(bit_planes.shape[0]):
        index = bit_planes.shape[0] - bit_plane_num - 1
        bit_plane = bit_planes[index, :]
        im = generate_bit_plane_image(bit_plane, is_horizontal, width, height)
        image_name = "bit_planes/%s_%d.png" % (image_file_prefix, bit_plane_num)
        im.save(image_name)
        bit_plane_images.append(image_name)


if __name__ == "__main__":

    if 0:
        # Test code for generating gray code frames and decoding them.
        frame_dir = r"bit_planes/"
        width = 12
        height = 4
        generate_horizontal = True
        generate_vertical = True

        warp_map_horiz = None
        warp_map_vert = None
        if generate_horizontal:
            # Generate the bit plane images.
            generate_gray_code_images(True, (width, height), "horizontal")
            # Decode the bit planes, to generate a warp map.
            images = glob(frame_dir + "horizontal*.png")
            warp_map_horiz = decode_bit_plane_images(images, 128)
        if generate_vertical:
            # Generate the bit plane images.
            generate_gray_code_images(False, (width, height), "vertical")
            # Decode the bit planes, to generate a warp map.
            images = glob(frame_dir + "vertical*.png")
            warp_map_vert = decode_bit_plane_images(images, 128)

        output_warp_map(warp_map_horiz, warp_map_vert, (width, height))

    elif 1:
        # Test code for decoding gray code frames captured by a real camera.
        if 0:
            # Images captured on laptop.
            frame_dir = r"gray_code/"
            file_name = r"graycode*.png"
            width = 640
            height = 480
            proj_img_dim = (2560, 1440)
            use_black_white = False
        elif 0:
            # Images captured on linux box.
            frame_dir = r"gray_code_2/"
            file_name = r"graycode*.png"
            width = 640
            height = 480
            proj_img_dim = (1920, 1080)
            use_black_white = False
        elif 1:
            # Windows, pos/neg, 500x500.
            frame_dir = r"gray_code_500x500/"
            file_name = r"graycode*pos.png"
            width = 640
            height = 480
            proj_img_dim = (500, 500)
            use_black_white = True
        warp_map_horiz = None
        warp_map_vert = None
        generate_horizontal = True

        if generate_horizontal:
            # Decode the bit planes, to generate a warp map.
            images = glob(frame_dir + file_name)
            images.sort()

            # Plot the input gray code images.
            fig, axes = plt.subplots(nrows=1, ncols=len(images), figsize=(20, 4))
            for i, image in enumerate(images):
                im = Image.open(image)
                im_array = np.asarray(im)
        #         plt.figure()
                axes[i].imshow(np.asarray(im_array), cmap='gray')

            black_image = None
            white_image = None
            if use_black_white:
                black_image = frame_dir + "black.png"
                white_image = frame_dir + "white.png"

            warp_map_horiz = decode_bit_plane_images(images, black_image, white_image, 80)

        # output_warp_map(warp_map_horiz, warp_map_vert, (width, height), proj_img_dim)

        im_horiz = write_warp_map_to_images(warp_map_horiz, warp_map_vert, (width, height), proj_img_dim)
        print(im_horiz)
        im_horiz.save("warp_map_horiz.png")

        plt.figure()
        plt.imshow(np.asarray(im_horiz))

plt.show()