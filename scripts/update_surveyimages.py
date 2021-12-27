#
#  Update the SurveyImages table, 
#  this is just the Python version of the Powershell script. But better of course
# 
#  1 build a list of new or updated docs by looking in the filesystem and comparing with the database table
#  2 look for entries in SurveyImages.
#     if found, update timestamp
#     else append a new entry
#
from utils import get_files_df
from config import Config

def search_fstable(files_df):
    print(files_df)
    d = dict()
    return d

def update_docs():
    return

if __name__ == "__main__":


    files_df = get_files_df(Config.SOURCE)
    search_fstable(files_df)

    update_docs()
