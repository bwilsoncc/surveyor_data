import os, sys
import arcpy
from arcgis.gis import GIS
from urllib.parse import urlencode
from config import Config


def find_map(aprx, map_name):
    project = arcpy.mp.ArcGISProject(aprx)
    maps = project.listMaps()
    map = None
    for item in maps:
        if item.name == map_name:
            return item
    return None


def create_service_definition(map, service_type, service_name, 
        tags="", portal_folder="", server_folder="", copy_to_server=True):
    """ 
        Using a map from ArcGIS Pro project, 
        create a new sddraft file
        and use the draft to create a new SD file.

        Input:  aprx_map is a map object from an APRX project
                sd_name is the service definition name
                folder (optional) destination folder on the server
        Output: files: a service draft and a service definition

        Returns: complete path for SD file or None
    """
    global tmp_path
    sddraft_name = os.path.join(tmp_path, service_name + ".sddraft")

    arcpy.env.overwriteOutput = True

    # I just want to publish the first layer, not the entire map.
    # You can include a list of layers here, and then you can omit services or add some that aren't in the AGP map.
    # Sample code https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-F529AD9A-B0D9-477A-9464-BB61F5747323
    all_layers = map.listLayers()
    selected_layers = [all_layers[0]]

    if service_type == 'MAP_IMAGE':
        server_type = 'FEDERATED_SERVER' 
        # This fails if you pass it a list of layers. It's not supposed to...
        sddraft = map.getWebLayerSharingDraft(server_type, service_type, service_name)
        sddraft.federatedServerUrl = Config.SERVER_URL # REQUIRED!!
    elif service_type == 'FEATURE':
        server_type = 'HOSTING_SERVER'
        sddraft = map.getWebLayerSharingDraft(server_type, service_type, service_name, selected_layers)
    else:
        raise Exception("Huh? service_type = %s" % service_type)

    # All these are optional
    sddraft.overwriteExistingService = True
    sddraft.portalFolder = portal_folder
    sddraft.serverFolder = server_folder 
    sddraft.summary = ''
    sddraft.tags = tags
    sddraft.credits = ''
    sddraft.description = ''
    sddraft.copyDataToServer = copy_to_server
    #sddraft.offline = False
    #sddraft.useLimitations = False

    # This writes the *.sddraft file to C:\TEMP.
    sddraft.exportToSDDraft(sddraft_name)

    # This uses the sddraft and writes the *.sd file.
    try:
        sd_name = os.path.join(tmp_path, service_name + '.sd')
        result = arcpy.server.StageService(sddraft_name, sd_name)
    except Exception as e:
        print("Staging failed:", e)
        return None

    return sd_name


def update_service_definition(gis, sd, service_name):
    try:
        sd.update(data=sd)
    except Exception as e:
        print("Could not update service definition.", e)
        return None
    try:
        print("Overwriting service…")
        fs = sd.publish(overwrite=True)
    except Exception as e:
        print("Could not overwrite \"%s\"." % sd, e)
        return None
    try:
        if shrOrg or shrEveryone or shrGroups:
            print("Setting sharing options…")
            fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
    except Exception as e:
        print("Could not set permissions for \"%s\"." % service_name, e)
        return None
    print("Finished updating: {} ID: {}".format(fs.title, fs.id))
    return fs.title


def publish(map, service_name, service_type, copy=True):
    global tmp_path, ags_file
    rval = False

    print("Searching server for SD to overwrite. \"%s\" on portal…" % service_name)
    # This protects other users' content
    query = "{} AND owner:{}".format(service_name, Config.PORTAL_USER)   
    existing_sd = None
    try:
        existing_sd = gis.content.search(query, item_type="Service Definition")[0]
        print("Found SD: {}, ID: {} Uploading and overwriting…".format(
            existing_sd.title, existing_sd.id))
    except Exception as e:
        print("No service definition matched \"%s\". Creating a new one." % query, e)
    if existing_sd:
        update_service_definition(gis, existing_sd, service_name)
        print("Service definition has been updated.")
        rval = True
        return rval

    tags = "Clatsop County, Public Works, Surveys"
    sd_file = create_service_definition(map, service_type, service_name, tags,
                                portal_folder, server_folder,
                                copy_to_server=copy)

    print("Uploading service definition")
    # Upload the service definition to SERVER
    # In theory everything needed to publish the service is already in the SD file.
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
    # You can override permissions, ownership, groups here too.
    try:
        msg = arcpy.server.UploadServiceDefinition(
            sd_file, ags_file, in_startupType="STARTED")
        # in_startupType HAS TO BE "STARTED" else no service is started on the SERVER.
        n = 0
        for m in msg:
            if m:
                print(n, m)
            n += 1
        rval = True
    except Exception as e:
        print("Upload failed.", e)
            
    return rval


if __name__ == "__main__":

    prj_path = "K:/webmaps/basemap/basemap.aprx"
    ags_file = "K:/webmaps/basemap/server (publisher).ags"

    assert os.path.exists(prj_path)
    assert os.path.exists(ags_file)

    webmap_name = 'Surveys PopUp Test'
    share_org = True
    share_everyone = True
    share_groups = 'GIS Team'

    portal_folder = "Public Works"
    server_folder = "Public_Works" 

    tmp_path = 'C:\\temp'

    # Sign in to arcgis and to arcpy
    arcpy.SignInToPortal(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    # Find the map we want in the ArcGIS Pro project.
    map_name = "Surveys"
    map = find_map(prj_path, map_name)
    if not map:
        sys.exit("No map \"%s\" found in %s" % (map_name, prj_path))

    publish(map, 'Surveys_HOSTED_MIL', 'MAP_IMAGE', copy=True)
    publish(map, 'Surveys_HOSTED_FEATURES', 'FEATURE', copy=True)

# The data for the first layer in map has to be registered for this to work.
    map_name = "Surveys_Registered"
    map = find_map(prj_path, map_name)
    if not map:
        sys.exit("No map \"%s\" found in %s" % (map_name, prj_path))
    publish(map, 'Surveys_MIL', 'MAP_IMAGE', copy=False)
