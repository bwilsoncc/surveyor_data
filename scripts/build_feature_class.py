"""

In Portal, this data was originally published as a query layer (called Surveys2 or Surveys_2)  
with an complex SQL query that was very slow.

Now it's this Pandas dataframe code that no one understands. But it's fast!!

Old workflow: 
Walk the directory tree and build a table
Update SurveyImages table from changes in the directory tree table
Generate the HYPERLINK<n> columns using SQL in a query layer (slow on display)

New workflow:
Walk the directory tree and create a dataframe
Update SurveyImages from the dataframe
Generate a hosted layer that has the HYPERLINK<n> and SURVEY<n> columns in it.
Use the SURVEY<n> attribute in the popup. 
Generating the hosted layer is slowish but rendering it is fast.

VERSIONING - for now I am assuming that this will ignore versioning and use sde.DEFAULT.
An option to use a branch might be nice someday so that the data could be previewed before publishing.

"""
import os
from arcgis.gis import GIS
from arcgis.features import GeoAccessor
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pandas as pd
from requests.utils import requote_uri
import re
from utils import get_files_df
from config import Config

TEST_MODE = False

# test data
survey_df = pd.DataFrame({
    "DocumentNa": ["CS-2039", "Adair"]
})
docs_df = pd.DataFrame({
    "DocumentName":  ["CS-2039", "Adair"],
    "Image":         ["ImageCS", "ImageAdair"]
})


def dbConnect():
    connUrl = URL.create(
        'mssql+pyodbc',
        username=Config.SDE_USER, password=Config.SDE_PASSWORD,
        host=Config.DB_INSTANCE,
        database=Config.DATABASE,
        query={
            "driver": 'SQL SERVER',
        }
    )
    engine = create_engine(connUrl)
    return engine.connect()


def read_docs(connection):
    """
    Return a dataframe containing docs, 
    each row being doc name as a key and a list of files containing the docs we're interested in.
    """

    # In the Powershell code we read CLATSOP.dbo.SURVEY_IMAGES_evw (and I think _evw means this is a view of a version)
    # KEY = DocumentName (eg "CS 13980", "Canona Beach") there can be many with the same document name
    #       Image is an absolute pathname to the associated file
    # but I believe this table is just built by some Powershell code too, after it reads the filesystem
    # and tries to determine what files are new.
    # I don't really care what files are new right now because it takes like 5 seconds longer to generate
    # the entire feature class.
    # Using get_files() also means I don't get any stupid metadata files returned as docs.

    # Yeah but there's no way to relate the key to the file name, 
    # that's being maintained manually

    # docs for using sqlalchemy to access SQL Server
    # https://docs.sqlalchemy.org/en/14/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc

    # NOTE: Traditional version is referencd via a VIEW hence the _evw suffix
    # I don't know what the [brackets] mean here.
    query="SELECT DocumentName,Image from [SURVEYIMAGES_evw]"
    df = pd.read_sql_query(sql=query, con=connection)
    print(df.info(verbose=True))
    return df


def read_surveys(connection):
    """
    Return a data frame containing data from the surveys feature class.

    It's possible to read the DF with sqlalchemy but then it won't have the polygons.
    It's FASTER doing it this way but we need to write a feature class so it won't work.
    """
    key_fields = ['DocumentNa']
    popup_fields = ["SYEAR", "SurveyDate", "Client", "Firm", "SurveyorKe"]
    
    # Via sqlalchemy
    # NOTE: Traditional version is referenced via a VIEW hence the _evw suffix
    # I still don't know what the [brackets] mean here.
#    query = f'SELECT {fields} from [surveys_evw]'
#    df = pd.read_sql_query(sql=query, con=connection)
    
    # Via ArcGIS API
    sde = os.path.join(Config.SDE_CONNECTION, 'surveys')
    df = GeoAccessor.from_featureclass(sde, fields=key_fields + popup_fields)
    
    print(df.info(verbose=True))
    return df


def make_document_dict(df):
    """
        Input is a dataframe with a key ("CS123") and document strings ("Survey/CS123-1")
        Return a dict indexed by the key and containing a list of associated documents.
    """
    re_base = re.compile(r"^.*/AA_INDEXED_SURVEYS/", re.IGNORECASE)
    groups = df.groupby('DocumentNa')
    d = {}
    dupe = 0
    for name,group in groups:
        longimages = group["Image"].tolist()
        
            # Use splitext() to get rid of the unwanted extension
            # Use lower() to ignore camelcased paths, we're using Windows here
            # Get rid of the absolute filepath (basepath)
            # Flip the backslashes because this will be a URL soon.

            # TODO: Using lower() means the output will always be all lower case, which functions but is not aesthetic
            # I should clean the input database instead.
        
        l1 = list()
        lcopy = list()
        for item in longimages:

            # Clean up the file path and make it relative
            img = os.path.splitext(item)[0].replace('\\', '/')
            m = re_base.match(img)
            if m:
                # Trim off the filepath
                img = img[m.end():]
            else:
                print(img)
            if img[-5:] == ' copy':
                if img not in lcopy: # Avoid duplication
                    lcopy.append(img)
                else:
                    dupe +=1
            else:
                if img not in l1: # Avoid duplication
                    l1.append(img)
                else:
                    dupe +=1

        t = (sorted(l1), sorted(lcopy))
        d[name] = t
    print("Deduplication: ", dupe)
    return d

