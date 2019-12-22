"""

Project Structure:
	00_pipeline

	01_client
		from
		to

	05_user
		benji
		romano

	10_preproduction
		concepts
		refs
		rnd
		script

	15_misc
		audio
		comp
		flip
		footage
		hda
		video

	20_assets
		chars
			[name]
				01_misc
				02_refs
				03_scenes
					[scene files]
				04_tex
				05_sims
				06_caches
					abc
					fbx
					obj
					proxies

				07_renders
				08_comp
		env
		props

	25_tex

	30_shots
		[name]
			01_misc
			02_refs
			03_scenes
				backup
				[scene files]
			04_tex
			05_sims
			06_caches
				assets
				fx
				proxies
			07_renders
			08_comp

	40_comp

	50_final

Scene file structure:

Asset:
[Project Tag] _ [Asset Type] _ [Name] _ [Department] _ [Version] _ [Tag] . [extension]

Shot
[Project Tag] _ [Name] _ [Department] _ [Version] _ [Tag] . [extension]

"""

import os
from sys import platform

# [Approach to file system]
# Dynamically read what's there,
# there may be some out-of-control changes so it must adapt!

def getFileFolderPath(file):
	fileTok = file.split("/")
	result = ""
	for i in range(len(fileTok)-1):
		result = result + fileTok[i] + "/"
	return result[:len(result)-1]

############################################
# Year and Project scanning
############################################

# drive: E:, K:, etc..
def getYears(drive):
	folders = os.listdir(drive + "/")
	years = []
	for i in range(len(folders)):
		try:
			year = int(folders[i])
			years.append(folders[i])
			pass
		except ValueError:
			continue
	years.sort(reverse=True)
	return years

def getProjects(path):
	folders = os.listdir(path)
	projects = []
	for i in range(len(folders)):
		folderTok = folders[i].split("_")
		if (len(folderTok) == 4):
			projects.append(folders[i])
	projects.sort(reverse=False)
	return projects

#############################
# Asset getter functions
#############################

def getProjectTag(filename):
	filenameTokens = filename.split("_")
	return filenameTokens[0]

def getAssetName(asset):
	assetTokens = asset.split("_")
	return assetTokens[2]

def getAssetType(asset):
	assetTokens = asset.split("_")
	return assetTokens[1]

def getAssetDepartment(asset):
	assetTokens = asset.split("_")
	return assetTokens[3]

def getAssetTag(asset):
	assetTokens = asset.split("_")
	return (assetTokens[5].split("."))[0]

def getAssetExtension(asset):
	assetTokens = asset.split("_")
	if (len(assetTokens) > 1):
		return (assetTokens[5].split("."))[1]
	else:
		return ""

def getAssetVersion(asset):
	assetTokens = asset.split("_")
	versionTok = assetTokens[4]
	return int(versionTok[1:])

#############################
# Shot getter functions
#############################

def getShotName(shot):
	shotTokens = shot.split("_")
	return shotTokens[1]

def getShotDepartment(shot):
	shotTokens = shot.split("_")
	return shotTokens[2]

def getShotTag(shot):
	shotTokens = shot.split("_")
	return (shotTokens[4].split("."))[0]

def getShotExtension(shot):
	shotTokens = shot.split("_")
	if (len(shotTokens) > 1):
		return (shotTokens[4].split("."))[1]
	else:
		return ""

def getShotVersion(shot):
	shotTokens = shot.split("_")
	versionTok = shotTokens[3]
	return int(versionTok[1:])

################################################
# Name constructor functions
# returns string of the filename to be saved
###############################################

def newShot(projectTag, name, department, tag):
	return projectTag + "_" + name + "_" + department + "_" + "v001" + "_" + tag

def newAsset(projectTag, atype, name, department, tag):
	return projectTag + "_" + atype + "_" + name + "_" + department + "_" + "v001" + "_" + tag

def upVersionAux(version):
	newVersion = version + 1
	if (newVersion < 10):
		return "v00" + str(newVersion)
	elif (newVersion < 100):
		return "v0" + str(newVersion)
	else:
		return "v" + str(newVersion)

