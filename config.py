import os
#from dotenv import load_dotenv
#load_dotenv()

class Config(object):
    # Linux
    # server = '/cifs/cc-files01/Applications/'
    # Windows 
    fileserver = '//cc-files01/Applications/'
    SOURCE = "I:/SurveyorData/survey/Scanned Surveys/AA_INDEXED_SURVEYS"
    TARGET = "K:/PublicWorks/Survey/PDF"
    # Testing
#    SOURCE = "./Pictures"
#    TARGET = "./PDF"

    PORTAL_URL      = "https://delta.co.clatsop.or.us/portal"
    PORTAL_USER     = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")
    PORTAL_APP_ID   = os.environ.get("PORTAL_APP_ID")
    PORTAL_APP_SECRET = os.environ.get("PORTAL_APP_SECRET")
    SERVER_URL      = "https://delta.co.clatsop.or.us/server"

    SDE_CONNECTION = "K:/webmaps/basemap/cc-gis.sde"
    SDE_USER       = os.environ.get("SDE_USER")
    SDE_PASSWORD   = os.environ.get("SDE_PASSWORD")
    DB_INSTANCE    = os.environ.get('DB_INSTANCE')
    DATABASE       = os.environ.get('DATABASE')
    SURVEYS_URL    = "https://delta.co.clatsop.or.us/surveys/"

    WORKSPACE = "K:\\webmaps\\basemap\\Basemap.gdb"

assert(len(Config.PORTAL_USER))
assert(len(Config.PORTAL_PASSWORD))
assert(len(Config.PORTAL_APP_ID))
assert(len(Config.PORTAL_APP_SECRET))