def make_hyperlinks_df(dsurveys):
    """ 
    Turn the messy data dictionary into a tidy dataframe for export. 
    """
    prefix='//clatsop.co.clatsop.or.us/data/applications/surveyordata/survey/scanned surveys/aa_indexed_surveys/'
    lp=len(prefix)

    surveys = list()
    maxlink=0
    for k,images in dsurveys.items():
        link_count = 0
        d = dict()
        d['DocumentNa'] = k

        # Because of my aborted attempt at making multipage PDF files, 
        # there are two lists in "images", one for docs ending in "copy" and one for everything else, 
        # I just glue them together here.
        allimages = images[0] + images[1]

        for baselink in allimages:
            link_count += 1
            name = os.path.split(baselink)[1]
            d['SURVEY%02d' % link_count] = name
            d['HYPERLINK%02d' % link_count] = requote_uri(Config.SURVEYS_URL + baselink + '.pdf')
        maxlink = max(maxlink, link_count)
        d['HYPERLINKS'] = link_count
        surveys.append(d)

    return pd.DataFrame.from_dict(surveys)

def find_updated_docs():
    """
    Someone (e.g. Paul) creates a new document and puts it in the filesystem.
    Walk the filesystem and find all docs, create a dataframe
    Read the SurveyImages table
    Find files that are newer.
    Find files that are not in the table yet. 
    """
    return


if __name__ == "__main__":

    # CLATSOP.dbo.SurveyTable_FromFileSystem
    # this is the equivalent of "get_files", the table is built by walking the directory tree
    files_df = get_files_df(Config.SOURCE)

    # Output will be written here
#    outputfolder = os.path.abspath(Config.TARGET)
#    assert(outputfolder)

    connection = dbConnect()    
    gisconnection = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    docs_df = read_docs(connection)
    survey_df = read_surveys(gisconnection)

    # THIS IS A SLOW STEP! Print every table entry that does not have a corresponding file on the fileserver.
    missing = 0
    for index,row in docs_df.iterrows():
        if not os.path.exists(row.Image):
            print("MISSING FILE: doc \"%s\" file: %s" % (row.DocumentName, row.Image))
            # I should just remove them from the dataframe, most likely...
            missing += 1
    if missing > 0:
        print("There are %d missing files." % missing) # this is a good place for a breakpoint!

    # This is a inner join so it throws away unwanted images
    # (Unwanted = has no polygon associated with it)
    # If I use an outer join instead, then I'd have rows where DocumentNa is NaN meaning documents with no polygon
    # Rows where DocumentName is NaN are polygons with no documents
    #
    # There are 2 (just two) items in surveys with the same DocumentNa
    # so we use a many to many join, resulting in duplication for that one polygon.
    
    xdf = pd.merge(survey_df, docs_df, left_on="DocumentNa", right_on="DocumentName", validate="m:m")

    # Print every entry that has no documents
    no_docs = 0
    for index,row in xdf.iterrows():
        if not row.Image or len(row.Image)<1:
            print("Shape missing a document. %s" % row.DocumentNa)
            no_docs += 1
    if no_docs > 0:
        print("%d shapes are missing docs." % no_docs)  # this is a good place for a breakpoint!

# I am not doing the PDF merge step at this time,
# because Paul asked me not to.
# I am pretty close to being ready to do that but some of the groupings
# in these lists will require more sorting out as there need to be
# multiple docs. For example, consider this batch.
# This would call for two PDF docs to be created, one with 3 pages and one with 2 pages.
#
# Subdivisions_by_Name_All/Adair, John DLC Towns and Subs within B0 P53
# Subdivisions_by_Name_All/Adair, John DLC Towns and Subs within B0 P54
# Subdivisions_by_Name_All/Adair, John DLC Towns and Subs within B0 P55
# Subdivisions_by_Name_All/Adairs Astoria B02 P19
# Subdivisions_by_Name_All/Adairs Astoria B02 P20
    dsurveys = make_document_dict(xdf)
    for docna in dsurveys:
        l1,lcopy = dsurveys[docna]
        if len(l1) + len(lcopy) <= 10:
            continue
        print("doc name: ", docna)
        if len(l1)>1: print("--l1\n", '\n'.join(l1))
        if len(lcopy)>1: print("--lcopy\n", '\n'.join(lcopy))

    hyperdf = make_hyperlinks_df(dsurveys)

    # Now join the original survey polygon data with the links

    sdf = pd.merge(survey_df, hyperdf, on="DocumentNa")
    print(sdf.info(verbose=True))

    # Now what can I do with this df? It should be writable as a feature class right now.
    # Can I send it straight to Portal and skip the geodatabase step?

    fc_filename = os.path.join(Config.WORKSPACE, "hyperlinked_surveys")
    results = sdf.spatial.to_featureclass(fc_filename, overwrite=True)
    print("Wrote to featureclass", results)

    # Write or Overwrite, that is the question?
    

# That's all!
