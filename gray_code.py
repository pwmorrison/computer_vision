import numpy as np
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

def generate_gray_code_sequence(upper=10):
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

if __name__ == "__main__":
    print "hello"
    gray_code_arrays = generate_gray_code_sequence()
    # Convert the sequence to bit planes.
    bit_planes = generate_gray_code_bit_planes(gray_code_arrays)
