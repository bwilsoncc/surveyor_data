#!/usr/bin/env -S conda run -n gdal
#
#  Update the metadata on each PDF file.
#  If any files are missing, first try to create them with GDAL.
#
import os
import osgeo.gdal as gdal
from utils import get_files
from datetime import datetime
from config import Config

if __name__ == "__main__":

    # If true ONLY process files that don't exist in the output.
    # Use this to update only files that could not be processed
    # in convert_image_files
    ONLY_NEW = False

    # Output will be written here
    outputfolder = os.path.abspath(Config.TARGET)
    assert(outputfolder)

    source = Config.SOURCE
    os.chdir(source)
    l, d, ignored = get_files('.')
    print("ignored", len(ignored))
    print(ignored)

    format = 'PDF'
    driver = gdal.GetDriverByName(format)
    print(driver.LongName)

    total_files = 0
    for e in d:
        length = len(d[e])
        print(e, length)
        total_files += length

    now = datetime.now()

    progress = 0
    errors = 0
    error_msg = list()

    for pathname in l:
        progress += 1
        fullpath = os.path.join(source, pathname)
        assert(os.path.exists(pathname))

        path,file = os.path.split(pathname)
        f,e = os.path.splitext(file)

        outputpath = os.path.join(outputfolder, path)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        # If you write nonstandard headers here then GDAL will create an *.aux.xml file

        my_metadata = {
            'TITLE': f, 
            'SUBJECT': 'File converted from "%s"' % fullpath,
            'PRODUCER': 'Clatsop County GIS Services <gisinfo@co.clatsop.or.us>',
        }

        if e.lower() == '.pdf': 
            # This is an existing copy of the PDF
            my_metadata = {
                'TITLE': f, 
                'SUBJECT': 'File copied from "%s"' % fullpath,
                'PRODUCER': 'Clatsop County GIS Services <gisinfo@co.clatsop.or.us>',
            }

        # Open file in UPDATE mode and fix up the metadata.
        outputfile = os.path.join(outputpath, f + '.pdf')
        if not os.path.exists(outputfile):
            # ImageMagick failed to convert this doc
            # so let's try again with GDAL.
            ds = gdal.Open(pathname, gdal.GA_ReadOnly)
            driver.CreateCopy(outputfile, ds, 0)
            del ds
        elif ONLY_NEW:
            continue

        ds = gdal.Open(outputfile, gdal.GA_Update)
        if not ds:
            # If GDAL also fails to copy, you'll get this error.
            errors += 1
            error_msg.append("Error: no file \"%s\"." % outputfile)
            continue

        old_metadata = ds.GetMetadata()
        
        ds.SetMetadata(my_metadata)
        del ds
        print("%d/%d Updated \"%s\"." % (progress, total_files, outputfile))

    print("Errors:", errors)
    for e in error_msg:
        print(e)

    print("Completed.")
# That's all
