=surveyor_data

## Overview

I want all survey documents to show up in PDF format in our web applications.
They exist in various formats including TIFF, JPEG, and PDF right now.

This project will pull them all into a unified PDF format.
It also writes a bit of metadata to each PDF file.

Once that's done, I will need to update links to point to the new files.

The scripts/ folder contains the Python code

## Method

I ended up using two passes, first I try to use graphicsmagick 
to convert files to PDF because generally it produced smaller files.

Then I wanted to write some metadata and the easiest way was using GDAL.

Since a few files could not be converted with graphicsmagick, there
is also some code to convert those files with GDAL.

## Set up (Linux only)

I tried using Windows at first but could not convince the packages to install there.

I tried installing both graphicsmagick and GDAL in one conda environment and failed. So I use two!
pgmagick and gdal fight one another and if you need to use a newer copy of either
you should create two separate conda environments so that they can live peacefully.
I think if you are happy using older code you could put them both in one environment.

The files all live in a Windows fileserver so I mount the filesystem
with all the picture files and use a remote session from VSCode to debug and test.

I am not sure if I need to do this apt installation, try without.

```bash
sudo apt install g++ libgraphicsmagick++1-dev libboost-python-dev
```

```bash
conda update --all
conda config --add channels conda-forge
```

For the first script, create a graphicsmagick environment called 'magick'.
The autopep8 package is for VSCode.

```bash
conda create -n magick python autopep8 boost
conda activate magick
pip install pgmagick
```

For the second script, create a GDAL environment called 'gdal'.
I wanted to do some testing in Jupyter so I added ipykernel to this one.

```bash
conda create -n gdal python autopep8 gdal ipykernel
conda activate gdal
```

## Source image files

My image files are all currently found in 
/cifs/cc-files01/Applications/SurveyorData/survey/Scanned\ Surveys/AA_INDEXED_SURVEYS
so I just embed that in scripts/config.py.

## Workflow

1 Set conda environment to 'magick'

2 Run convert_image_files.py to convert and or copy files to PDF format

3 Set conda environment to 'gdal'

4 Run update_metadata.py to fix up the metadata and copy any missing files from #2.
