# photo-mosaic

Create photo mosaics from the command line. :art:

## Example

Given the images from the [example](https://github.com/mguida22/photo-mosaic/tree/master/example) folder, we can take the following image:

![girl](https://github.com/mguida22/photo-mosaic/blob/master/example/girl.png)

and turn it into this:

![mosaic-girl](https://github.com/mguida22/photo-mosaic/blob/master/example/out.png)

To do this, we simply run the following command

```
$ python3 photo-mosaic.py example/girl.png example/out.png --boxes=50
```

There's a lot to play around with. The size of the starting image and number of boxes you choose to display will create mosaics that vary greatly from one another.

## Installation

Clone this repository locally and pip install the requirements.

```
$ git clone git@github.com:mguida22/photo-mosaic.git
$ cd photo-mosaic
$ pip3 install -r requirements.txt
```

## How do I use this?

Once you've cloned the repo and installed the requirements, you're ready to get started. Take a look at the [example](https://github.com/mguida22/photo-mosaic/tree/master/example) folder for some sample images to play with.

The most basic example requires an input file of the image you wish to convert, an output file to store the result in, and a param corresponding to how many pixelated boxes the image is divided into.

```
$ python3 photo-mosaic.py <input_file> <output_file> --boxes=<number_of_boxes>
```

For more advanced usage, you can specify any of the following arguments. If you want to use your own images for pixelating, simply put them in a directory and pass it in with the `--tile-image-dir` flag. Numerous, large images may take quite a while to process.

```
required arguments:
  infile                Location of image to create a photo-mosaic from
  outfile               Location to save photo-mosaic to
  --boxes               Number of boxes to use for pixelating image

optional arguments:
  -h, --help            show this help message and exit
  --tile-image-dir      Directory to pull tile images from (will only use .png files)
  --tmp-dir             Temporary directory path to use
```

## License

MIT © Michael Guida
