import numpy as np
from PIL import Image
from glob import glob
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cv2


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
    # print("Decoding bit plane images.")
    # print("Bit plane images:", bit_plane_images)

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
        # print(im_data.shape)
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
    # print(depth, width, height)
    # print('')
    for y in range(height):
        for x in range(width):

            decode_threshold = threshold
            if black_image is not None:
                black_pixel = black_im_data[y, x]
                white_pixel = white_im_data[y, x]

                if (white_pixel - black_pixel) < 10:
                    continue

                # PAUL: This threshold didn't seem to work as well as the above diff.
                # if black_pixel > threshold or white_pixel < threshold:
                #     warp_map_dict[(x, y)] = 750
                #     continue

                decode_threshold = (black_pixel + white_pixel) / 2

            # Decode this position.
            bits = []
            for d in range(depth):
                bit = all_data[d, y, x]
                if bit >= decode_threshold:
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


def write_warp_map_to_images(output_dir,
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
    # camera_positions = list(set(horiz_cam_positions + vert_cam_positions))
    if warp_map_dict_horiz is not None and warp_map_dict_vert is not None:
        camera_positions = list(set(horiz_cam_positions) & set(vert_cam_positions))
    elif warp_map_dict_horiz is not None:
        camera_positions = horiz_cam_positions
    elif warp_map_dict_vert is not None:
        camera_positions = vert_cam_positions
    camera_positions.sort()

    filename = "warp_map.csv"
    print("Outputting warp map to file: %s" % (filename))
    csv_file = open(os.path.join(output_dir, filename), "w")
    row_str = "cam_x, cam_y, proj_x, proj_y\n"
    csv_file.write(row_str)

    im_horiz = None
    im_vert = None
    if warp_map_dict_horiz is not None:
        im_horiz = Image.new("RGB", image_dim, (0, 0, 255))
    if warp_map_dict_vert is not None:
        im_vert = Image.new("RGB", image_dim, (0, 0, 255))

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

        if warp_map_dict_vert is not None:
            if projector_y > proj_img_dim[1]:
                # The decoded position being too large is an error.
                im_vert.putpixel((int(camera_position[0]), int(camera_position[1])), (255, 0, 0))
            else:
                val = float(projector_y) / proj_img_dim[1] * 255
                im_vert.putpixel((int(camera_position[0]), int(camera_position[1])), (0, int(val), 0))

    csv_file.close()
    # if warp_map_dict_horiz is not None:
    #     im_horiz.save("warp_map_horiz.png")

    return im_horiz, im_vert


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


def combine_warp_maps(warp_map_horiz, warp_map_vert):
    """
    Creates a warp map from projector pixel to camera pixel, and a warp map from
    camera to projector pixel, given the horizontal and vertical camera-projector
    warp maps.
    """
    print("Combining horizontal and vertical warp maps.")
    cam_proj_warp_map = {}
    proj_cam_warp_map = {}

    cam_positions = list(warp_map_horiz.keys())
    cam_positions.sort()
    for cam_position in cam_positions:
        proj_position = (warp_map_horiz[cam_position], warp_map_vert[cam_position])
        cam_proj_warp_map[cam_position] = proj_position
        proj_cam_warp_map[proj_position] = cam_position

    return cam_proj_warp_map, proj_cam_warp_map


def generate_warp_map(frame_dir, file_name_horiz, file_name_vert, cam_img_dim,
                      proj_img_dim, generate_horizontal=True, generate_vertical=True,
                      use_black_white=True):
    if generate_horizontal:
        # Decode the bit planes, to generate a warp map.
        images = glob(os.path.join(frame_dir, file_name_horiz))
        images.sort()
        print("Generating horizontal warp map using images: ", images)

        if 0:
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
            black_image = os.path.join(frame_dir, "black.png")
            white_image = os.path.join(frame_dir, "white.png")

        warp_map_horiz = decode_bit_plane_images(
            images, black_image, white_image, 90)

    warp_map_vert = None
    if generate_vertical:
        # Decode the bit planes, to generate a warp map.
        images = glob(os.path.join(frame_dir, file_name_vert))
        images.sort()
        print("Generating vertical warp map using images: ", images)

        if 0:
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
            black_image = os.path.join(frame_dir, "black.png")
            white_image = os.path.join(frame_dir, "white.png")

        warp_map_vert = decode_bit_plane_images(images, black_image,
                                                white_image, 90)

    # output_warp_map(warp_map_horiz, warp_map_vert, (width, height), proj_img_dim)

    im_horiz, im_vert = write_warp_map_to_images(
        frame_dir, warp_map_horiz, warp_map_vert, cam_img_dim, proj_img_dim)

    return warp_map_horiz, warp_map_vert, im_horiz, im_vert


def find_camera_quad(cam_pts, cam_img_dim):
    """
    Finds a quad surrounding the given set of camera points.
    Assumes that the points are dense enough that, when the points are rendered
    to an image, it forms a quad in the image.
    """
    # Render the camera points to an image.
    cam_img = np.zeros((cam_img_dim[1], cam_img_dim[0]), dtype=np.uint8)
    for cam_pt in cam_pts:
        cam_img[int(cam_pt[1]), int(cam_pt[0])] = 255
    # Get the edges in the image.
    bin = cv2.Canny(cam_img, 0, 50, apertureSize=5)
    bin = cv2.dilate(bin, None)
    # Find the contours in the image, matching the edges.
    bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST,
                                                cv2.CHAIN_APPROX_SIMPLE)
    # Select te quad that we'll use.
    # The quad should be large enough, have 4 sides, etc.
    quads = []
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
        if len(cnt) == 4 and cv2.contourArea(
                cnt) > 1000 and cv2.isContourConvex(cnt):
            cnt = cnt.reshape(-1, 2)
            quads.append(cnt)
    quads = np.array(quads)
    return quads


