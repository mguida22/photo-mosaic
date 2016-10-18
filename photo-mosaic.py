import glob, math, sys

from colorthief import ColorThief
from scipy import misc
from skimage import color


R, G, B = 0, 1, 2

def load_tile_images():
    images = {}

    for filename in glob.glob("*.png"):
        dominate_color = ColorThief(filename).get_color()
        images[filename] = dominate_color

    return images

def avg_color(img, box):
    start_x, start_y, end_x, end_y = box

    colors = [0, 0, 0]
    count = 0
    for j in range(start_x, end_x):
        for k in range(start_y, end_y):
            colors[R] = colors[R] + img[j][k][R]
            colors[G] = colors[G] + img[j][k][G]
            colors[B] = colors[B] + img[j][k][B]
            count += 1

    return (
        int(colors[R] / count),
        int(colors[G] / count),
        int(colors[B] / count),
    )

def best_match(color, tile_images):
    # TODO: this needs to be a better diffing algo. It really should focus on
    # each band in the image. Ex. 20 off on red, green and blue is not that bad,
    # but 60 off on one band and perfect on the others is definitely noticeable.

    # can't be higher than 255 per band, 3 bands --> 765
    min_diff = 765
    match = None
    diff = 0
    for img in tile_images:
        tile_image = tile_images[img]

        diff = (math.fabs(tile_image[R] - color[R])
              + math.fabs(tile_image[G] - color[G])
              + math.fabs(tile_image[B] - color[B]))

        if diff < min_diff:
            match = img

    return match

def replace_with_img(img, box, new_img):
    start_x, start_y, end_x, end_y = box
    # TODO: replace with image here, cropped or resized to fit
    for j in range(start_x, end_x):
        for k in range(start_y, end_y):
            img[j][k] = list(avg_color)

def process_square(img, box, tile_images):
    color = avg_color(img, box)
    new_img = best_match(color, tile_images)
    img = replace_with_img(img, box, new_img)

    return img

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: photo-mosaic.py <input file> <output file> <number of boxes>")
        sys.exit()

    infile_name = sys.argv[1]
    outfile_name = sys.argv[2]
    num_boxes = int(sys.argv[3])

    img = misc.imread(infile_name)

    # TODO: load up images to tile with and caluclate their dominate colors
    tile_images = load_tile_images()

    img_dim_x = len(img)
    img_dim_y = len(img[1])
    box_dim = int(img_dim_x / num_boxes)

    # pixelate image
    end_x, end_y, box = None, None, None
    for j in range(0, img_dim_x, box_dim):
        for k in range(0, img_dim_y, box_dim):
            # make sure we don't exceed the boundaries
            end_x = j + box_dim if j + box_dim < len(img) else len(img)
            end_y = k + box_dim if k + box_dim < len(img[1]) else len(img[1])
            box = (j, k, end_x, end_y)

            img = process_square(img, box, tile_images)

    misc.imsave(outfile_name, img)
