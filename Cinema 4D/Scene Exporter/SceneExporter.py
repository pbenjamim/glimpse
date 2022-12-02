from typing import Optional
from pathlib import Path
import c4d
import os

doc: c4d.documents.BaseDocument # The document evaluating this tag
op: c4d.BaseTag # The Python scripting tag
flags: int # c4d.EXECUTIONFLAGS
priority: int # c4d.EXECUTIONPRIORITY
tp: Optional[c4d.modules.thinkingparticles.TP_MasterSystem] # Particle system
thread: Optional[c4d.threading.BaseThread] # The thread executing this tag

# GLOBAL VARIABLES - These must always have these values
AddExportSetButtonID = 3;
ExportAllExportSetsButtonID = 4;
DeleteAllExportSetsButtonID = 5;

# Class for encapsulating user data elements
class ExportSet:
    def __init__(self, exportSetUserDataList):
        if len(exportSetUserDataList) != 9:
            print("Error: exportSetUserDataList length is not 9")
            pass

        # Each element in the exportSetUserDataList is a tuple:
        # [0] contains DescID, [1] contains the container
        # [0][1].id contains ID, [0][1].dtype contains DTYPE
        self.Set = exportSetUserDataList[0];
        self.ReadyToExport = exportSetUserDataList[1];
        self.Delete = exportSetUserDataList[2];
        self.Settings = exportSetUserDataList[3];
        self.SelectionSet = exportSetUserDataList[4];
        self.Version = exportSetUserDataList[5];
        self.Destination = exportSetUserDataList[6];
        self.Format = exportSetUserDataList[7];
        self.FormatSettings = exportSetUserDataList[8];
        #self.Presets = exportSetUserDataList[9];

        pass

# Main function, called when anything happens apparently
def main() -> None:

    #nullObject = op.GetObject();
    #userDataContainer = nullObject.GetUserDataContainer();

    #addOrRemoveSelectionSet = userDataContainer[1];
    #addButton = userDataContainer[2];
    #deleteAllButton = userDataContainer[3];
    #exportButton = userDataContainer[-1];

    pass

# Function that receives button press events
def message(msg_type, data):
    if msg_type == c4d.MSG_NOTIFY_EVENT:
        event_data = data['event_data']
        if event_data['msg_id'] == c4d.MSG_DESCRIPTION_COMMAND:
            desc_id = event_data['msg_data']['id'];
            HandleMessage(desc_id[1].id);

# Handle button press events
def HandleMessage(id):
    global AddExportSetButtonID;
    global DeleteAllExportSetsButtonID;
    global ExportAllExportSetsButtonID;

    nullObject = op.GetObject();
    userDataContainer = nullObject.GetUserDataContainer();
    exportSets = ScanExportSets(userDataContainer);

    # If "Add" button pressed:
    if id == AddExportSetButtonID:
        # Get parent container to attach new ExportSet to
        addOrRemoveSelectionSet = userDataContainer[1];

        # Create new ExportSet
        newExportSet = NewExportSet(len(exportSets) + 1, nullObject, addOrRemoveSelectionSet[0]);

        # If "Export" button pressed
    elif id == ExportAllExportSetsButtonID:
        ExportSelectionSets(exportSets, nullObject);

    # If "Delete All" button pressed
    elif id == DeleteAllExportSetsButtonID:
        # Get all ExportSets
        exportSets = ScanExportSets(userDataContainer);
        for exportSet in exportSets:
            DeleteExportSet(exportSet, nullObject);

    else:
        # Find the matching ExportSet of the button
        for exportSet in exportSets:

            # If "Format Settings" button pressed
            if id == exportSet.FormatSettings[0][1].id:

                # Get selected Format option and open Preferences Window on the Format's Export page
                option = nullObject[c4d.ID_USERDATA, exportSet.Format[0][1].id];

                # .abc
                if option == 0:
                    prefsPageToOpen = c4d.FORMAT_ABCEXPORT;
                # .fbx
                elif option == 1:
                     prefsPageToOpen = c4d.FORMAT_FBX_EXPORT;
                # .obj
                elif option == 2:
                    prefsPageToOpen = c4d.FORMAT_OBJ2EXPORT;

                c4d.PrefsLib_OpenDialog(prefsPageToOpen);

            # Delete button pressed
            elif id == exportSet.Delete[0][1].id:
                DeleteExportSet(exportSet, nullObject);

    pass

