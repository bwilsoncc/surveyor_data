import os, sys
import arcpy
from arcgis.gis import GIS
from urllib.parse import urlencode
from config import Config

def create_service_definition(aprx_map, service_type, sd_name, tags="", portal_folder="", server_folder="", overwrite=True):
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
    path, name = os.path.split(sd_name)
    service_name, ext = os.path.splitext(name)
    sddraft_name = os.path.join(path, service_name + ".sddraft")

    arcpy.env.overwriteOutput = True

    if service_type == 'MAP_IMAGE':
        # "MAP IMAGE LAYER" -- This will include all the layers in the map.
        server_type = 'FEDERATED_SERVER' 
        sddraft = aprx_map.getWebLayerSharingDraft(server_type, service_type, service_name)
        sddraft.federatedServerUrl = Config.SERVER_URL # REQUIRED!!
    else: 
        # service_type = 'FEATURE'
        # "FEATURE SHARING" -- This will include all the layers in the map.
        # You can include a list of layers here, and then you can omit services or add some that aren't in the AGP map.
        # sample code https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-F529AD9A-B0D9-477A-9464-BB61F5747323
        server_type = 'HOSTED_SERVER'

        # I just want to publish the first layer, not the entire map.
        all_layers = aprx_map.listLayers()
        selected_layer = all_layers[0]

        sddraft = aprx_map.getWebLayerSharingDraft(server_type, service_type, service_name, [selected_layer])

    # All these are optional
    sddraft.overwriteExistingService = overwrite
    sddraft.portalFolder = portal_folder
    sddraft.serverFolder = server_folder 
    sddraft.summary = ''
    sddraft.tags = tags
    sddraft.credits = ''
    sddraft.description = ''
    sddraft.copyDataToServer = True
    #sddraft.offline = False
    #sddraft.useLimitations = False

    # This writes the *.sddraft file to C:\TEMP.
    sddraft.exportToSDDraft(sddraft_name)

    # This uses the sddraft and writes the *.sd file.
    try:
        print("Building sdfile \"%s\"." % sd_name)
        arcpy.server.StageService(sddraft_name, sd_name)
    except Exception as e:
        print("Staging failed:", e)
        return False

    return True

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
        print("Could not overwrite \"%s\"." % sd_name, e)
        return None
    try:
        if shrOrg or shrEveryone or shrGroups:
            print("Setting sharing options…")
            fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
    except Exception as e:
        print("Could set permissions for \"%s\"." % service_name, e)
        return None
    print("Finished updating: {} – ID: {}".format(fs.title, fs.id))
    return fs.title


if __name__ == "__main__":

    prj_path  = "K:/webmaps/basemap/basemap.aprx"
    ags_file = "K:/webmaps/Basemap_PRO/server (publisher).ags"
    map_name = "Surveys"

    service_name = "Surveys"
    webmap_name = 'Surveys PopUp Test'
    share_org = True
    share_everyone = True
    share_groups = 'GIS Team'

    portal_folder = "Public Works"
    server_folder = "Public_Works" 

    tmp_path = 'C:\\temp'

    # Find the map we want in the ArcGIS Pro project.
    project = arcpy.mp.ArcGISProject(prj_path)
    maps = project.listMaps()
    map = None
    for item in maps:
        if item.name == map_name:
            map = item
            break

    # Sign in to arcgis and to arcpy
    arcpy.SignInToPortal(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    if not map:
        map_names = [map.name for map in maps]
        #print('\n'.join(map_names))
        print("All these did I search, and yet found nothing!", '\n'.join(map_names))
        sys.exit("No map \"%s\" found in %s" % (map_name, prj_path))

    print("Searching for SD to overwrite. \"%s\" on portal…" % service_name)
    query = "{} AND owner:{}".format(service_name, Config.PORTAL_USER) # This protects other users' content
    existing_sd = None
    try:
        existing_sd = gis.content.search(query, item_type="Service Definition")[0]
        print("Found SD: {}, ID: {} Uploading and overwriting…".format(existing_sd.title, existing_sd.id))
    except Exception as e:
        print("No service definition matched \"%s\". Creating a new one." % query, e)

    overwrite = False
    sd_name = os.path.join(tmp_path, service_name + '.sd')
    
    service_type = "FEATURE"

    if overwrite or not os.path.exists(sd_name):
        tags = "Clatsop County, Public Works, Surveys"
        create_service_definition(map, service_type, sd_name, tags, 
            portal_folder, server_folder, 
            overwrite=(existing_sd!=None))

    # I think updating when possible might preserve the GUID on the Portal?
    if existing_sd:
        update_service_definition(gis, existing_sd, service_name)
        print("Service definition has been updated.")
    else:
        print("Uploading service definition")
        # Upload the service definition to SERVER 
        # In theory everything needed to publish the service is already in the SD file.
        # https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
        # You can override permissions, ownership, groups here too.
        try:
            msg = arcpy.server.UploadServiceDefinition(sd_name, ags_file, in_startupType="STARTED")
            # in_startupType HAS TO BE "STARTED" else no service is started on the SERVER.
            n = 0
            for m in msg:
                if m: print(n, m)
                n += 1
        except Exception as e:
            print("Upload failed.", e)
    
    service = Config.SERVER_URL + '/rest/services/' 
    if server_folder:
        service += server_folder + "/"
    service += service_name + '/MapServer'
    print("Map Image published successfully - ", service)

