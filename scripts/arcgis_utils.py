
import os, sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode
import arcpy
from arcgis.gis import GIS
from config import Config

# RTFM
# https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/introduction-to-arcpy-sharing.htm

def create_service_definition(aprx_map, sdname, folder=""):
    """ 
        Using a map from ArcGIS Pro project, 
        create a new SDDraft
        use the draft to create a new SD file.

        Input:  aprx_map is a map object from an APRX project
                sdname is the service definition name
                folder (optional) destination folder on the server
        Output: files: a service draft and a service definition

        Returns: complete path for SD file or None
    """
    path, name = os.path.split(sdname)
    service_name, ext = os.path.splitext(name)
    sddraft = os.path.join(path, service_name + ".sddraft")

    arcpy.env.overwriteOutput = True

    """Current version."""
    # This call is ONLY for "STANDALONE_SERVER" (no federation allowed!!!)
    """sharing_draft = arcpy.sharing.CreateSharingDraft('STANDALONE_SERVER', 'MAP_SERVICE', service_name, aprx_map)
    sharing_draft.targetServer = ags_file"""
    
    # You can include a list of layers here, and then you can omit services or add some that aren't in the AGP map.
    sharing_draft = aprx_map.getWebLayerSharingDraft('FEDERATED_SERVER', 'MAP_IMAGE', service_name)
    sharing_draft.federatedServerUrl = Config.SERVER_URL # required!

    # FAIL: You can't write a MAP_IMAGE to a HOSTING_SERVER
    #sharing_draft = aprx_map.getWebLayerSharingDraft('HOSTING_SERVER', 'TILE', service_name)
    #sharing_draft.portalUrl = Config.PORTAL_URL # required!

    # All these are optiona;
    sharing_draft.portalFolder = folder
    sharing_draft.serverFolder = folder
    sharing_draft.summary = ''
    sharing_draft.tags = 'TEST'
    sharing_draft.credits = ''
    sharing_draft.description = ''
    sharing_draft.copyDataToServer = True
    sharing_draft.overwriteExistingService = True
    #sharing_draft.offline = False
    #sharing_draft.useLimitations = False

    # In theory this writes the XML file we're looking for.
    sharing_draft.exportToSDDraft(sddraft)

    # I wish I could do an "Analyze" step here

    try:
        print("Converting XML sddraft to sdfile \"%s\"." % sdname)
        arcpy.StageService_server(sddraft, sdname)
    except Exception as e:
        print("Staging failed:", e)
        return False

    return True

def update_service_definition(gis, sd, service_name):

    print("Searching for original SD \"%s\" on portal…" % service_name)
    query = "{} AND owner:{}".format(service_name, Config.PORTAL_USER)
    try:
        sdItem = gis.content.search(query, item_type="Service Definition")[0]
    except Exception as e:
        print("Could not find service definition for \"%s\"." % service_name, e)
        return None

    try:
        print("Found SD: {}, ID: {} Uploading and overwriting…".format(sdItem.title, sdItem.id))
        sdItem.update(data=sd)
    except Exception as e:
        print("Could not update service definition.", e)
        return None

    try:
        print("Overwriting service…")
        fs = sdItem.publish(overwrite=True)
    except Exception as e:
        print("Could not overwrite sercvice")
        return None

#    try:
#        if shrOrg or shrEveryone or shrGroups:
#            print("Setting sharing options…")
#            fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
#    except Exception as e:
#        print("Could set permissions for \"%s\"." % service_name, e)
#        return None

    print("Finished updating: {} ID: {}".format(fs.title, fs.id))
    return fs.title

if __name__ == '__main__':

    service_name = 'Hyperlinked_Surveys'
    sdfile = os.path.join("C:\\Temp", service_name + '.sd')

    prjPath  = "K:/webmaps/basemap/basemap.aprx"
    ags_file = "K:/webmaps/basemap/server (publisher).ags"
    
    folder = 'TESTING_Brian'
    title  = 'Hyperlinked Surveys'

    # Find the map we want in the ArcGIS Pro project.
    project = arcpy.mp.ArcGISProject(prjPath)
    maps = project.listMaps()
    map = None
    for item in maps:
        if item.name == "arcgis_utils unit test":
            map = item
            break
    if map:
        print("Map found in %s." % prjPath)
    else:
        sys.exit("No map found in %s" % prjPath)


    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    if not os.path.exists(sdfile):
        create_service_definition(map, sdfile, folder)

    # First I try to update an existing definition.
    # If that fails then I create a new one...

    if update_service_definition(gis, sdfile, service_name):
        print("Service definition has been updated.")

    else:
        print("Uploading definition using \"%s\" %s" % (ags_file, folder))

        # Upload the service definition to SERVER 
        # In theory everything needed to publish the service is already in the SD file.
        # https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
        # You can override permissions, ownership, groups here too.
        try:
            # In theory ags_file could be Config.SERVER_URL but then where does it get authenticated?
            # arcpy.server.UploadServiceDefinition(sdname, ags_file, in_startupType="STARTED")
            # in_startupType HAS TO BE "STARTED" else no service is started on the SERVER.

            rval_signin = arcpy.SignInToPortal(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
            rval_upload = arcpy.server.UploadServiceDefinition(sdfile, ags_file, in_startupType="STARTED")
        except Exception as e:
            print("Upload failed.", e)



    print("Unit tests completed.")
