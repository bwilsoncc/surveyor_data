import os

class Config(object):
    # Linux
    # server = '/cifs/cc-files01/Applications/'
    # Windows 
    server = '//cc-files01/Applications/'
    SOURCE = server + "SurveyorData/survey/Scanned Surveys/AA_INDEXED_SURVEYS"
    TARGET = server + 'GIS/PublicWorks/Survey/PDF'
    # Testing
#    SOURCE = "./Pictures"
#    TARGET = "./PDF"

    PORTAL_URL = "https://delta.co.clatsop.or.us/portal"
    PORTAL_USER     = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")
    SURVEYS_URL = "https://delta.co.clatsop.or.us/server/rest/services/Surveys2/FeatureServer/0"

    SDE_CONNECTION = "K:/webmaps/basemap/cc-gis.sde"

    assert(len(PORTAL_USER))
    assert(len(PORTAL_PASSWORD))
