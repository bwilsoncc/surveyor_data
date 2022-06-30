# surveyor_data

## Overview

Create new workflow for publishing survey documents.

Old workflow

1 Public Works (aka PW) scans surveys and puts them on the server.
2 PW creates new polygons in 'surveys'.
3 GIS runs a Powershell (Create_pathname_table2019.ps1) that

* finds new or changed files on the server and updates a database.
* uses that database to update a table

4 PW links entries in the table to the polygons

Potential new workflow

1. PW scans new surveys and puts them on the server
2. PW updates old surveys (possibly)
3. PW creates a polygon for each new survey, with a matching name
4. PW invokes an update via a web page (that has openlayers map in it)

* walks file system and updates the surveyImages table (as a microservice) build_feature_class.py
* generates a new hyperlinked_surveys and publishes it
* shows the file in openlayers as it is updated

## Sub-project: convert all old scans to PDF format (completed)

2021-12-16 Final run of scripts to create finished files.

The older scans were in various formats including TIFF, JPEG, and PDF right now.

After converting them all to PDF,
I had to generate a script that would build a new service for WebMaps.

The scripts/ folder contains the Python code

### Method

I ended up using two passes, first I try to use ImageMagick
to convert files to PDF because generally it produced smaller files.

Then I wanted to write some metadata and the easiest way was using GDAL.

Since a few files could not be converted in the first pass, there
is also some code to try to convert those files with GDAL.

### Set up on Windows

(I needed ArcPy and could not get it to run on Linux. So I used Windows.)

I had to install the full Windows ImageMagick package and I made sure "magick" is on the command PATH
so in convert_image_files.py, it can just call magick via subprocess.
Using magick in a conda module did not work.

Every attempt today at creating a clean environment failed today. (11/5/21)
Falling back to cloning. Geez.

I have to have separate Conda environments on Windows, one for Esri and one for GDAL.

FIXME: TODAY 12/21/21 I could not use the 'surveys' but the one for 'arcgis_tools' worked. ??

```bash
conda update --all
conda config --remove channels conda-forge
conda config --add channels esri

conda create -n surveys arcgis pandas sqlalchemy pyodbc requests
conda activate surveys
conda install autopep8 ipykernel
```

Today I had to edit my ~/bin/condarc file to get rid of the esri channel, not sure why

```bash
conda config --add channels conda-forge
conda config --remove channels esri
conda create -n gdal gdal
conda activate gdal
conda install autopep8 ipykernel
```

### Source image files

My image files are all currently found in
/cifs/cc-files01/Applications/SurveyorData/survey/Scanned\ Surveys/AA_INDEXED_SURVEYS
so I just set that in scripts/config.py.

### Workflow

1 Set conda environment to 'magick'

2 Run convert_image_files.py to convert and or copy files to PDF format

3 Set conda environment to 'gdal'

4 Run update_metadata.py to fix up the metadata and copy any missing files from #2.

5 Fix the database table Clatsop.dbo.SurveyImages

This file is versioned. The easiest way to do this step is to use
"Calculate Field" inside ArcPro. Here is some python.

```python
import os
def fn(file):
  ext=['.jpg', '.tif', 'tiff']
  for e in ext:
      if file.lower().endswith(e):
          f = file[-len(e)]
          return f += '.pdf'
  return file
```
