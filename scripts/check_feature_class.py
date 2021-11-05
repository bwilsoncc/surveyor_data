#!/usr/bin/env -S conda run -n magick
#
#  Report on the state of the surveyor data.
#
import os
from arcgis.gis import GIS
from arcgis.features import FeatureLayer, FeatureSet, Feature, Table

from utils import get_files, get_ext_dict
from config import Config

if __name__ == "__main__":

    portal = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    layer = FeatureLayer(Config.SURVEYS_URL, gis=portal)
    fields = "*"
    df = layer.query(where="1=1", out_fields=fields, out_sr=3857).sdf
    print(df)

    # Output will be written here
    outputfolder = os.path.abspath(Config.TARGET)
    assert(outputfolder)

    os.chdir(Config.SOURCE)
    matched, ignored = get_files('.')

    # Read every row from the surveys feature class
    # What's missing from the survey documents?
    # Build a dict of docs
    d = dict()
    for file in matched:
        pass
    # What docs are not referenced from the survey feature class?
    for file in matched:
        pass

# That's all!