# Exports all "Ready" Selection Sets
def ExportSelectionSets(exportSets, nullObject):
    activeDoc = c4d.documents.GetActiveDocument();

    for exportSet in exportSets:
        if  nullObject[c4d.ID_USERDATA, exportSet.ReadyToExport[0][1].id] == False:
            continue;

        pickedObject = nullObject[c4d.ID_USERDATA, exportSet.SelectionSet[0][1].id];

        if(pickedObject == None):
            print("Picked object is not a Selection Object");
            return

        selectionObjectList = pickedObject[c4d.SELECTIONOBJECT_LIST];

        # Contains no objects
        if(selectionObjectList == None):
            return

        # Get objects contained in selection object
        objects = [];
        for idx in range(selectionObjectList.GetObjectCount()):
            objects.append(selectionObjectList.ObjectFromIndex(activeDoc, idx));

        # For each object
        for obj in objects:
            ExportObject(exportSet, obj, nullObject);

    activeDoc.SetActiveObject(nullObject, c4d.SELECTION_NEW);
    pass

def ExportObject(exportSet, objectToExport, nullObject):
    # Get exportation path:
    # With current GL_Project folder structure, just go up 1 dir,
    # enter 06_caches and enter abc/fbx/obj
    activeDoc = c4d.documents.GetActiveDocument();
    docDir = activeDoc.GetDocumentPath();
    exportDir = docDir + "\\..\\06_caches";
    selectedFormat = nullObject[c4d.ID_USERDATA, exportSet.Format[0][1].id];

    # .abc
    if selectedFormat == 0:
        exportDir += "\\abc";
        fileExtention = ".abc";
        exportFormat = c4d.FORMAT_ABCEXPORT;
    # .fbx
    elif selectedFormat == 1:
         exportDir += "\\fbx";
         fileExtention = ".fbx";
         exportFormat = c4d.FORMAT_FBX_EXPORT;
    # .obj
    elif selectedFormat == 2:
        exportDir += "\\obj";
        fileExtention = ".obj";
        exportFormat = c4d.FORMAT_OBJ2EXPORT;

    selectedDestination = nullObject[c4d.ID_USERDATA, exportSet.Destination[0][1].id];
    destinationDir = "\\";

    # to Max
    if selectedDestination == 0:
        destinationDir += "toMax";
    # to C4d
    elif selectedDestination == 1:
        destinationDir += "toC4d";
    # to Hou
    elif selectedDestination == 2:
        destinationDir += "toHou";
    # to Maya
    elif selectedDestination == 3:
        destinationDir += "toMaya";
    # to Blender
    elif selectedDestination == 4:
        destinationDir += "toBlender";

    exportDir += destinationDir;

    # Get a fresh, temporary document with only the selected object (in a list)
    docTemp = c4d.documents.IsolateObjects(activeDoc, [objectToExport]);

    # If directory does not exist, create the dir
    if os.path.isdir(exportDir) == False:
        #print("Export directory does not exist, creating...");
        Path(exportDir).mkdir(parents=True, exist_ok=True);

    #TODO PLUGIN PRESET RESEARCH
    """
    plugins = c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_SCENESAVER, True)
    for plug in plugins:
        print(plug.GetID())

    FBX EXPORTER is no 9
    """

    # Calculate version string
    version =  nullObject[c4d.ID_USERDATA, exportSet.Version[0][1].id];
    versionString = "";

    if (version < 10):
        versionString = "v00" + str(version)
    elif (version < 100):
        versionString = "v0" + str(version)
    else:
        versionString = "v" + str(version)

    # Get object file name
    docName = activeDoc.GetDocumentName();
    docNameTokens = docName.split("_");

    if len(docNameTokens) != 5:
        print("Error: Document name is invalid");
        return

    objFileName = docNameTokens[0] + "_" + docNameTokens[1] + "_" + docNameTokens[2] + "_" + objectToExport.GetName() + "_" + versionString + fileExtention;

    #print("Exporting to " + exportDir + "\\" + objFileName)

    # Export it
    if c4d.documents.SaveDocument(docTemp, exportDir + "\\" + objFileName, c4d.SAVEDOCUMENTFLAGS_NONE, exportFormat) == False:
        print("Could not export object " + objFileName);
    else:
        print("Exported object " + objectToExport.GetName());

    # Destroy temp document
    c4d.documents.KillDocument(docTemp);
    c4d.EventAdd();
    pass

# Scans for all current export sets in the UI, returns list
def ScanExportSets(userDataContainer):
    # Skip first 5 elements (2 title bars and 3 buttons)
    totalExportSetUserDataList = userDataContainer[5:]

    if len(totalExportSetUserDataList) % 9 != 0:
        print("Error: totalExportSetUserDataList length is not multiple of 9")
        pass

    setCount = int(len(totalExportSetUserDataList) / 9);

    # Parse data in sets of 10 for each ExportSet
    exportSets = []
    for idx in range(setCount):
        startIdx = idx*9;
        endIdx = (idx+1)*9;
        exportSetUserDataList = totalExportSetUserDataList[startIdx:endIdx];
        exportSets.append(ExportSet(exportSetUserDataList))

    return exportSets

