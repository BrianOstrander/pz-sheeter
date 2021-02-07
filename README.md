# Pz Sheeter

## What's it do?

Stitches unpacked and split texture data from [this](https://theindiestone.com/forums/index.php?/topic/3511-pz-unpacker/) exporter into their original tile sheets, ready for use in TileZed. Using unpacked tile sheets means you can use the exports from this project in your custom map without specifying a custom `.pack` file, though you may need to add tile definitions for ones that don't have any yet.

## A word of caution...

It is a known fact that certain unreleased tiles have disappeared or moved between Project Zomboid releases, particularly on the IWBUMS development branch.
**When using unreleased tiles, you do so at your own risk!** 

## How to use this repository

1. Create a directory called `resources/packs` in the same location as this `README` file.
2. Using [this](https://theindiestone.com/forums/index.php?/topic/3511-pz-unpacker/) tool, unpack and split the `.pack` assets from your Project Zomboid install that you wish to restitch using this project.
3. Place the directories created by the unpack/split tool into your `resources/packs` directory.
4. Run `main.py` and the results will be output to an `exports` directory next to this `README` file. You now have the latest and greatest tilesheets!

## Suggested `.pack` files

Not all packs in the Project Zomboid install are needed for mapping, below are my suggestions:

* `Erosion.pack`
* `Tiles2x.pack`
* `Tiles2x.floor.pack`

## Optional steps

### Tracking changes

It is possible to compare your existing tile sheets to the ones exported by this project. To do so, follow these steps:

1. Create a directory called `resources/existing_sheets`
2. Place the tile sheets you are already using in TileZed into the directory you just created. Do not include the 2x directory, just the tile sheet `.png` files within it.
3. Rerun `main.py` and additional information will be included in the console output, along with helper directories you can learn more in the **Understanding your export results** section.  

### Specifying patches

For reasons unclear to me, certain pack files may be missing essential tiles. Additionally, packs may include sheets you will not use for mapping. To solve both problems, it is possible to specify a `json` patch file to clean up the output of your `exports` directory.

1. Create a directory called `resources/patches`
2. Include any number of `json` patch files within this directory -- an example patch file can be found in `examples/patch.jsonc`. If you copy this example, make sure to rename it to use the `.json` extension.
3. Rerun `main.py` and your patch operations will be included in the next export. The pass or fail status of a particular patch operation will be logged in the console.

## Understanding your export results

### `exports`

The root `exports` directory contains all the tile sheets you need. If you are just interested in the latest and greatest tile sheets from your `.pack` files, take the `.png` files from this directory and ignore the other sub directories.

### `__diffs changed__`

This directory contains copies of export tile sheets that have had content modified or their size has changed, relative to the sheets you placed in your `resources/existing_sheets` directory. If their size has changed, they are simply copied. However, if their size has stayed constant, but pixel level changes were detected, they will be copied over with a `_diff.png` file as well. A sheet's `_diff.png` file will show the location of any large changes to the tile sheet's alpha channel - the best way I have found of automatically detecting new tiles on a sheet. Very minor shifts in the alpha channel are ignored, but false positives are still possible. Since it is only the alpha channel being examined, color changes to existing tiles will also be ignored. 

### `__diffs new__`

This directory contains copies of any brand new tile sheets. This is accomplished by comparing export tile sheet names to the tile sheet names in your `resources/existing_sheets` directory.

## Want to help grow this project?

Quality merge requests are welcome! Suggestions via GitHub's issue tracker are also welcome!

**NOTICE FOR THOSE SUBMITTING MERGE REQUESTS: DO NOT INCLUDE ORIGINAL FILES FROM PROJECT ZOMBOID!**

Those files should not be distributed without permission from The Indie Stone. 