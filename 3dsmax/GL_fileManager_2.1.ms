-- FOR FUTURE DIR STRUCT CHANGES:
/*
	Change scan functions and open functions, that's it!
*/

-- FUTURE: combine scanShots and scanAssets into one!

-- FUTURE: warnings!

/*
macroScript GL_fileManager
category:"Glimpse_VFX"
buttonText:"GL_fileManager"
toolTip:"GL_fileManager"
(*/

-- encase in "global" block
(
------------------------------------------------[ GLOBAL VARIABLES ]-------------------------------------------------

local GL_Drives = #("K:", "W:")
local GL_Departments = #("layout","anim","model","rig","fx","lgt","print")
local GL_AssetTypes = #("scene", "chars", "env", "props")

------------------------------------------------[ FORWARD FUNCTION DECLARATIONS ]-------------------------------------------------
local inArray
local desc

local scanFolders
local scanMaxFiles 
local scanShots
local scanAssets

local getAssetName
local getMenuTag
local getNewVersion
local getMenuDepartment
local getMenuProject
local getMenuProjectPath
local getFilters
local getFilteredMaxfiles
local getSelectionFilepath

local refreshYears
local refreshProjects
local refreshMaxfiles
local refreshFilters

local newMaxFile
local newVersion

local openMaxfile
local openFileExplorer
local openProjectExplorer

local initPreSelect

------------------------------------------------[ INTERFACE CODE ]------------------------------------------------
gc()

try(destroydialog GLFM)catch()

rollout GLFM "Glimpse File Manager v2.1" width:(588+150) height:390
(
	radiobuttons Drives ""  align:#left labels:GL_Drives

	dropdownList Years "Year"  width:96 align:#left items:#()

	multiListBox Projects "Project"  width:175 height:22 align:#left items:#()
	multiListBox FileFilters "" pos:[200,86] width:150 height:22 items:#()
	multiListBox Maxfiles ""  pos:[200+150,86] width:241 height:22 items:#()
	multiListBox Departments ""  pos:[452+150,115] width:123 height:9 items:GL_Departments
	radiobuttons AssetTypes ""  pos:[199,68] labels:GL_AssetTypes

	button Create_BTN "Create"  pos:[451+150,274] width:125 height:35 border:true
	button Open_BTN "Open"  pos:[451+150,309] width:125 height:35
	button Version_BTN "Version Up"  pos:[451+150,344] width:125 height:35

	edittext Filename_EDT ""  pos:[448+150,87] width:127 height:21 text:""
	edittext Tag_EDT ""  pos:[448+150,246] width:127 height:21 text:"main" bold:false readOnly:false

------------------------------------------------[ EVENTS ]------------------------------------------------

	on Drives changed idx do (
		refreshYears()
		refreshProjects()
	)

	on Years selected idx do (
		refreshProjects()
	)

	on Projects selectionEnd do (
		refreshMaxfiles()
		refreshFilters()
	)

	on AssetTypes changed idx do (
		local projSelect = (Projects.selection as array)
		if (projSelect.count == 1) then (
			refreshMaxfiles()
			refreshFilters()
		)
	)

	on Maxfiles selectionEnd do (
		Filename_EDT.text = getAssetName( Maxfiles.items[(Maxfiles.selection as array)[1]] )
	)

	on FileFilters selectionEnd do (
		refreshMaxfiles()

		local filter = FileFilters.items[(FileFilters.selection as array)[1]]
		Maxfiles.items = getFilteredMaxfiles Maxfiles.items filter
	)

	on Filename_EDT changed nameText do (
		local textLength = nameText.count
		if (nameText[textLength] == "_") then (
			Filename_EDT.text = substring nameText 1 (textLength-1)
		)
		Maxfiles.selection = 0)

	on Tag_EDT changed tagText do (
		local textLength = tagText.count
		if (tagText[textLength] == "_") then (
			Tag_EDT.text = substring tagText 1 (textLength-1)
		)
	)

	on Create_BTN pressed do (
		-- Run only if a department was selected in the menus
		local depSelection = (Departments.selection as array)
		if (depSelection.count == 1) then (
			newMaxFile()
			refreshMaxfiles()
			refreshFilters()
		)
	)

	on Version_BTN pressed do (
		-- If max has a file opened...
		if(maxFilePath != "") then (
			newVersion()
			refreshMaxfiles()
			refreshFilters()
		)
	)

	on Open_BTN pressed do (
		-- Run only if a file was selected in the menus
		local fileSelection = (Maxfiles.selection as array)
		if (fileSelection.count == 1) then ( openMaxfile() )
	)

	on Maxfiles doubleClicked idx do (
		-- Run only if a file was selected in the menus
		local fileSelection = (Maxfiles.selection as array)
		if (fileSelection.count == 1) then ( openMaxfile() )
	)

	on Projects rightClick do (
		-- Run only if a project was selected in the menus
		local projSelection = (Projects.selection as array)
		if (projSelection.count == 1) then ( openProjectExplorer() )
	)

	on Maxfiles rightClick do (
		-- Run only if a file was selected in the menus
		local fileSelection = (Maxfiles.selection as array)
		if (fileSelection.count == 1) then ( openFileExplorer() )
	)

)

------------------------------------------------[ UTILITY FUNCTIONS ]------------------------------------------------

-- returns 0 if obj not in array, otherwise returns its index on the array
fn inArray array obj = (
	local result = 0
	if(array.count <= 0) then (
		result = 0
		)
	else (
		for i=1 to array.count do (
			if (array[i] == obj) then (
				result = i
				return result
				)
			)
		)
	result)

-- rsort: aux function to sort arrays in descending order
fn desc v1 v2 = (
	local d = (v1 as Integer) - (v2 as Integer)
	case of (
		(d > 0): -1
		(d < 0): 1
		default: 0
		)
	)

-- returns all folders in a given path/folder (just the name)
fn scanFolders path = (
	local folders = #()
	local dirs = getDirectories(path + "\\*")
	local dirsCount = dirs.count
	local depth = 0
	if (dirsCount > 0) then (
		depth = (FilterString dirs[1] "\\").count
	)
	local i = 1
	while(i <= dirsCount) do (
		local folder = FilterString dirs[i] "\\" -- #("C:", "2018", "Vodafone")
		append folders folder[depth]
		i = i + 1
		)
	i = 1

	-- Return value
	folders)

-- returns all maxfilenames in a given path 
fn scanMaxFiles path = (
	local filePaths = getFiles (path + "\\*.max")
	local files = #()
	if (filePaths.count > 0) then (
		local separatorAux = FilterString filePaths[1] "\\"
		local separatorCount = separatorAux.count

		for i=1 to filePaths.count do (
			local fFilePath = FilterString filePaths[i] "\\"
			local file = fFilePath[separatorCount]
			append files file
			)
		)
	-- Return value
	files)

-- returns all maxfilenames of shots for a given project
fn scanShots path = (
	local shotsFolders = scanFolders(path + "\\30_shots")
	local shots = #()
	for i = 1 to shotsFolders.count do (
		shots = shots + scanMaxFiles(path + "\\30_shots\\" + shotsFolders[i] + "\\03_scenes")
	)
	shots)

-- returns all maxfilenames of assets for a given project

-- separated(chars[], env[], props[])
fn scanAssets path = (
	local assetTypeFolders = scanFolders(path + "\\20_assets")
	local assets = #()

	for i = 1 to assetTypeFolders.count do (
		local assetFolders = scanFolders(path + "\\20_assets\\" + assetTypeFolders[i])

		local typeAssets = #()

		for j = 1 to assetFolders.count do (
			typeAssets = typeAssets + (scanMaxFiles(path + "\\20_assets\\" + assetTypeFolders[i] + "\\" + assetFolders[j] + "\\03_scenes"))
		)
		append assets typeAssets
		typeAssets = #()
	)
	assets)

------------------------------------------------[ MAIN FUNCTIONS ]------------------------------------------------
fn getAssetName fullname = (
	local typeIdx = GLFM.AssetTypes.state
	local result = ""
	local fName = FilterString fullname "_"

	-- SCENE
	if (typeIdx == 1) then (
		result = fName[2]
		)
	else (
		result = fName[3]
		)

	-- return value
	result)

fn getMenuTag = (
	local tagText = GLFM.Tag_EDT.text
	if (tagText == "main" or tagText == "") then (
		-- return value
		"_main"
		)
	else (
		-- return value
		("_" + tagText)
		)
	)

fn getNewVersion oldVersion = (
	local result = ""
	local newVersion = oldVersion + 1

	if (newVersion < 10) then (
		result = "00" + (newVersion as string)
		)
	else (
		if (newVersion < 100) then (
			result = "0" + (newVersion as string)
			)
		else (
			result = (newVersion as string)
			)
		)

	-- return value
	result)

fn getMenuDepartment = (
	( GLFM.Departments.items[(GLFM.Departments.selection as array)[1]] )
)

-- returns selected project name
fn getMenuProject = (
	( GLFM.Projects.items[(GLFM.Projects.selection as array)[1]] )	
)

-- returns selected project path
fn getMenuProjectPath = (
	(GL_Drives[GLFM.Drives.state] + "\\" + GLFM.Years.selected + "\\" + getMenuProject() )
)

-- from a list of file names, get a list of filters
fn getFilters files = (
	local ffilters = #()
	for i=1 to files.count do (
		filteredFile = filterstring files[i]  "_"

		if(GLFM.AssetTypes.state == 1) then (
			appendIfUnique ffilters filteredFile[2]
		)
		else (
			appendIfUnique ffilters filteredFile[3]
		)
	)
	ffilters
)

fn getFilteredMaxfiles files filter = (
	local result = #()
	local idx

	if(GLFM.AssetTypes.state == 1) then (idx = 2)
	else (idx = 3)


	for i=1 to files.count do (
		filtered = FilterString files[i] "_"

		if not (filtered[idx] != filter ) then (
			append result files[i]
		)
	)

	result
)

fn getSelectionFilepath = (
	local year = GLFM.Years.selected
	local projectPath = getMenuProjectPath()

	local fullpath

	-- shot file
	if(GLFM.AssetTypes.state == 1) then (
		local filename = GLFM.Maxfiles.items[(GLFM.Maxfiles.selection as array)[1]]
		fullpath = projectPath + "\\30_shots\\" + (getAssetName filename) + "\\03_scenes\\"
	)
	-- asset file
	else (
		local filename = GLFM.Maxfiles.items[(GLFM.Maxfiles.selection as array)[1]]
		local assetType = GL_AssetTypes[GLFM.AssetTypes.state]
		fullpath = projectPath + "\\20_assets\\" + assetType + "\\" + (getAssetName filename) + "\\03_scenes\\"
	)

	fullpath
)

fn refreshYears = (
	local yearFolders = #()
	local aux = scanFolders (GL_Drives[GLFM.Drives.state])
	for i=1 to aux.count do (
		if((aux[i] as integer) != undefined) then (
			appendIfUnique yearFolders aux[i]
		)
	)

	qsort yearFolders desc
	GLFM.Years.items = yearFolders
	GLFM.Years.selection = 1
)

fn refreshProjects = (
	GLFM.Projects.items = scanFolders (GL_Drives[GLFM.Drives.state] + "\\" + GLFM.Years.selected)

	GLFM.Projects.selection = 0
	GLFM.Maxfiles.items = #()
	GLFM.Filename_EDT.text = ""
)

-- refresh max files in the menu (depends on chosen file type (e.g scene, prop, env))
fn refreshMaxfiles = (
	local year = GLFM.Years.selected
	local project = getMenuProject()

	if(GLFM.AssetTypes.state == 1) then (
		GLFM.Maxfiles.items = scanShots (getMenuProjectPath())
	)
	else (
		GLFM.Maxfiles.items = (scanAssets(getMenuProjectPath()))[GLFM.AssetTypes.state - 1]
	)
	GLFM.Maxfiles.selection = 0
	GLFM.Filename_EDT.text = ""
)

fn refreshFilters = (
	GLFM.FileFilters.items = getFilters (GLFM.Maxfiles.items)
	GLFM.FileFilters.selection = 0
)

fn newMaxFile = (
	local type = GLFM.AssetTypes.state
	-- project tag is the last token of filterstring "_"
	local fProject = FilterString (getMenuProject()) "_"
	local projectTag = fProject[fProject.count]

	local saveDir
	local saveName 
	-- if shot
	if (type == 1) then (
		saveDir = getMenuProjectPath() + "\\30_shots\\" + GLFM.Filename_EDT.text
		saveName = projectTag + "_" +  GLFM.Filename_EDT.text + "_" + getMenuDepartment() + "_v001" + getMenuTag() + ".max"
	)
	else (
		saveDir = getMenuProjectPath() + "\\20_assets\\" + GL_AssetTypes[type] + "\\" + GLFM.Filename_EDT.text
		saveName = projectTag + "_" + GL_AssetTypes[type] + "_" + GLFM.Filename_EDT.text + "_" + getMenuDepartment() + "_v001" + getMenuTag() + ".max"
	)

	if not(doesFileExist saveDir) then (makeDir saveDir)

	if not(doesFileExist (saveDir + "\\01_misc"))    then (makeDir (saveDir + "\\01_misc"))
	if not(doesFileExist (saveDir + "\\02_refs"))    then (makeDir (saveDir + "\\02_refs"))
	if not(doesFileExist (saveDir + "\\03_scenes"))  then (makeDir (saveDir + "\\03_scenes"))
	if not(doesFileExist (saveDir + "\\04_tex"))     then (makeDir (saveDir + "\\04_tex"))
	if not(doesFileExist (saveDir + "\\05_sims"))    then (makeDir (saveDir + "\\05_sims"))

	if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches"))

	if(type == 1) then (
		if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\assets"))
		if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\fx"))
	)
	else (
		if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\abc"))
		if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\fbx"))
		if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\obj"))
	)

	if not(doesFileExist (saveDir + "\\06_caches"))  then (makeDir (saveDir + "\\06_caches\\proxies"))

	if not(doesFileExist (saveDir + "\\07_renders")) then (makeDir (saveDir + "\\07_renders"))
	if(type == 1) then (
		if not(doesFileExist (saveDir + "\\07_renders")) then (makeDir (saveDir + "\\07_renders\\misc"))
	)
	if not(doesFileExist (saveDir + "\\08_comp"))    then (makeDir (saveDir + "\\08_comp"))

	if not(doesFileExist (saveDir + saveName)) then (saveMaxFile (saveDir + "\\03_scenes\\" + saveName)))

fn newVersion = (
	local filepath = maxFilePath
	local filename = maxFileName

	local fFilename = FilterString filename "_"

	-- "v001"
	local versionTok = fFilename[fFilename.count - 1]
	local oldVersion = (substring versionTok 2 4) as integer
	local newVer = "v" + getNewVersion oldVersion

	fFilename[fFilename.count - 1] = newVer

	local newfilename = ""
	for i=1 to fFilename.count do (
		newfilename = newfilename + fFilename[i]
		if (i < fFilename.count) then (newfilename = newfilename + "_")
	)

	local fullsavepath = filepath + newfilename

	if not (doesFileExist fullsavepath) then (saveMaxFile fullsavepath)
)

fn openMaxfile = (
	local filename = GLFM.Maxfiles.items[(GLFM.Maxfiles.selection as array)[1]]
	loadMaxFile (getSelectionFilepath() + filename)
)

fn openFileExplorer = (
	ShellLaunch "explorer.exe" (getSelectionFilepath())
)

fn openProjectExplorer = (
	ShellLaunch "explorer.exe" (getMenuProjectPath())
)
------------------------------------------------[ ENTRY POINT ]-------------------------------------------------

-- default init
fn init = (
	refreshYears()
	refreshProjects()

	if (maxFilePath != undefined and maxfilepath != "") then (
		initPreSelect()
	)
)


-- init the rollout and pre select the file that is opened
fn initPreSelect = (
	
	local maxFilt = FilterString maxFilePath "\\"
	-- Step 1: choose drive
	if(maxFilt[1] == GL_Drives[1]) then (
		GLFM.Drives.state = 1
	)
	else if (maxFilt[1] == GL_Drives[2]) then (
		GLFM.Drives.state = 2
	)
	refreshYears()
	refreshProjects()

	-- Step 2: year
	GLFM.Years.selection = (inArray GLFM.Years.items maxFilt[2])
	refreshProjects()

	-- Step 3: project
	GLFM.Projects.selection = #{(inArray GLFM.Projects.items maxFilt[3])}
	refreshMaxfiles()
	refreshFilters()

	-- Step 4: Asset Type
	local name_filt = FilterString maxFileName "_"
	if(maxFilt[4] == "30_shots") then (
		GLFM.AssetTypes.state = 1
	)
	else (
		if(name_filt[2] == GL_AssetTypes[2]) then (GLFM.AssetTypes.state = 2)
		if(name_filt[2] == GL_AssetTypes[3]) then (GLFM.AssetTypes.state = 3)
		if(name_filt[2] == GL_AssetTypes[4]) then (GLFM.AssetTypes.state = 4)
	)
	local projSelect = (GLFM.Projects.selection as array)
	if (projSelect.count == 1) then (
		refreshMaxfiles()
		refreshFilters()
	)

	-- Step 5: Choose file

	GLFM.Maxfiles.selection = #{(inArray GLFM.Maxfiles.items maxFileName)}
	GLFM.Filename_EDT.text = getAssetName( GLFM.Maxfiles.items[(GLFM.Maxfiles.selection as array)[1]] )

	-- Step 6: Choose department
	local dep
	if(GLFM.AssetTypes.state == 1) then (
		dep = name_filt[3]
	)
	else (
		dep = name_filt[4]
	)

	GLFM.Departments.selection = #{(inArray GL_Departments dep)}
)

CreateDialog GLFM

init()

) -- end of "global" block

/*)