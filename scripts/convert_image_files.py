#!/usr/bin/env -S conda run -n magick
#
#  Convert images to PDF format.
#
import os, sys
from pgmagick import Image
import shutil

from utils import get_files
from config import Config

if __name__ == "__main__":

    # Output will be written here
    outputfolder = os.path.abspath(Config.TARGET)
    assert(outputfolder)

    os.chdir(Config.SOURCE)
    l, d, ignored = get_files('.')
    print("ignored", len(ignored))
    print(ignored)

    total_files = 0
    for e in d:
        length = len(d[e])
        print(e, length)
        total_files += length

    errors = 0
    error_msg = list()
    progress = 0
    for pathname in l:
        progress += 1

        assert(os.path.exists(pathname))

        path,file = os.path.split(pathname)
        f,e = os.path.splitext(file)

        outputpath = os.path.join(outputfolder, path)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        # I find it very difficult to leave trailing spaces
        # on filenames, it's just weird to have those.
        # and yet it's what I do
        outputfile = os.path.join(outputpath, f + '.pdf')
#        stripped = f.strip()
#        if f != stripped:
#            # Remove ones that were created by an earlier version
#            if os.path.exists(outputfile):
#                os.unlink(outputfile)
#            outputfile = os.path.join(outputpath, stripped + '.pdf')
        
        if os.path.exists(outputfile):
            # If the file exists, it better have size > 0
            # else we try to copy it again.
            stats = os.lstat(outputpath)
            if stats.st_size > 0:
                continue
            os.unlink(outputfile)

        if e.lower() == '.pdf': 
            # Just copy this file, it's already in PDF format
            print("%d/%d Copying \"%s\"." % (progress, total_files, pathname))
            shutil.copyfile(pathname, outputfile)
            continue

        print("%d/%d Converting \"%s\"." % (progress, total_files, pathname))
        try:
            im = Image()
            # ignore the message about this tag
            # I have not gotten this to work but
            # the CreateCopy in update_metadata.py does fix it
            im.defineValue("Tiff", "ignore-tags=32934")
            im.read(pathname)
            im.write(outputfile)
        except Exception as e:
            print(">>>--------ERROR--------->", e)
            error_msg.append("\"%s\" \"%s\"" % (outputfile, e))
            errors += 1
            continue

    print("Errors:", errors)
    for e in error_msg:
        print(e)

    print("Completed.")
# That's all
