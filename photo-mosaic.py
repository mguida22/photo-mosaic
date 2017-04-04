import glob
import math
import os
import shutil
import sys

from colorthief import ColorThief
from PIL import Image
from scipy import misc


R, G, B = 0, 1, 2
TMP_DIR_PATH = "tmp-photo-mosaic-imgs"
TILE_IMAGE_DIR_PATH = "tile-images"


def cleanup():
    shutil.rmtree(TMP_DIR_PATH)


def get_image_name(full_path):
    return os.path.split(full_path)[-1]


def get_tile_path(image_name):
    return os.path.join(TILE_IMAGE_DIR_PATH, image_name)


def get_tmp_path(image_name):
    return os.path.join(TMP_DIR_PATH, image_name)


def create_sized_img(filename, x_dim, y_dim):
    img = Image.open(get_tile_path(filename))
    img = img.resize((x_dim, y_dim), Image.BILINEAR)
    new_filename = get_tmp_path(filename)
    img.save(new_filename)


def prep_tile_images(dim):
    images = {}

    # create a temp dir for our images
    os.makedirs(TMP_DIR_PATH, exist_ok=True)
    for filename in glob.glob(get_tile_path("*.png")):
        dominate_color = ColorThief(filename).get_color()

        image_filename = get_image_name(filename)
        create_sized_img(image_filename, dim, dim)
        images[image_filename] = dominate_color

    return images


def avg_color(img, box):
    start_x, start_y, end_x, end_y = box

    colors = [0, 0, 0]
    count = 0
    for j in range(start_x, end_x):
        for k in range(start_y, end_y):
            colors[R] = colors[R] + img[k][j][R]
            colors[G] = colors[G] + img[k][j][G]
            colors[B] = colors[B] + img[k][j][B]
            count += 1

    return (
        int(colors[R] / count),
        int(colors[G] / count),
        int(colors[B] / count),
    )


def best_match(color, imgs):
    # TODO: this needs to be a better diffing algo. It really should focus on
    # each band in the image. Ex. 20 off on red, green and blue is not that bad,
    # but 60 off on one band and perfect on the others is definitely
    # noticeable.

    # can't be higher than 255 per band, 3 bands --> 765
    min_diff = 765
    match = None
    diff = 0
    for img in imgs:
        tile_image = imgs[img]

        diff = (math.fabs(tile_image[R] - color[R])
                + math.fabs(tile_image[G] - color[G])
                + math.fabs(tile_image[B] - color[B]))

        if diff < min_diff:
            match = img
            min_diff = diff

    return match


def replace_img(img, imgs_to_replace, outfile_name):
    img = Image.open(img)

    images = {}
    for replacement in imgs_to_replace:
        box, new_img = replacement

        if new_img not in images:
            images[new_img] = Image.open(os.path.join(TMP_DIR_PATH, new_img))

        try:
            img.paste(images[new_img], box)
        # except ValueError:
            # def create_sized_img(filename, x_dim, y_dim):
            #
            # TODO: this is fucked - fix it.
            # It needs to generate new images to fit the required width here
            # and attempt to replace again
        except Exception as err:
            print("Couldn't fit image tile to box")
            print("  ERROR: {}\n  BOX: {}".format(err, box))

    img.save(outfile_name)


def process_square(img, box, tile_images):
    color = avg_color(img, box)
    match = best_match(color, tile_images)

    return match

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: photo-mosaic.py <input file> <output file> <number of boxes>")
        sys.exit()

    infile_name = sys.argv[1]
    outfile_name = sys.argv[2]
    num_boxes = int(sys.argv[3])

    img = misc.imread(infile_name)

    img_dim_y = len(img)
    img_dim_x = len(img[1])
    box_dim = int(min(img_dim_x, img_dim_y) / num_boxes)

    tile_images = prep_tile_images(box_dim)

    # store the images/locations to replace later
    imgs_to_replace = []

    # pixelate image
    end_x, end_y, box, match = None, None, None, None
    for j in range(0, img_dim_x, box_dim):
        for k in range(0, img_dim_y, box_dim):
            # make sure we don't exceed the boundaries
            end_x = j + box_dim if j + box_dim < img_dim_x else img_dim_x
            end_y = k + box_dim if k + box_dim < img_dim_y else img_dim_y
            box = (j, k, end_x, end_y)

            match = process_square(img, box, tile_images)
            imgs_to_replace.append((box, match))

    replace_img(infile_name, imgs_to_replace, outfile_name)

    cleanup()
