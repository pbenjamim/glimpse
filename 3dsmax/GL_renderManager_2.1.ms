/** /
macroScript GL_renderManager
category:"Glimpse_VFX"
buttonText:"GL_RenderManager"
toolTip:"GL_RenderManager"
(
/**/

-- Render Master 2.1

-- fix version : get from render and not from file name


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
	result
)

-- get the project directory
fn glvfx_getproject = (
	local aux = FilterString maxfilepath "\\"
	local result = aux[1] + "\\" + aux[2] + "\\" + aux[3] + "\\"
	--return
	result
)

fn glvfx_getfiletag = (
	local aux = FilterString maxfilename "\_"
	local aux2 = FilterString aux[aux.count] "\."
	
	local result = aux2[1]
	--return value
	result
)

fn glvfx_getrenderver item = (
	local aux = FilterString item "\_"
	local result = (FilterString aux[aux.count] "\.")[1]
	--return value
	result
)

-- get the shot folder for currently opened file
fn glvfx_getshot = (
	local aux = FilterString maxfilename "_"
	local result = aux[1] + "_" + aux[2] + "_" + aux[3]
	--return
	result
	)

-- get all the shots for the project
fn glvfx_getshots = (
	local shots_path = glvfx_project + "\\30_shots\\"
	local aux_dirs = getDirectories(shots_path + "\*")
	
	local result = #()
	if(aux_dirs.count <= 0) then (
		messagebox "No shots found for selected project!" title:"Warning!"
	)
	else (
		for i=1 to aux_dirs.count do (
			local aux_files = getFiles (aux_dirs[i] + "\\03_scenes\\" + "\*.max")

			for j=1 to aux_files.count do (
				local filt_aux = FilterString aux_files[j] "\\"
				local filt_aux2 = FilterString filt_aux[filt_aux.count] "_"
				local aux = filt_aux2[1] + "_" + filt_aux2[2] + "_" + filt_aux2[3]
				appendIfUnique result aux
			)
		)
	)

	--return
	result
)

fn glvfx_getrendersdir = (
	local shotname = (FilterString maxFileName "_")[2]
	local result = glvfx_project + "30_shots\\" + shotname + "\\07_renders"
	--return value
	result
)

fn glvfx_getrenders renders_path = (
	local clean_files = #()
	local renders = #()
	local renders_count = #()
	
	local raw_files = #()
	
	local vfolders = getDirectories (renders_path + "\*")
	if( vfolders.count > 0 ) then (
		for i=1 to vfolders.count do (
			local aux = getFiles (vfolders[i] + "\*")
			raw_files = raw_files + aux --concatenate
		)
	)

	--raw_files = getFiles(renders_path + "\*.exr")
	
	
	if(raw_files.count > 0) then (

		-- eliminate the path section of the strings
		for i=1 to raw_files.count do (
			local filt_file = FilterString raw_files[i] "\\"
			append clean_files filt_file[filt_file.count]
		)

		for i=1 to clean_files.count do (
			local filt_render = FilterString clean_files[i] "\."

			local idx = inArray renders filt_render[1]

			if (idx) then (
				renders_count[idx] = renders_count[idx] + 1
			)
			else (
				append renders filt_render[1]
				append renders_count 1
				)
		)
	)

	if(renders_count.count > 0) then (
		for i=1 to renders_count.count do (
			renders_count[i] = renders_count[i] as string
			)
		)
	

	local result = #(renders, renders_count)

	result
)

fn glvfx_getfirstshot renders_path ren = (
	local raw_files = getFiles (renders_path + "\*")
	local clean_files = #()
	local renders = #()
	local renders_count = #()

	if(raw_files.count > 0) then (
		-- eliminate the path section of the strings
		for i=1 to raw_files.count do (
			local filt_file = FilterString raw_files[i] "\\"
			append clean_files filt_file[filt_file.count]
		)

		for i=1 to clean_files.count do (
			local filt_render = FilterString clean_files[i] "\."

			if(ren == filt_render[1]) then (
				return (clean_files[i])
			)
		)

		messagebox "Error: could not find a render to target"
	)

)

------------------------------------------------[ INTERFACE ]------------------------------------------------
	--garbage collection
