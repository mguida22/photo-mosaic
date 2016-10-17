# photo-mosaic

Create photo mosaics from the command line.

By splitting an image into boxes we can pixelate it, giving all pixels in that box the average color. From here we can match photos with similar colors to the different boxes.

```
$ python3 photo-mosaic.py <input.png> <output.png> <number of boxes>
```

### License

MIT © Michael Guida
