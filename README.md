#survey

As usual I am co-opting this folder which currently contains a shapefile.
I will probably just delete it since it's been around since 2006.

There are a bunch of files out there called "surveys" containing images in different formats.
This project will pull them all into a unified PDF format.

Once that's done, I will need to update links to point to the new files.

The scripts/ folder will contain Python code

## Method

I am using graphicsmagick because I can run it from Python and because
it produces the smallest PDF files. The other library I tried was GDAL.
It generates PDFs that are 4x the size of the TIFF file so it's doing
something extra in there.

I need to use GDAL to set up the metadata on each PDF once they are created and/or copied.

## Set up (Linux only)

Create a conda environment for Python 3 and install the packages we need and activate it.
The support for this on Windows is weak so I'm doing Linux today. I mount the filesystem
with all the picture files and use a remote session from VSCode to debug and test.

I am not sure if I need to do the apt installation, try without.

```bash
sudo apt install g++ libgraphicsmagick++1-dev libboost-python-dev
```

```bash
conda update --all
conda config --add channels conda-forge
conda create -n magick python autopep8 boost
conda activate magick
pip install pgmagick
```

```bash
conda create -n gdal python autopep8 gdal
conda activate gdal
```

Note that pgmagick and gdal fight one another and if you need to use a newer copy of either
you should create two separate conda environments so that they can live peacefully.

## Files

The image files are all currently found in 
/cifs/cc-files01/Applications/SurveyorData/survey/Scanned\ Surveys/AA_INDEXED_SURVEYS/Subdivisions_by_Name_All
so I just embed that in the code.

## Workflow

1 Run convert_image_files.py to convert and or copy files to PDF foirmat
2 Run update_metadata.py to fix up the metadata