gc()

--Deadline variables
global SMTDSettings
global SMTDFunctions
global ddl_poollist

-- was local before
global theNetworkRoot = @"\\192.168.3.200\DeadlineRepository10"

-- project path
global glvfx_project

-- array with all shots (just the name)
global glvfx_shots

-- currently opened file's shot
global glvfx_shot

global glvfx_vr

global GL_Render_Master

try(destroydialog GL_Render_Master)catch()
rollout GL_Render_Master "Glimpse Render Manager v2.1" width:850 height:550
(
	edittext edt_preview "Current path"  pos:[30,20] width:750 height:22 labelOnTop:false text:"" bold:true readOnly:true

	multiListBox mlb_shots "Shots"  pos:[30,80] width:250 height:30 items:#()
	multiListBox mlb_renders "Renders"  pos:[310,80] width:250 height:30 align:#left items:#()
	multiListBox mlb_rendercount "#" pos:[565,80] width:30 height:30 align:#left items:#()


	edittext edt_tag "Tag"  pos:[625,175] width:150 labelOnTop:true text:"main" bold:false

	button btn_new "New version"  pos:[625,100] width:150 height:50
	button btn_tag "Apply tag"  pos:[625,215] width:150 height:50 border:true

	button btn_refresh "Refresh" pos:[680,50] width:100 height:30


	-- Deadline Interface
	spinner spn_priority "Priority:" pos:[625, 400] range:[1,100,SMTDSettings.Priority] type:#integer fieldwidth:50 align:#center
-- 	spinner spn_chunkSize "Frames Per Task:" range:[1,100,SMTDSettings.ChunkSize] type:#integer fieldwidth:50
-- 	checkbox chk_limitEnabled "" across:2 checked:SMTDSettings.LimitEnabled
-- 	label lbl_pool "Pool:" pos:[20,40] width:20
	dropdownList ddl_poollist "" pos:[625, 450] width:100 align:#center
-- 	spinner spn_machineLimit "Machine Limit:" range:[1,100,SMTDSettings.MachineLimit] type:#integer fieldwidth:50
	button btn_submit "SUBMIT SCENE" pos:[625, 500] width:190 height:30 align:#center

	------------------------------------------------[ INTERFACE EVENTS ]------------------------------------------------

	on mlb_shots selectionEnd do (
		local idx = (mlb_shots.selection as array)[1]
		local item = mlb_shots.items[idx]

		glvfx_shot = item

		local aux = glvfx_getrenders (glvfx_getrendersdir())

		mlb_renders.items = aux[1]
		mlb_rendercount.items = aux[2]

		if(glvfx_vr.output_rawfilename != undefined) then (
			edt_preview.text = glvfx_vr.output_rawfilename
		)
		else(
			edt_preview.text = "..."
		)
	)

	on mlb_renders selectionEnd do (
		local idx = (mlb_renders.selection as array)[1]
		local item = mlb_renders.items[idx]
		if(glvfx_vr.output_rawfilename != undefined) then (
			edt_preview.text = glvfx_vr.output_rawfilename
		)
		else(
			edt_preview.text = "..."
		)
	)

	on mlb_renders doubleClicked trash_var do (
		local idx = (mlb_renders.selection as array)[1]
		if(idx != undefined) then (
			local item = mlb_renders.items[idx]
			local itemf = filterstring item "_"
			local aux_ver = itemf[itemf.count]
			local aux_tag = itemf[itemf.count - 1]
			
			glvfx_vr.output_rawfilename = glvfx_getrendersdir() + "\\" + aux_tag + "_" + aux_ver  + "\\" + item + ".exr"
			
			edt_preview.text = glvfx_vr.output_rawfilename
		)
	)

	on mlb_renders rightClick do (
		local idx = (mlb_renders.selection as array)[1]
		local target = ""
		if(idx != undefined) then (
			local item = mlb_renders.items[idx]
			local itemf = filterstring item "_"
			local aux_ver = itemf[itemf.count]
			local aux_tag = item[itemf.count - 1]

			target = glvfx_getfirstshot (glvfx_getrendersdir() + "\\" + aux_tag + "_" + aux_ver + "\\")  item

			ShellLaunch "C:\\Program Files\\Pdplayer 64\\pdplayer64.exe" ( glvfx_getrendersdir() + "\\" + aux_tag + "_" + aux_ver + "\\" + target)
		)	
	)

	on btn_refresh pressed do (
		local idx = (mlb_shots.selection as array)[1]

		if not(idx == undefined) then (
			local item = mlb_shots.items[idx]

			local aux = glvfx_getrenders (glvfx_getrendersdir())

			mlb_renders.items = aux[1]
			mlb_rendercount.items = aux[2]

			if(glvfx_vr.output_rawfilename != undefined) then (
				edt_preview.text = glvfx_vr.output_rawfilename
			)
			else(
				edt_preview.text = "..."
			)
		)
	)

	on edt_tag changed nameText do (
		local textLength = nameText.count
		if (nameText[textLength] == "_" or nameText[textLength] == " " or nameText[textLength] == "\t") then (
			edt_tag.text = substring nameText 1 (textLength-1)
		)
	)

	on btn_tag pressed do (
		local filt = FilterString edt_preview.text "_"
		local result = ""

		result = result + filt[filt.count] + ".exr"
			
		local resultf = filterstring edt_preview.text "\\"
		local renderdir = ""
		for i=1 to (resultf.count-2) do (
			renderdir = renderdir + resultf[i] + "\\"
		)
		
		local aux = filterstring resultf[resultf.count-1] "_"
		local newfold = edt_tag.text + "_" + aux[2]
		
		renderdir = renderdir + newfold + "\\"
		
		filt[filt.count-1] = edt_tag.text
		
		for i=1 to (filt.count-1) do (
			result = result + filt[i] + "_"
		)
		
		result = result + filt[filt.count]
		
		local result_auxf = filterstring result "\\"
		local result_aux = result_auxf[result_auxf.count]
		
		local final = renderdir + result_aux
		
		
		if not (doesfileexist renderdir) then (
			makedir renderdir
		)
		
		glvfx_vr.output_rawfilename = final
		edt_preview.text = glvfx_vr.output_rawfilename

		)

	on btn_new pressed do (
		local version = 1
		
		local items = mlb_renders.items
		if (items.count > 0) then (
			local most_recent = 1
			for i=1 to items.count do (
				local itemf = FilterString items[i] "_"
				local vstring = itemf[itemf.count]
				local ver = FilterString vstring "v"
				local ver_int = ver[1] as integer
				if (ver_int > most_recent) then (
					most_recent = ver_int
				)
			)
			
			version = most_recent
			version = version + 1
		)

		local new_version_str
		if(version < 10) then (
			new_version_str = "00" + (version as string)
			)
		else(
			if(version < 100) then (
				new_version_str = "0" + (version as string)
				)
			else(
				if(version < 1000) then (
					new_version_str = version as string
					)
				else (
					messagebox "Exceeded version limit! Cap at v999" title:"Limit reached"
					return false
					)
				)
			)

		result = glvfx_shot +  "_ren_" + glvfx_getfiletag() + "_v" + new_version_str
		
		local newdir = glvfx_getrendersdir() + "\\" + glvfx_getfiletag() + "_v" + new_version_str + "\\"
		if not (doesfileexist newdir) then (
			makeDir newdir
		)

		glvfx_vr.output_rawfilename = newdir + "\\" + result + ".exr"
		
		edt_preview.text = glvfx_vr.output_rawfilename
		)

	on btn_submit pressed do (

		local remoteScript = theNetworkRoot + @"\submission\3dsmax\main\SubmitMaxToDeadline_Functions.ms"  
		local localScript = getDir #userscripts + "\\SubmitMaxToDeadline_Functions.ms"

		if doesFileExist remoteScript do (
			

			if SMTDFunctions == undefined do (
				deleteFile localScript
				copyFile remoteScript localScript
				fileIn localScript
				
			)
			
			local vrayoutputfile=(if (isProperty renderers.current #output_on) then (
				if (renderers.current.output_splitgbuffer) and (renderers.current.output_splitfilename != "") then (
					getFilenameFile renderers.current.output_splitfilename) 
				else if (renderers.current.output_saveRawFile) and (renderers.current.output_rawFileName != undefined) then (
					getFilenameFile renderers.current.output_rawFileName) 
					else if (rendOutputFilename != "") then (
						getFilenameFile rendOutputFilename)
						else "[No save output filenameFile]") 
				else (if (rendOutputFilename != "") then (
					getFilenameFile rendOutputFilename) 
					else "[No save output filenameFile]"))   
	
			SMTDFunctions.loadSettings()
			SMTDSettings.JobName = maxFileName + " [SIMPLE MXS SUBMISSION]"
-- 			SMTDSettings.JobName = vrayoutputfile
			SMTDSettings.PoolName = ddl_poollist.selected
			SMTDSettings.Comment = "Created using the simplest Deadline submission script imaginable."
			SMTDSettings.Priority = spn_priority.value
			--SMTDSettings.ChunkSize = spn_chunkSize.value
			--SMTDSettings.LimitEnabled = chk_limitEnabled.checked
			--SMTDSettings.MachineLimit = spn_machineLimit.value
				

			local maxFileToSubmit = SMTDPaths.tempdir + maxFileName
			SMTDFunctions.SaveMaxFileCopy maxFileToSubmit

			local SubmitInfoFile = SMTDPaths.tempdir + "\\max_submit_info.job"
			local JobInfoFile = SMTDPaths.tempdir+ "\\max_job_info.job"
				
			SMTDFunctions.CreateSubmitInfoFile SubmitInfoFile
			SMTDFunctions.CreateJobInfoFile JobInfoFile

			local initialArgs = "\""+SubmitInfoFile+"\" \""+JobInfoFile+"\" \""+maxFileToSubmit+"\" "

			local result = SMTDFunctions.waitForCommandToComplete initialArgs SMTDSettings.TimeoutSubmission

			local renderMsg = SMTDFunctions.getRenderMessage()
			SMTDFunctions.getJobIDFromMessage renderMsg

			if result == #success then
			(
				format "Submitted successfully as Job %.\n\n%\n\n" \
				
				SMTDSettings.DeadlineSubmissionLastJobID renderMsg
			)
			else
			
			format "Job Submission FAILED.\n\n%" renderMsg

		)--end if
	)--end on button pressed

	------------------------------------------------[ MAIN FUNCTION ]------------------------------------------------

	on GL_Render_Master open do (
		-- project path
		glvfx_project = glvfx_getproject()
		
		-- file tag
		glvfx_filetag = glvfx_getfiletag()
		edt_tag.text = glvfx_filetag

		-- array with all shots (just the name)
		glvfx_shots = glvfx_getshots()

		-- currently opened file's shot
		glvfx_shot = glvfx_getshot()

		mlb_shots.items = glvfx_shots

		/**/
		glvfx_vr = renderers.current
		glvfx_vr.output_saveRawFile = true
		
		if(glvfx_vr.output_rawfilename != undefined) then (
			edt_preview.text = glvfx_vr.output_rawfilename
		)
		else(
			edt_preview.text = "..."
		)
		/**/


		-- pre select currently selected file

		local idx = inArray mlb_shots.items glvfx_shot
		if(idx) then (
			mlb_shots.selection = #{idx}

			local aux = glvfx_getrenders (glvfx_getrendersdir())
				
			mlb_renders.items = aux[1]
			mlb_rendercount.items = aux[2]
		)


		ddl_poollist.items = SMTDSettings.Pools
		local theIndex = findItem ddl_poollist.items SMTDSettings.PoolName
		if theIndex > 0 then (
			ddl_poollist.selection = theIndex 
		)
		else
		(
			theIndex = findItem ddl_poollist.items "none"
			if theIndex > 0 do
			(
				ddl_poollist.selection = theIndex
				SMTDSettings.PoolName = "none"
            --::SMTDFunctions.storeSettingsWithScene()
			)
		)
	)

)

-- If no maxfile is opened, don't even run this bytch
if (maxfilepath == "") then (
	messagebox "No max file opened, closing script." title:"No file opened"
	)
else (
	CreateDialog GL_Render_Master
	)
--)