# Creates a new ExportSet UserData
def NewExportSet(setNumber, nullObject, parentGroupDescID):
    newExportUserDataList = [];

    # NOTE: Order of objects in list is important!
    # Create new UserData: create BaseContainer, get DescID, add it to nullObject
    # then, add the tuple with (DescID, BaseContainer) to list for creating ExportSet class instance
    setContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_GROUP);
    readyToExportContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BOOL);
    deleteContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BUTTON);
    settingsContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_GROUP);
    selectionSetContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BASELISTLINK);
    versionContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_LONG);
    destinationContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_LONG);
    formatContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_LONG);
    formatSettingsContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BUTTON);
    #presetsContainer = c4d.GetCustomDataTypeDefault(c4d.DTYPE_LONG);

    setContainer[c4d.DESC_NAME] = "Set " + str(setNumber);
    setContainer[c4d.DESC_SHORT_NAME] = "Set " + str(setNumber);
    setContainer[c4d.DESC_GUIOPEN] = False;
    setContainer[c4d.DESC_TITLEBAR] = False;
    setContainer[c4d.DESC_COLUMNS] = 2;

    readyToExportContainer[c4d.DESC_NAME] = "Ready to Export";
    readyToExportContainer[c4d.DESC_SHORT_NAME] = "Ready to Export";
    readyToExportContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;

    deleteContainer[c4d.DESC_NAME] = "Delete";
    deleteContainer[c4d.DESC_SHORT_NAME] = "Delete";
    deleteContainer.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_BUTTON);

    settingsContainer[c4d.DESC_NAME] = "Settings";
    settingsContainer[c4d.DESC_SHORT_NAME] = "Settings";
    settingsContainer[c4d.DESC_GUIOPEN] = False;
    settingsContainer[c4d.DESC_TITLEBAR] = False;
    settingsContainer[c4d.DESC_COLUMNS] = 2;

    selectionSetContainer[c4d.DESC_NAME] = "Selection Set";
    selectionSetContainer[c4d.DESC_SHORT_NAME] = "Selection Set";
    selectionSetContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;

    versionContainer[c4d.DESC_NAME] = "Version";
    versionContainer[c4d.DESC_SHORT_NAME] = "Version";
    versionContainer[c4d.DESC_STEP] = 1;
    versionContainer[c4d.DESC_MIN] = 1;
    versionContainer[c4d.DESC_MINEX] = False;
    versionContainer[c4d.DESC_MAX] = 999;
    versionContainer[c4d.DESC_MAXEX] = False;
    versionContainer[c4d.DESC_DEFAULT] = 1;
    versionContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;

    destinationContainer[c4d.DESC_NAME] = "Destination";
    destinationContainer[c4d.DESC_SHORT_NAME] = "Destination";
    destinationContainerValues = c4d.BaseContainer();
    destinationContainerValues[0] = "toMax";
    destinationContainerValues[1] = "toC4d";
    destinationContainerValues[2] = "toHou";
    destinationContainerValues[3] = "toMaya";
    destinationContainerValues[3] = "toBlender";
    destinationContainer[c4d.DESC_CYCLE] = destinationContainerValues;
    destinationContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;

    formatContainer[c4d.DESC_NAME] = "Format";
    formatContainer[c4d.DESC_SHORT_NAME] = "Format";
    formatContainerValues = c4d.BaseContainer();
    formatContainerValues[0] = ".abc";
    formatContainerValues[1] = ".fbx";
    formatContainerValues[2] = ".obj";
    formatContainer[c4d.DESC_CYCLE] = formatContainerValues;
    formatContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;

    formatSettingsContainer[c4d.DESC_NAME] = "Format Settings";
    formatSettingsContainer[c4d.DESC_SHORT_NAME] = "Format Settings";
    formatSettingsContainer.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_BUTTON);

    #presetsContainer[c4d.DESC_NAME] = "Preset";
    #presetsContainer[c4d.DESC_SHORT_NAME] = "Preset";
    #presetsContainer[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF;
    # TODO figure out how this is supposed to work
    #presetsContainerValues = c4d.BaseContainer();
    #presetsContainerValues[0] = "default";
    #presetsContainerValues[1] = "cam";
    #presetsContainerValues[2] = "anim_geo";
    #presetsContainerValues[2] = "static_geo";
    #presetsContainer[c4d.DESC_CYCLE] = presetsContainerValues;
    # TODO Check if this is needed
    #presetsContainer[c4d.DESC_DEFAULT] = 0;

    # Order must be maintained here... be careful
    setContainer[c4d.DESC_PARENTGROUP] = parentGroupDescID;
    setContainerDescID = nullObject.AddUserData(setContainer);

    readyToExportContainer[c4d.DESC_PARENTGROUP] = setContainerDescID;
    deleteContainer[c4d.DESC_PARENTGROUP] = setContainerDescID;
    settingsContainer[c4d.DESC_PARENTGROUP] = setContainerDescID;
    readyToExportContainerDescID = nullObject.AddUserData(readyToExportContainer);
    deleteContainerDescID = nullObject.AddUserData(deleteContainer);
    settingsContainerDescID = nullObject.AddUserData(settingsContainer);

    selectionSetContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    versionContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    destinationContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    formatContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    formatSettingsContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    #presetsContainer[c4d.DESC_PARENTGROUP] = settingsContainerDescID;
    selectionSetContainerDescID = nullObject.AddUserData(selectionSetContainer);
    versionContainerDescID = nullObject.AddUserData(versionContainer);
    destinationContainerDescID = nullObject.AddUserData(destinationContainer);
    formatContainerDescID = nullObject.AddUserData(formatContainer);
    formatSettingsContainerDescID = nullObject.AddUserData(formatSettingsContainer);
    #presetsContainerDescID = nullObject.AddUserData(presetsContainer);

    newExportUserDataList.append((setContainerDescID, setContainer));
    newExportUserDataList.append((readyToExportContainerDescID, readyToExportContainer));
    newExportUserDataList.append((deleteContainerDescID, deleteContainer));
    newExportUserDataList.append((settingsContainerDescID, settingsContainer));
    newExportUserDataList.append((selectionSetContainerDescID, selectionSetContainer));
    newExportUserDataList.append((versionContainerDescID, versionContainer));
    newExportUserDataList.append((destinationContainerDescID, destinationContainer));
    newExportUserDataList.append((formatContainerDescID, formatContainer));
    newExportUserDataList.append((formatSettingsContainerDescID, formatSettingsContainer));
    #newExportUserDataList.append((presetsContainerDescID, presetsContainer));

    c4d.EventAdd();
    return ExportSet(newExportUserDataList);

