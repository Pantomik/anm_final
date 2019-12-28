
import numpy as np
import struct
import matplotlib.pyplot as plt


def parser(path):
    file = open(path, 'r')
    values = []
    for line in file.readlines()[1:500]:
        value = line.split(',')[1]
        values.append(value)
    file.close()
    return values


def read_ekg_data(input_file):
    """
    Read the EKG data from the given file.
    """
    with open(input_file, 'rb') as input_file:
        data_raw = input_file.read()
    n_bytes = len(data_raw)
    n_shorts = n_bytes/2
    # data is stored as 16-bit samples, little-endian
    # '<': little-endian
    # 'h': short
    unpack_string = '<%dh' % n_shorts
    # sklearn seems to throw up if data not in float format
    data_shorts = np.array(struct.unpack(unpack_string, data_raw)).astype(float)
    print(data_shorts)
    return data_shorts


def plot_ekg(input_file, n_samples):
    """
    Plot the EKG data from the given file (for debugging).
    """
    ekg_data = read_ekg_data(input_file)
    plt.plot(ekg_data[0:n_samples])
    plt.show()


def plot_mine(path='datasets/train.csv'):
    values = parser(path)
    plt.plot(np.array(values))
    plt.show()


def main():
    plot_mine()


if __name__ == '__main__':
    main()