def upShotVersion(shot):
	version = upVersionAux(getShotVersion(shot))
	upShot = getProjectTag(shot) + "_" + getShotName(shot) + "_" + getShotDepartment(shot) + "_" + version + "_" + getShotTag(shot)
	return upShot

def upAssetVersion(asset):
	version = upVersionAux(getAssetVersion(asset))
	upAsset = getProjectTag(asset) + "_" + getAssetType(asset) + "_" + getAssetName(asset) + "_" + getAssetDepartment(asset) + "_" + version + "_" + getAssetTag(asset)
	return upAsset

####################################################################
# GL Project container class
####################################################################

class GLProject:

	# rootDir: K:\2019\Project_Name_Example_PNE
	def __init__(self, rootDir):
		self.rootDir = rootDir

		# checking if loading an invalid rootDir
		rootDirTokens = rootDir.split("/")

		if platform != "linux2":
			if(len(rootDirTokens) < 3):
				self.valid = False
				print("[Loading Error] Project directory is invalid!")
				return
			self.drive = rootDirTokens[0]
			self.year = rootDirTokens[1]
			self.name = rootDirTokens[2]
		else:
			if(len(rootDirTokens) < 5):
				self.valid = False
				print("[Loading Error] Project directory is invalid!")
				return
			self.drive = rootDirTokens[0] + "/" + rootDirTokens[1] + "/" + rootDirTokens[2] + "/" + rootDirTokens[3] + "/"
			self.year = rootDirTokens[4]
			self.name = rootDirTokens[5]

		nameTokens = self.name.split("_")

		if(len(nameTokens) < 4):
			self.valid = False
			print("[Loading Error] Project name is invalid!")
			return

		self.tag = nameTokens[3]

		# Validate project structure/folders, etc

		# At the very least, assets and shots folders must exist

		toValidate = 5
		valid = 0

		if (os.path.isdir(rootDir + "/20_assets")): valid += 1
		if (os.path.isdir(rootDir + "/20_assets/chars")): valid += 1
		if (os.path.isdir(rootDir + "/20_assets/env")): valid += 1
		if (os.path.isdir(rootDir + "/20_assets/props")): valid += 1
		if (os.path.isdir(rootDir + "/30_shots")): valid += 1

		self.valid = False
		if(valid == toValidate):
			self.valid = True

	#############################
	# Directory functions
	#############################
	def getAssetsPath(self):
		return self.rootDir + "/20_assets"
	def getCharsPath(self):
		return self.getAssetsPath() + "/chars"
	def getEnvsPath(self):
		return self.getAssetsPath() + "/env"
	def getPropsPath(self):
		return self.getAssetsPath() + "/props"
	def getShotsPath(self):
		return self.rootDir + "/30_shots"

	#############################
	# Name functions
	#############################
	def getCharNames(self):
		return next(os.walk(str(self.getCharsPath())))[1]
	def getEnvNames(self):
		return next(os.walk(str(self.getEnvsPath())))[1]
	def getPropNames(self):
		return next(os.walk(str(self.getPropsPath())))[1]

	def getAssetNames(self):
		chars = self.getCharNames()
		env = self.getEnvNames()
		props = self.getPropNames()
		assets = [chars, env, props]
		return assets

	def getShotNames(self):
		return next(os.walk(str(self.getShotsPath())))[1]

	#############################
	# Scene file functions
	# returns list of scene file names (.max, .hip, etc)
	#############################
	def getScenes(self, names, path):
		scenes = []
		for i in range(len(names)):
			sceneDir = path + "/" + names[i] + "/03_scenes"
			scenes = scenes + os.listdir(sceneDir)
		if "backup" in scenes: scenes.remove("backup")
		return scenes

	def getCharScenes(self):
		return self.getScenes(self.getCharNames(), self.getCharsPath())
	def getEnvScenes(self):
		return self.getScenes(self.getEnvNames(), self.getEnvsPath())
	def getPropScenes(self):
		return self.getScenes(self.getPropNames(), self.getPropsPath())
	def getAssetScenes(self):
		return [self.getCharScenes(), self.getEnvScenes(), self.getPropScenes()]
	def getShotScenes(self):
		return self.getScenes(self.getShotNames(), self.getShotsPath())

	#############################
	# Scene file path functions
	#############################

	def getScenesPath(self, names, path):
		scenesPath = []
		for i in range(len(names)):
			sceneDir = path + "/" + names[i] + "/03_scenes"
			dirFiles = os.listdir(sceneDir)
			for j in range(len(dirFiles)):
				dirFiles[j] = sceneDir + "/" + dirFiles[j]
			scenesPath = scenesPath + dirFiles
		return scenesPath

	def getCharScenesPath(self):
		return self.getScenesPath(self.getCharNames(), self.getCharsPath())
	def getEnvScenesPath(self):
		return self.getScenesPath(self.getEnvNames(), self.getEnvsPath())
	def getPropScenesPath(self):
		return self.getScenesPath(self.getPropNames(), self.getPropsPath())
	def getShotScenesPath(self):
		return self.getScenesPath(self.getShotNames(), self.getShotsPath())

	def getShotHomePath(self, shot):
		return self.getShotsPath() + "/" + getShotName(shot)
	def getCharHomePath(self, char):
		return self.getCharsPath() + "/" + getAssetName(char)
	def getEnvHomePath(self, env):
		return self.getEnvsPath() + "/" + getAssetName(env)
	def getPropHomePath(self, prop):
		return self.getPropsPath() + "/" + getAssetName(prop)

	def getShotPath(self, shot):
		return self.getShotsPath() + "/" + getShotName(shot) + "/03_scenes/" + shot
	def getCharPath(self, char):
		return self.getCharsPath() + "/" + getAssetName(char) + "/03_scenes/" + char
	def getEnvPath(self, env):
		return self.getEnvsPath() + "/" + getAssetName(env) + "/03_scenes/" + env
	def getPropPath(self, prop):
		return self.getPropsPath() + "/" + getAssetName(prop) + "/03_scenes/" + prop

	#############################
	# Creation functions
	#############################
	def createFolders(self, dir):
		if not(os.path.exists(dir)): os.mkdir(dir)
		if not(os.path.exists(dir + "/01_misc")): os.mkdir(dir + "/01_misc")
		if not(os.path.exists(dir + "/02_refs")): os.mkdir(dir + "/02_refs")
		if not(os.path.exists(dir + "/03_scenes")): os.mkdir(dir + "/03_scenes")
		if not(os.path.exists(dir + "/04_tex")): os.mkdir(dir + "/04_tex")
		if not(os.path.exists(dir + "/05_sims")): os.mkdir(dir + "/05_sims")
		if not(os.path.exists(dir + "/07_renders")): os.mkdir(dir + "/07_renders")
		if not(os.path.exists(dir + "/08_comp")): os.mkdir(dir + "/08_comp")

	def createShotFolders(self, dir):
		self.createFolders(dir)
		if not(os.path.exists(dir + "/06_caches")):
			os.mkdir(dir + "/06_caches")
			os.mkdir(dir + "/06_caches/assets")
			os.mkdir(dir + "/06_caches/fx")
			os.mkdir(dir + "/06_caches/proxies")

	def createAssetFolders(self, dir):
		self.createFolders(dir)
		if not(os.path.exists(dir + "/06_caches")):
			os.mkdir(dir + "/06_caches")
			os.mkdir(dir + "/06_caches/abc")
			os.mkdir(dir + "/06_caches/fbx")
			os.mkdir(dir + "/06_caches/obj")
			os.mkdir(dir + "/06_caches/proxies")

	def newShot(self, name, department, tag):
		self.createShotFolders(self.getShotsPath() + "/" + name)
		filename = newShot(self.tag, name, department, tag)
		return filename

	def newChar(self, name, department, tag):
		self.createAssetFolders(self.getCharsPath() + "/" + name)
		filename = newAsset(self.tag, "chars", name, department, tag)
		return filename

	def newEnv(self, name, department, tag):
		self.createAssetFolders(self.getEnvsPath() + "/" + name)
		filename = newAsset(self.tag, "env", name, department, tag)
		return filename

	def newProp(self, name, department, tag):
		self.createAssetFolders(self.getPropsPath() + "/" + name)
		filename = newAsset(self.tag, "props", name, department, tag)
		return filename