def find_homographies(
        cam_proj_warp_map, proj_cam_warp_map, cam_size, proj_size, ransac_thresh=2.0):
    """
    Finds homographies in an warp map. This verifies that we can use findHomography
    with RANSAC to find the planes in an image.
    """
    all_proj_pts = list(proj_cam_warp_map.keys())
    # proj_pts.sort()
    cam_pts = []
    proj_pts = []
    for i in range(len(all_proj_pts)):
        proj_pt = all_proj_pts[i]
        cam_pt = proj_cam_warp_map[proj_pt]

        # if proj_pt[0] < 180 or proj_pt[0] > 560 or proj_pt[1] < 150 or proj_pt[1] > 530:
        # if proj_pt[0] < 180 or proj_pt[0] > 560:# or proj_pt[1] < 150 or proj_pt[1] > 530:
        # if proj_pt[0] < 500 or proj_pt[1] < 500:#560:
        #     continue

        cam_pts.append(cam_pt)
        proj_pts.append(proj_pt)

    proj_pts = np.array(proj_pts, dtype=np.float32)
    cam_pts = np.array(cam_pts, dtype=np.float32)

    # Iterate over the image, finding a new plane at each iteration.
    homogs = []
    plane_quads = []
    for iteration in range(2):
        print("Finding planes, iteration %d" % iteration)
        M, mask = cv2.findHomography(proj_pts, cam_pts, cv2.RANSAC, ransac_thresh)
        mask = mask.ravel().tolist()
        # print(M)

        cam_inliers_img = np.zeros((cam_size[1], cam_size[0]))
        cam_inliers = []
        proj_outliers = []
        cam_outliers = []
        for i, inlier_flag in enumerate(mask):
            proj_pt = proj_pts[i]
            cam_pt = cam_pts[i]
            if inlier_flag == 1:
                cam_inliers_img[int(cam_pt[1]), int(cam_pt[0])] = 255
                cam_inliers.append(cam_pt)
            else:
                proj_outliers.append(proj_pt)
                cam_outliers.append(cam_pt)

        # Get the quads surrounding the inliers.
        quads = find_camera_quad(cam_inliers, cam_size)
        print("Quads at iteration %d:" % iteration, quads)
        # Insert the quads into the inliers image.
        cam_inliers_img_rgb = np.zeros(
            (cam_inliers_img.shape[0], cam_inliers_img.shape[1], 3))
        cam_inliers_img_rgb[:, :, 0] = cam_inliers_img
        cam_inliers_img_rgb[:, :, 1] = cam_inliers_img
        cam_inliers_img_rgb[:, :, 2] = cam_inliers_img
        # print([quads])
        cv2.drawContours(cam_inliers_img_rgb, [quads], -1, (0, 0, 255), 5)

        cv2.imshow('Cam inliers %d:' % (iteration), cam_inliers_img_rgb)

        homogs.append(M)
        plane_quads.append(quads)

        # Replace the current projector and camera points with the outliers.
        proj_pts = np.array(proj_outliers)
        cam_pts = np.array(cam_outliers)

    # Render all quads into a camera image.

    # Render all quads into a projector image.
    print("Rendering quads to projector image.")
    proj_quads_img = np.zeros((proj_size[1], proj_size[0], 3))
    for plane_num in range(len(homogs)):
        # Invert the homography, to map from camera space to projector space.
        success, M_inv = cv2.invert(M)
        # Map the quads to projector space.
        quads_cam = plane_quads[plane_num]
        quads_proj = []
        for quad in quads_cam:
            quad = quad.astype(np.float64)
            quad_proj = cv2.perspectiveTransform(np.array([quad]), M_inv)
            quads_proj.append(quad_proj.astype(np.int32))
        # quads_cam = quads_cam.astype(np.float64)
        # quads_proj = cv2.perspectiveTransform(quads_cam, M_inv)
        # print(quads_proj)

        # quads_proj = quads_proj.tolist()
        cv2.drawContours(proj_quads_img, quads_proj, -1, (0, 0, 255), 5)
    cv2.imshow('Projector space quads', proj_quads_img)

    return homogs, plane_quads


