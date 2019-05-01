"""
# PASTE THIS IN SHELF TOOL ("Script" toolbar)

from GL_File_Manager import HoudiniFileManager
reload(HoudiniFileManager)
HoudiniFileManager.run()

"""
#################################################################

import hou
import os
import subprocess

import GLProject
reload(GLProject)

from PySide2 import QtWidgets, QtCore, QtUiTools

class FileManager(QtWidgets.QWidget):
	def loadUI(self):
		self.scriptPath = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
		self.UI = QtUiTools.QUiLoader().load(self.scriptPath + "/FileManager.ui")
		self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

		self.kdrive = self.UI.findChild(QtWidgets.QRadioButton, "kdrive")
		self.wdrive = self.UI.findChild(QtWidgets.QRadioButton, "wdrive")

		self.yearCbox = self.UI.findChild(QtWidgets.QComboBox, "yearCbox")

		self.shotRadio = self.UI.findChild(QtWidgets.QRadioButton, "shotRadio")
		self.charRadio = self.UI.findChild(QtWidgets.QRadioButton, "charRadio")
		self.envRadio = self.UI.findChild(QtWidgets.QRadioButton, "envRadio")
		self.propRadio = self.UI.findChild(QtWidgets.QRadioButton, "propRadio")

		self.projectList = self.UI.findChild(QtWidgets.QListWidget, "projectList")
		self.filterList = self.UI.findChild(QtWidgets.QListWidget, "filterList")
		self.fileList = self.UI.findChild(QtWidgets.QListWidget, "fileList")

		self.nameEdit = self.UI.findChild(QtWidgets.QTextEdit, "nameEdit")
		self.departmentList = self.UI.findChild(QtWidgets.QListWidget, "departmentList")
		self.tagEdit = self.UI.findChild(QtWidgets.QTextEdit, "tagEdit")

		self.createButton = self.UI.findChild(QtWidgets.QPushButton, "createButton")
		self.explorerButton = self.UI.findChild(QtWidgets.QPushButton, "explorerButton")
		self.versionButton = self.UI.findChild(QtWidgets.QPushButton, "versionButton")



	def setupGUI(self):
		self.loadUI()
		self.mainLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.setContentsMargins(0,0,0,0)
		self.mainLayout.addWidget(self.UI)
		self.setLayout(self.mainLayout)

		####################################
		# Fill static widgets
		####################################
		self.departmentList.addItem("layout")
		self.departmentList.addItem("anim")
		self.departmentList.addItem("model")
		self.departmentList.addItem("rig")
		self.departmentList.addItem("fx")
		self.departmentList.addItem("lgt")
		self.departmentList.addItem("print")

	###################################################
	# Event Functions
	###################################################

	def clearFilters(self):
		self.filter = ""
		self.filterList.clear()
		self.clearFiles()

	def clearFiles(self):
		self.file = ""
		self.fileList.clear()


	def clearProjects(self):
		self.clearFilters()
		self.project = ""
		self.glprojects = []
		self.projectList.clear()

	def clearYears(self):
		self.year = ""

		self.clearProjects()
		self.yearCbox.clear()

	def updateDrive(self, drive):
		self.clearYears()
		self.yearCbox.addItems(GLProject.getYears(drive))

		if(self.yearCbox.currentIndex != -1):
			self.yearCboxActivated(self.yearCbox.currentIndex)

	def updateFiles(self):
		self.clearFiles()
		if(self.project != ""):
			idx = self.projectList.row(self.projectList.currentItem())
			project = self.glprojects[idx]

			if(self.type != ""):
				if(self.type == "Shot"):
					items = []
					scenes = project.getShotScenes()
					for i in range(len(scenes)):
						if(GLProject.getShotExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Char"):
					items = []
					scenes = project.getCharScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Env"):
					items = []
					scenes = project.getEnvScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Prop"):
					items = []
					scenes = project.getPropScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)


	def updateFilesAndFilters(self):
		self.clearFilters()
		if(self.project != ""):
			idx = self.projectList.row(self.projectList.currentItem())
			project = self.glprojects[idx]

			if(self.type != ""):
				if(self.type == "Shot"):
					self.filterList.addItems(project.getShotNames())
					items = []
					scenes = project.getShotScenes()
					for i in range(len(scenes)):
						if(GLProject.getShotExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Char"):
					self.filterList.addItems(project.getCharNames())
					items = []
					scenes = project.getCharScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Env"):
					self.filterList.addItems(project.getEnvNames())
					items = []
					scenes = project.getEnvScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

				elif(self.type == "Prop"):
					self.filterList.addItems(project.getPropNames())
					items = []
					scenes = project.getPropScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "hip"):
							items.append(scenes[i])
					self.fileList.addItems(items)

	def filterFiles(self):
		result = []
		self.updateFiles()

		for i in range(self.fileList.count()):
			file = self.fileList.item(i).text()

			if(self.type != ""):
				if(self.type == "Shot"):
					if(GLProject.getShotName(file) == self.filter):
						result.append(file)
				else:
					if(GLProject.getAssetName(file) == self.filter):
						result.append(file)
		self.clearFiles()
		self.fileList.addItems(result)

	def openFileInExplorer(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		if(self.type == "Shot"):
			path = project.getShotPath(file)
			subprocess.Popen(r'explorer /select,' + path)
		elif(self.type == "Char"):
			path = project.getCharPath(file)
			subprocess.Popen(r'explorer /select,' + path)
		elif(self.type == "Env"):
			path = project.getEnvPath(file)
			subprocess.Popen(r'explorer /select,' + path)
		else:
			path = project.getPropPath(file)
			subprocess.Popen(r'explorer /select,' + path)

	def openFile(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		hou.hipFile.clear()
		valid = False
		if(self.type == "Shot"):
			filefolder = GLProject.getFileFolderPath(project.getShotPath(file)).replace("\\", "/")
			if (GLProject.getShotExtension(file) == "hip"):
				valid = True
		elif(self.type == "Char"):
			filefolder = GLProject.getFileFolderPath(project.getCharPath(file)).replace("\\", "/")
			if (GLProject.getAssetExtension(file) == "hip"):
				valid = True
		elif(self.type == "Env"):
			filefolder = GLProject.getFileFolderPath(project.getEnvPath(file)).replace("\\", "/")
			if (GLProject.getAssetExtension(file) == "hip"):
				valid = True
		else:
			filefolder = GLProject.getFileFolderPath(project.getPropPath(file)).replace("\\", "/")
			if (GLProject.getAssetExtension(file) == "hip"):
				valid = True

		if (valid):
			hou.putenv("Hip", filefolder)
			hou.hipFile.load(file)
			hou.putenv("Hip", (project.rootDir + "\\").replace("\\", "/"))

	def saveFile(self, project, homepath, fullpath):
			hou.putenv("Hip", (project.rootDir + "\\").replace("\\", "/"))
			hou.putenv("GLProject", (project.rootDir + "\\").replace("\\", "/"))
			hou.putenv("GLScene", GLProject.getFileFolderPath(fullpath))
			hou.putenv("GLSim", (homepath + "\\05_sims\\").replace("\\", "/"))
			hou.putenv("GLTex", (homepath + "\\04_tex\\").replace("\\", "/"))
			hou.putenv("GLCache", (homepath + "\\06_caches\\").replace("\\", "/"))
			hou.putenv("GLRender", (homepath + "\\07_renders\\").replace("\\", "/"))
			hou.hipFile.save(fullpath)
			self.updateFilesAndFilters()

	def newFile(self, name, department, tag):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]
		if(self.type == "Shot"):
			filename = project.newShot(name, department, tag) + ".hip"
			fullpath = project.getShotPath(filename)
			homepath = project.getShotHomePath(filename)
		elif(self.type == "Char"):
			filename = project.newChar(name, department, tag) + ".hip"
			fullpath = project.getCharPath(filename)
			homepath = project.getCharHomePath(filename)
		elif(self.type == "Env"):
			filename = project.newEnv(name, department, tag) + ".hip"
			fullpath = project.getEnvPath(filename)
			homepath = project.getEnvHomePath(filename)
		else:
			filename = project.newProp(name, department, tag) + ".hip"
			fullpath = project.getPropPath(filename)
			homepath = project.getPropHomePath(filename)

		self.saveFile(project, homepath, fullpath)

	def upVersion(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		if(self.type == "Shot"):
			filename = GLProject.upShotVersion(file) + ".hip"
			fullpath = project.getShotPath(filename)
			homepath = project.getShotHomePath(file)
		elif(self.type == "Char"):
			filename = GLProject.upAssetVersion(file) + ".hip"
			fullpath = project.getCharPath(filename)
			homepath = project.getCharHomePath(file)
		elif(self.type == "Env"):
			filename = GLProject.upAssetVersion(file) + ".hip"
			fullpath = project.getEnvPath(filename)
			homepath = project.getEnvHomePath(file)
		else:
			filename = GLProject.upAssetVersion(file) + ".hip"
			fullpath = project.getPropPath(filename)
			homepath = project.getPropHomePath(file)

		if not (os.path.exists(fullpath)):
			self.saveFile(project, homepath, fullpath)

	###################################################
	# Events
	###################################################

	def kdriveClicked(self):
		self.drive = "K:"
		self.updateDrive("K:")

	def wdriveClicked(self):
		self.drive = "W:"
		self.updateDrive("W:")

	def yearCboxActivated(self, index):
		if (index != -1):
			self.year = self.yearCbox.currentText()
			self.clearProjects()
			projectsAux = GLProject.getProjects(self.drive + "\\" + self.year)

			projects = []
			for i in range(len(projectsAux)):
				project = GLProject.GLProject(self.drive + "\\" + self.year + "\\" + projectsAux[i])
				if(project.valid):
					self.glprojects.append(project)
					projects.append(projectsAux[i])

			self.projectList.addItems(projects)
	

	def shotClicked(self):
		self.type = "Shot"
		self.updateFilesAndFilters()

	def charClicked(self):
		self.type = "Char"
		self.updateFilesAndFilters()

	def envClicked(self):
		self.type = "Env"
		self.updateFilesAndFilters()

	def propClicked(self):
		self.type = "Prop"
		self.updateFilesAndFilters()

	def projectListClicked(self, item):
		self.project = item.text()
		self.updateFilesAndFilters()

	def filterListClicked(self, item):
		self.filter = item.text()
		self.filterFiles()

	def fileListClicked(self, item):
		self.file = item.text()

	def fileListDoubleClicked(self, item):
		file = item.text()
		self.openFile(file)

	def departmentListClicked(self, item):
		self.department = item.text()

	def explorerButtonClicked(self):
		file = self.file
		if(file != ""):
			self.openFileInExplorer(file)

	def nameEditTextChanged(self):
		text = self.nameEdit.toPlainText()
		if(len(text) > 0):
			char = text[len(text)-1]
			if (char == "_" or char == " " or char == "	"):
				self.nameEdit.setPlainText(text[:len(text)-1])

	def tagEditTextChanged(self):
		text = self.tagEdit.toPlainText()
		if(len(text) > 0):
			char = text[len(text)-1]
			if (char == "_" or char == " " or char == "	"):
				self.tagEdit.setPlainText(text[:len(text)-1])

	def createButtonClicked(self):
		if(self.project != "" and self.department != ""):
			name = self.nameEdit.toPlainText()
			tag = self.tagEdit.toPlainText()
			if(tag == "" or len(tag) == 0):
				tag = "main"

			if(len(name) > 0 and len(tag) > 0):
				self.newFile(name, self.department, tag)

	def versionButtonClicked(self):
		if(self.project != "" and self.file != ""):
			self.upVersion(self.file)

	######################################################################################

	def setupEvents(self):

		self.kdrive.clicked.connect(self.kdriveClicked)
		self.wdrive.clicked.connect(self.wdriveClicked)

		self.yearCbox.activated.connect(self.yearCboxActivated)

		self.shotRadio.clicked.connect(self.shotClicked)
		self.charRadio.clicked.connect(self.charClicked)
		self.envRadio.clicked.connect(self.envClicked)
		self.propRadio.clicked.connect(self.propClicked)

		self.projectList.itemClicked.connect(self.projectListClicked)
		self.filterList.itemClicked.connect(self.filterListClicked)
		self.fileList.itemClicked.connect(self.fileListClicked)
		self.departmentList.itemClicked.connect(self.departmentListClicked)
		self.fileList.itemDoubleClicked.connect(self.fileListDoubleClicked)

		self.nameEdit.textChanged.connect(self.nameEditTextChanged)
		self.tagEdit.textChanged.connect(self.tagEditTextChanged)

		self.createButton.clicked.connect(self.createButtonClicked)
		self.explorerButton.clicked.connect(self.explorerButtonClicked)
		self.versionButton.clicked.connect(self.versionButtonClicked)

	def __init__(self):
		super(FileManager, self).__init__()

		###################################################
		# Class variables
		###################################################
		self.drive = ""
		self.year = ""
		self.project = ""
		self.type = ""
		self.file = ""
		self.filter = ""
		self.department = ""

		self.glprojects = []

		self.setupGUI()
		self.setupEvents()

		self.kdrive.click()
		self.kdrive.setChecked(True)
		self.shotRadio.click()

def run():
	mainWin = FileManager()
	mainWin.show()