import sys
from scipy import misc


R, G, B = 0, 1, 2

def process_square(arr, start_x, start_y, end_x, end_y):
    end_x = end_x if end_x < len(arr) else len(arr)
    end_y = end_y if end_y < len(arr[1]) else len(arr[1])

    colors = [0, 0, 0]
    count = 0
    for j in range(start_x, end_x):
        for k in range(start_y, end_y):
            colors[R] = colors[R] + arr[j][k][R]
            colors[G] = colors[G] + arr[j][k][G]
            colors[B] = colors[B] + arr[j][k][B]
            count += 1

    avg_color = [
        int(colors[R] / count),
        int(colors[G] / count),
        int(colors[B] / count),
    ]

    for j in range(start_x, end_x):
        for k in range(start_y, end_y):
            arr[j][k] = avg_color

    return arr

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: photo-mosaic.py <input file> <output file> <number of boxes>")
        sys.exit()

    infile_name = sys.argv[1]
    outfile_name = sys.argv[2]
    num_boxes = int(sys.argv[3])

    arr = misc.imread(infile_name)

    img_dim_x = len(arr)
    img_dim_y = len(arr[1])
    box_dim = int(img_dim_x / num_boxes)

    # arr data
    # [x coord][y coord][rgb values]
    for j in range(0, img_dim_x, box_dim):
        for k in range(0, img_dim_y, box_dim):
            arr = process_square(arr, j, k, j + box_dim, k + box_dim)

    misc.imsave(outfile_name, arr)
