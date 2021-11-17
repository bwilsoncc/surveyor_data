=surveyor_data

## Overview

I want all survey documents to show up in PDF format in our web applications.
They exist in various formats including TIFF, JPEG, and PDF right now.

This project will pull them all into a unified PDF format.
It also writes a bit of metadata to each PDF file.

Once that's done, I will need to update links to point to the new files.

The scripts/ folder contains the Python code

## Method

I ended up using two passes, first I try to use ImageMagick 
to convert files to PDF because generally it produced smaller files.

Then I wanted to write some metadata and the easiest way was using GDAL.

Since a few files could not be converted in the first pass, there
is also some code to try to convert those files with GDAL.

## Failure to set up (Linux only)

I tried doing all processing on Linux because I could use graphicsmagick and the pgmagick python module there.
I gave up eventually because graphicsmagick and GDAL can't install in one conda environment.
Then I needed arcpy to access some Esri things and that is a total loss on Linux. It's hopelessly broken.

Hence I deleted the instructions for Linux. Press on.

## Set up on Windows

I had to install the full Windows ImageMagick package and I made sure "magick" is on the command PATH
so in convert_image_files.py, it can just call magick via subprocess.

I needed to use arcpy and let's face it, co-workers might benefit from being able to run this.

Every attempt today at creating a clean environment failed today. (11/5/21)
Falling back to cloning. Geez.

```bash
conda update --all
conda config --remove channels conda-forge
conda config --add channels esri

conda create -n magick --clone arcgispro-py3
conda activate magick
conda install autopep8
```

## Source image files

My image files are all currently found in 
/cifs/cc-files01/Applications/SurveyorData/survey/Scanned\ Surveys/AA_INDEXED_SURVEYS
so I just set that in scripts/config.py.

## Workflow

1 Set conda environment to 'magick'

2 Run convert_image_files.py to convert and or copy files to PDF format

3 Set conda environment to 'gdal'

4 Run update_metadata.py to fix up the metadata and copy any missing files from #2.
