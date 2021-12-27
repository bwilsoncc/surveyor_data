#!/usr/bin/env -S conda run -n gdal
#
#  Update the metadata on each converted file.
#  If any files are missing, first try to create them with GDAL.
#
#  2021-12-16 
#  I used to write metadata to every file but quit doing that today.
#  See "update" variable to change it back
#
import os
import osgeo.gdal as gdal
from utils import get_files, get_ext_dict
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
    matched, ignored = get_files('.')
    print("extensions of ignored files: ", get_ext_dict(ignored))

    format = 'PDF'
    driver = gdal.GetDriverByName(format)
    print(driver.LongName)

    now = datetime.now()

    errors = 0
    error_msg = list()
    total_files = len(matched)
    progress = 0
    converted = 0
    copied = 0
    updated = 0
    for pathname in matched:
        progress += 1
        fullpath = os.path.join(source, pathname)
        assert(os.path.exists(pathname))

        path,file = os.path.split(pathname)
        f,e = os.path.splitext(file)

        outputpath = os.path.join(outputfolder, path)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        # If you write nonstandard headers here then GDAL will create an *.aux.xml file

        update = True

        my_metadata = {
            'TITLE': f, 
            'SUBJECT': 'File converted from "%s"' % fullpath
        }

        if e.lower() == '.pdf': 
            # This is an existing copy of the PDF
            # Don't update it
            my_metadata = {
                'TITLE': f, 
                'SUBJECT': 'File copied from "%s"' % fullpath
            }
            update = False
            copied += 1
        else:
            converted += 1

        outputfile = os.path.join(outputpath, f + '.pdf')

        if not os.path.exists(outputfile):
            # ImageMagick failed to convert this doc
            # so let's try again with GDAL.
            ds = gdal.Open(pathname, gdal.GA_ReadOnly)
            driver.CreateCopy(outputfile, ds, 0)
            del ds
        elif ONLY_NEW:
            continue

        if update:
            # Open file in UPDATE mode and fix up the metadata.       
            ds = gdal.Open(outputfile, gdal.GA_Update)
            if not ds:
                # If GDAL also fails to copy, you'll get this error.
                errors += 1
                error_msg.append("Error: no file \"%s\"." % outputfile)
                continue

            old_metadata = ds.GetMetadata()
            
            ds.SetMetadata(my_metadata)
            del ds
            print("%d/%d Updated \"%s\"." % (progress, total_files, file))
            updated += 1

    print("Errors:", errors)
    for e in error_msg:
        print(e)

    print("Converted %d Copied %d Updated %d" % (converted, copied, updated))
    print("Completed.")
# That's all