# Deletes an Export Set from User Data
def DeleteExportSet(exportSet, nullObject):
    #nullObject.RemoveUserData(exportSet.Presets[0]);
    nullObject.RemoveUserData(exportSet.FormatSettings[0]);
    nullObject.RemoveUserData(exportSet.Format[0]);
    nullObject.RemoveUserData(exportSet.Destination[0]);
    nullObject.RemoveUserData(exportSet.Version[0]);
    nullObject.RemoveUserData(exportSet.SelectionSet[0]);
    nullObject.RemoveUserData(exportSet.Settings[0]);
    nullObject.RemoveUserData(exportSet.Delete[0]);
    nullObject.RemoveUserData(exportSet.ReadyToExport[0]);
    nullObject.RemoveUserData(exportSet.Set[0]);

    #del(nullObject[exportSet.Presets[0]]);
    del(nullObject[exportSet.FormatSettings[0]]);
    del(nullObject[exportSet.Format[0]]);
    del(nullObject[exportSet.Destination[0]]);
    del(nullObject[exportSet.Version[0]]);
    del(nullObject[exportSet.SelectionSet[0]]);
    del(nullObject[exportSet.Settings[0]]);
    del(nullObject[exportSet.Delete[0]]);
    del(nullObject[exportSet.ReadyToExport[0]]);
    del(nullObject[exportSet.Set[0]]);

    c4d.EventAdd(c4d.EVENT_FORCEREDRAW);

    # TODO for some reason C4D will not refresh the user data. I have no idea why.
    """
    # Refresh Set numbers
    nullObject = op.GetObject();
    userDataContainer = nullObject.GetUserDataContainer();
    exportSets = ScanExportSets(userDataContainer);

    print("BEFORE");
    setCounter = 0;
    for eS in exportSets:
        setCounter += 1;
        #print(eS.Set[1][c4d.DESC_NAME])
        #print(nullObject[c4d.ID_USERDATA, eS.Set[0][1].id])
        eS.Set[1][c4d.DESC_NAME] = "Set " + str(setCounter);
        #eS.Set[1].SetString(c4d.DESC_NAME, "Set " + str(setCounter));

        #print(eS.Set[1][c4d.DESC_NAME]);
        eS.Set[1][c4d.DESC_SHORT_NAME] = "Set " + str(setCounter);
        #eS.Set[1].SetString(c4d.DESC_SHORT_NAME, "Set " + str(setCounter));

    c4d.EventAdd(c4d.EVENT_FORCEREDRAW);

    print("AFTER");
    for eS in exportSets:
        print(eS.Set[1][c4d.DESC_NAME]);
    """

    pass