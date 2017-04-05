import argparse
import glob
import math
import os
import shutil
import sys

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colorthief import ColorThief
from PIL import Image
from scipy import misc


R, G, B = 0, 1, 2
TMP_DIR_PATH = None
TILE_IMAGE_DIR_PATH = None

def setup():
    os.makedirs(TMP_DIR_PATH, exist_ok=True)


def cleanup():
    shutil.rmtree(TMP_DIR_PATH)


def rgb_to_lab(c):
    return convert_color(sRGBColor(c[R], c[G], c[B]), LabColor)


def get_image_name(full_path):
    return os.path.split(full_path)[-1]


def get_tile_path(image_name):
    return os.path.join(TILE_IMAGE_DIR_PATH, image_name)


def get_tmp_path(image_name):
    return os.path.join(TMP_DIR_PATH, image_name)


def create_sized_img(filename, x_dim, y_dim, is_tile=True):
    if is_tile:
        img = Image.open(get_tile_path(filename))
    else:
        img = Image.open(filename)

    img = img.resize((x_dim, y_dim), Image.BILINEAR)
    new_filename = get_tmp_path(get_image_name(filename))
    img.save(new_filename)

    return new_filename


def prep_tile_images(dim):
    images = {}

    for filename in glob.glob(get_tile_path("*.png")):
        c = ColorThief(filename).get_color()
        dominate_color = rgb_to_lab(c)

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

    c = (
        int(colors[R] / count),
        int(colors[G] / count),
        int(colors[B] / count),
    )

    return rgb_to_lab(c)


def best_match(color, imgs):
    min_diff = None
    match = None
    diff = 0
    for img in imgs:
        tile_image = imgs[img]

        # Using CIEDE2000 as the diffing algo to approx. human perception
        # https://en.wikipedia.org/wiki/Color_difference#CIEDE2000
        diff = delta_e_cie2000(tile_image, color)

        if match == None or diff < min_diff:
            match = img
            min_diff = diff

    return match


def replace_imgs(img, imgs_to_replace, outfile_name):
    img = Image.open(img)

    images = {}
    for replacement in imgs_to_replace:
        box, new_img = replacement

        if new_img not in images:
            images[new_img] = Image.open(os.path.join(TMP_DIR_PATH, new_img))

        x1, y1, x2, y2 = box
        if x2 - x1 == box_dim and y2 - y1 == box_dim:
            try:
                img.paste(images[new_img], box)
            except Exception as err:
                print("ERROR: Couldn't fit image tile to box")
                print("  ERR_MSG: {}\n  BOX: {}".format(err, box))

    img.save(outfile_name)
    print("Image saved to {}".format(args.outfile))


def process_square(img, box, tile_images):
    color = avg_color(img, box)
    match = best_match(color, tile_images)

    return match

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create photo-mosaics from the command line")

    parser.add_argument("infile", type=str,
                        help="Location of image to create a photo-mosaic from")
    parser.add_argument("outfile", type=str, default="out.png",
                        help="Location to save photo-mosaic to")
    parser.add_argument("--boxes", required=True, type=int,
                        help="Number of boxes to use for pixelating image")
    parser.add_argument("--tile-image-dir", default="example/tile-images", type=str,
                        help="Directory to pull tile images from (will only use .png files)")
    parser.add_argument("--tmp-dir", default="tmp-photo-mosaic-imgs",
                        type=str, help="Temporary directory path to use")

    args = parser.parse_args()

    TILE_IMAGE_DIR_PATH = args.tile_image_dir
    TMP_DIR_PATH = args.tmp_dir

    setup()

    img = misc.imread(args.infile)

    img_dim_y = len(img)
    img_dim_x = len(img[1])
    box_dim = int(min(img_dim_x, img_dim_y) / args.boxes)

    x_cropped = img_dim_x - (img_dim_x % box_dim)
    y_cropped = img_dim_y - (img_dim_y % box_dim)
    r_img = create_sized_img(args.infile, x_cropped, y_cropped, is_tile=False)

    tile_images = prep_tile_images(box_dim)

    # store the images/locations to replace later
    imgs_to_replace = []

    # pixelate image
    end_x, end_y, box, match = None, None, None, None
    for j in range(0, img_dim_x, box_dim):
        for k in range(0, img_dim_y, box_dim):
            # make sure we don't exceed the boundaries, even though img is now
            # resized to fit.
            end_x = j + box_dim if j + box_dim < img_dim_x else img_dim_x
            end_y = k + box_dim if k + box_dim < img_dim_y else img_dim_y
            box = (j, k, end_x, end_y)

            match = process_square(img, box, tile_images)
            imgs_to_replace.append((box, match))

    replace_imgs(r_img, imgs_to_replace, args.outfile)

    cleanup()