def allocate_warp_map_pts_to_planes(
        cam_proj_warp_map, homogs, cam_size, max_error_thresh=5,
        cam_error_thresh=0.2, max_error_ceiling=20):
    """
    Allocates the mapped points in a warp map to planes, as defined by the given
    homographies.
    The error of each point is calculated, being a measure of the distance between
    the point an the planes. In particularly, the maximum error defines how well each
    point belongs to a single plane - if a point has large maximum error, and small
    minimum error, it is probably a good point for its allocated plane. If a point
    has small maximum error, it is close to two or more planes, and is therefore
    not a good point, to use to define the planes.

    cam_error_thresh -- (between 0 and 1). A threshold on the maximum error. Any
    points less than this threshold are considered too close to two or more planes,
    and therefore do not contribute to plane boundaries. Larger values cause the
    planes to separate more.

    max_error_ceiling -- (> 0). A limit on the maximum error values. This is used
    to normalise the errors prior to applying cam_error_thresh, so it affects the
    separation of planes etc.
    """
    print("Allocating warp map points to %d planes." % len(homogs))
    # Extract the projector and camera points from the warp map.
    cam_proj_pts = np.array(list(cam_proj_warp_map.items()), dtype=np.float32)
    cam_pts = cam_proj_pts[:, 0, :]
    proj_pts = cam_proj_pts[:, 1, :]

    # Find the homography (plane) that has the smallest "reprojection" error, for
    # each point.
    # First, determine the error for each point, under each homography (plane).
    print("Determining homography errors for each warp map point.")
    homog_errors = []
    for proj_cam_homog in homogs:
        # Errors when mapping from projector to camera.
        mapped_cam_pts = cv2.perspectiveTransform(
            np.array([proj_pts]).astype(np.float64), proj_cam_homog)
        mapped_cam_pts = mapped_cam_pts[0]
        cam_errors = np.linalg.norm(cam_pts - mapped_cam_pts, axis=1)
        # Errors when mapping from camera to projector.
        success, cam_proj_homog = cv2.invert(proj_cam_homog)
        mapped_proj_pts = cv2.perspectiveTransform(
            np.array([cam_pts]).astype(np.float64), cam_proj_homog)
        mapped_proj_pts = mapped_proj_pts[0]
        proj_errors = np.linalg.norm(proj_pts - mapped_proj_pts, axis=1)
        # Combine the errors, to form a single error for this point.
        summed_errors = cam_errors + proj_errors
        homog_errors.append(summed_errors)
    homog_errors = np.array(homog_errors)
    # The plane that has the smallest error, for each point.
    min_error_homog = np.argmin(homog_errors, axis=0)
    # The smallest error, for each point.
    min_errors = np.amin(homog_errors, axis=0)
    # The largest error, for each point.
    max_errors = np.amax(homog_errors, axis=0)

    print("Number of points allocated to each plane:", np.bincount(min_error_homog))

    # Form dictionaries mapping cam and proj points to planes.
    cam_plane_dict = {}
    proj_plane_dict = {}
    for i in range(cam_pts.shape[0]):
        cam_pt = cam_pts[i]
        proj_pt = proj_pts[i]
        plane = min_error_homog[i]
        error = min_errors[i]
        if error > max_error_thresh:
            plane = -1
        cam_plane_dict[(int(cam_pt[0]), int(cam_pt[1]))] = plane
        proj_plane_dict[(int(proj_pt[0]), int(proj_pt[1]))] = plane

    # Generate some other stats.
    print(list(cam_plane_dict.values()))
    unique_planes, counts = np.unique(list(cam_plane_dict.values()), return_counts=True)
    print("Number of thresholded points allocated to each plane, at threshold %d:" %
          max_error_thresh, np.asarray((unique_planes, counts)).T)
    # for plane in unique_planes:
    #     if plane == -1:
    #         continue
    #     # Get the minimum and maximum error for points allocated to this plane.
    #     min_plane_error

    if 0:
        # Form a camera image that contains all the planes, with pixels coloured
        # according to the plane they belong to.
        colors = cm.rainbow(np.linspace(0, 1, len(homogs)))
        # cmap = cm.get_cmap('Spectral')
        cam_plane_img = np.zeros((cam_size[1], cam_size[0], 3))
        for i in range(cam_pts.shape[0]):
            cam_pt = cam_pts[i]
            plane = min_error_homog[i]
            error = min_errors[i]
            if plane == -1:#is None:#error > max_error_thresh:
                continue
            colour = colors[plane]
            # cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), :] = colour[:3]
            # for colour_channel = [0, 1, 2]:
            #     cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), colour_channel] = colour[]
            if plane == 0:
                cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), 0] = 255
            elif plane == 1:
                cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), 1] = 255
            else:
                assert(False)
        # cv2.imshow('Camera space planes', cam_plane_img)

    # Form a camera image that shows the minimum error.
    cam_error_img = np.zeros((cam_size[1], cam_size[0]), dtype=np.float32)
    for i in range(cam_pts.shape[0]):
        cam_pt = cam_pts[i]
        min_error = min_errors[i]
        max_error = max_errors[i]
        if min_error > 100:
            continue
        # error = min_errors[i] / 10  # np.amax(min_errors)
        cam_error_img[int(cam_pt[1]), int(cam_pt[0])] = max_error
    # Limit the maximum errors to the ceiling.
    # Use this value to adjust the "gap" between planes. Smaller value = smaller gap.
    cam_error_img[cam_error_img > max_error_ceiling] = max_error_ceiling
    # Normalise the max error values to between 0 and 1.
    cam_error_img /= max_error_ceiling
    # Make a copy so we can view the original errors later.
    original_cam_error_img = cam_error_img.copy()
    # Threshold the error image, to get a binary error map.
    # Any value below the threshold is considered "close" to two or more planes,
    # and therefore we can't allocate it to any one plane.
    # The larger the threshold, the more separated the planes, around
    # intersections between planes. Between 0 and 1.
    cam_error_img[cam_error_img >= cam_error_thresh] = 1.0
    cam_error_img[cam_error_img < cam_error_thresh] = 0.0
    # Filter to remove noise, and smooth the edges.
    # cam_error_img = cv2.blur(cam_error_img, (5, 5))
    # cam_error_img = cv2.GaussianBlur(cam_error_img, (5, 5), 0)
    # cam_error_img = cv2.medianBlur(cam_error_img, 5)
    cam_error_img = cv2.bilateralFilter(cam_error_img, 9, 75, 75)
    # cam_error_img[cam_error_img >= 0.2] = 1.0
    # Dilation to make the subsequent contour match the boundary closer.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10, 10))
    cam_error_img = cv2.dilate(cam_error_img, kernel, iterations=1)
    # cv2.imshow('Camera space homog error', cam_error_img)
    # Find the contours in the image, matching the edges.
    bin, contours, hierarchy = cv2.findContours(
        cam_error_img.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    print("Found %d contours in camera error image." % len(contours))
    # The polygons should be large enough.
    polys = []
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
        if cv2.contourArea(cnt) > 1000:# and cv2.isContourConvex(cnt):
            cnt = cnt.reshape(-1, 2)
            polys.append(cnt)
    polys = np.array(polys)
    cv2.drawContours(original_cam_error_img, polys, -1, (0, 0, 255), 1)
    cv2.imshow('Camera space error polys', original_cam_error_img)

    filled_poly_imgs = []
    for poly in polys:
        filled_poly_img = np.zeros((cam_size[1], cam_size[0]), dtype=np.float32)
        cv2.fillPoly(filled_poly_img, pts=[poly], color=(1))
        filled_poly_imgs.append(filled_poly_img)

    # Re-create the plane dicts, according to the determined plane contours.
    cam_plane_dict = {}
    proj_plane_dict = {}
    for i in range(cam_pts.shape[0]):
        cam_pt = cam_pts[i]
        proj_pt = proj_pts[i]

        found_poly = False
        for plane, filled_poly_img in enumerate(filled_poly_imgs):
            if filled_poly_img[int(cam_pt[1]), int(cam_pt[0])] == 1:
                found_poly = True
                break
        if not found_poly:
            plane = None

        cam_plane_dict[(int(cam_pt[0]), int(cam_pt[1]))] = plane
        proj_plane_dict[(int(proj_pt[0]), int(proj_pt[1]))] = plane

    cam_plane_img = np.zeros((cam_size[1], cam_size[0], 3))
    for i in range(cam_pts.shape[0]):
        cam_pt = cam_pts[i]
        plane = cam_plane_dict[(int(cam_pt[0]), int(cam_pt[1]))]
        if plane == 0:
            cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), 0] = 255
        elif plane == 1:
            cam_plane_img[int(cam_pt[1]), int(cam_pt[0]), 1] = 255
        else:
            pass

    return cam_plane_dict, proj_plane_dict, cam_plane_img

def main():
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
            file_name_horiz = r"graycode*.png"
            width = 640
            height = 480
            proj_img_dim = (2560, 1440)
            use_black_white = False
        elif 0:
            # Images captured on linux box.
            frame_dir = r"gray_code_2/"
            file_name_horiz = r"graycode*.png"
            width = 640
            height = 480
            proj_img_dim = (1920, 1080)
            use_black_white = False
        elif 0:
            # Windows, pos/neg, 500x500.
            frame_dir = r"gray_code_500x500/"
            file_name_horiz = r"graycode*pos.png"
            width = 640
            height = 480
            # proj_img_dim = (500, 500)
            proj_img_dim = (800, 600)
            use_black_white = True
        elif 1:
            # Windows, pos, 500x500, horiz and vert.
            # frame_dir = r"gray_code_500x500_horiz_vert/"
            # frame_dir = r"gray_code_projector_500x500"
            # frame_dir = r"gray_code_projector_500x500_corner"
            # frame_dir = r"gray_code_screen_500x500"
            # frame_dir = r"gray_code_garagenight2"
            frame_dir = r"gray_code_projector_500x500_corner"
            file_name_horiz = r"graycode*horiz.png"
            file_name_vert = r"graycode*vert.png"
            cam_img_dim = (640, 480)
            proj_img_dim = (800, 600)
            use_black_white = True
            generate_vertical = True
        warp_map_horiz = None
        warp_map_vert = None
        generate_horizontal = True

        warp_map_horiz, warp_map_vert, im_horiz, im_vert = generate_warp_map(
            frame_dir, file_name_horiz, file_name_vert, cam_img_dim, proj_img_dim)

        cam_proj_warp_map, proj_cam_warp_map = combine_warp_maps(
            warp_map_horiz, warp_map_vert)

        homogs, plane_quads = find_homographies(
            cam_proj_warp_map, proj_cam_warp_map, cam_img_dim, proj_img_dim)

        cam_planes_dict, proj_planes_dict, cam_plane_img = \
            allocate_warp_map_pts_to_planes(cam_proj_warp_map, homogs, cam_img_dim)
        cv2.imshow('Camera space planes', cam_plane_img)

        print(im_horiz)
        print(im_vert)
        if im_horiz is not None:
            im_horiz.save("warp_map_horiz.png")
            plt.figure()
            plt.imshow(np.asarray(im_horiz))
        if im_vert is not None:
            im_vert.save("warp_map_vert.png")
            plt.figure()
            plt.imshow(np.asarray(im_vert))

    plt.show()

if __name__ == "__main__":
    main()