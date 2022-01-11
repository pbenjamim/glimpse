"""
Installation guide:

"""
#################################################################

import os
import sys
import subprocess
import c4d
from sys import platform

from . import GLProject
import importlib
importlib.reload(GLProject)

from PySide import QtGui, QtCore, QtUiTools

class FileManager(QtGui.QMainWindow):
	def loadUI(self):
		self.scriptPath = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
		self.UI = QtUiTools.QUiLoader().load(self.scriptPath + "/FileManager.ui", self)
		#self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

		self.kdrive = self.UI.findChild(QtGui.QRadioButton, "kdrive")
		self.wdrive = self.UI.findChild(QtGui.QRadioButton, "wdrive")
		self.idrive = self.UI.findChild(QtGui.QRadioButton, "idrive")

		self.yearCbox = self.UI.findChild(QtGui.QComboBox, "yearCbox")

		self.shotRadio = self.UI.findChild(QtGui.QRadioButton, "shotRadio")
		self.charRadio = self.UI.findChild(QtGui.QRadioButton, "charRadio")
		self.envRadio = self.UI.findChild(QtGui.QRadioButton, "envRadio")
		self.propRadio = self.UI.findChild(QtGui.QRadioButton, "propRadio")

		self.projectList = self.UI.findChild(QtGui.QListWidget, "projectList")
		self.filterList = self.UI.findChild(QtGui.QListWidget, "filterList")
		self.fileList = self.UI.findChild(QtGui.QListWidget, "fileList")

		self.nameEdit = self.UI.findChild(QtGui.QTextEdit, "nameEdit")
		self.departmentList = self.UI.findChild(QtGui.QListWidget, "departmentList")
		self.tagEdit = self.UI.findChild(QtGui.QTextEdit, "tagEdit")

		self.createButton = self.UI.findChild(QtGui.QPushButton, "createButton")
		self.explorerButton = self.UI.findChild(QtGui.QPushButton, "explorerButton")
		self.versionButton = self.UI.findChild(QtGui.QPushButton, "versionButton")
		self.overwriteButton = self.UI.findChild(QtGui.QPushButton, "overwriteButton")



	def setupGUI(self):
		self.loadUI()
		"""
		self.mainLayout = QtGui.QVBoxLayout()
		self.mainLayout.setContentsMargins(0,0,0,0)
		self.mainLayout.addWidget(self.UI)
		self.setLayout(self.mainLayout)
		"""

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
						if(GLProject.getShotExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Char"):
					items = []
					scenes = project.getCharScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Env"):
					items = []
					scenes = project.getEnvScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Prop"):
					items = []
					scenes = project.getPropScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

	def updateFilesAndFilters(self):
		self.clearFilters()
		if(self.project != ""):
			idx = self.projectList.row(self.projectList.currentItem())
			project = self.glprojects[idx]

			if(self.type != ""):
				if(self.type == "Shot"):
					self.filterList.addItems(sorted(project.getShotNames()))
					items = []
					scenes = project.getShotScenes()
					for i in range(len(scenes)):
						if(GLProject.getShotExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Char"):
					self.filterList.addItems(sorted(project.getCharNames()))
					items = []
					scenes = project.getCharScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Env"):
					self.filterList.addItems(sorted(project.getEnvNames()))
					items = []
					scenes = project.getEnvScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
					self.fileList.addItems(items)

				elif(self.type == "Prop"):
					self.filterList.addItems(sorted(project.getPropNames()))
					items = []
					scenes = project.getPropScenes()
					for i in range(len(scenes)):
						if(GLProject.getAssetExtension(scenes[i]) == "c4d"):
							items.append(scenes[i])
					items.sort()
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
		result.sort()
		self.fileList.addItems(result)

	def openFileInExplorer(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		if(self.type == "Shot"):
			path = project.getShotPath(file)
			subprocess.Popen(r'explorer /select,' + path.replace('/', '\\'))
		elif(self.type == "Char"):
			path = project.getCharPath(file)
			subprocess.Popen(r'explorer /select,' + path.replace('/', '\\'))
		elif(self.type == "Env"):
			path = project.getEnvPath(file)
			subprocess.Popen(r'explorer /select,' + path.replace('/', '\\'))
		else:
			path = project.getPropPath(file)
			subprocess.Popen(r'explorer /select,' + path.replace('/', '\\'))

	def openFile(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		#hou.c4dFile.clear()
		valid = False
		if(self.type == "Shot"):

			fullpath = project.getShotPath(file)
			homepath = project.getShotHomePath(file)
			filefolder = GLProject.getFileFolderPath(project.getShotPath(file))

			if (GLProject.getShotExtension(file) == "c4d"):
				valid = True
		elif(self.type == "Char"):
			fullpath = project.getCharPath(file)
			homepath = project.getCharHomePath(file)
			filefolder = GLProject.getFileFolderPath(project.getCharPath(file))
			if (GLProject.getAssetExtension(file) == "c4d"):
				valid = True
		elif(self.type == "Env"):
			fullpath = project.getEnvPath(file)
			homepath = project.getEnvHomePath(file)
			filefolder = GLProject.getFileFolderPath(project.getEnvPath(file))
			if (GLProject.getAssetExtension(file) == "c4d"):
				valid = True
		else:
			fullpath = project.getPropPath(file)
			homepath = project.getPropHomePath(file)
			filefolder = GLProject.getFileFolderPath(project.getPropPath(file))
			if (GLProject.getAssetExtension(file) == "c4d"):
				valid = True

		if (valid):
			c4d.documents.LoadFile(str(fullpath))
			c4d.EventAdd()

	def saveFile(self, project, homepath, fullpath):
			doc = c4d.documents.GetActiveDocument()
			doc.SetDocumentName(str(fullpath).split("/")[-1])
			doc.SetDocumentPath(str(fullpath))
			assets = []
			missingAssets = []
			#c4d.documents.SaveProject(doc, c4d.SAVEPROJECT_ASSETS | c4d.SAVEPROJECT_SCENEFILE | c4d.SAVEPROJECT_ADDTORECENTLIST | c4d.SAVEPROJECT_USEDOCUMENTNAMEASFILENAME, str(homepath), assets, missingAssets)
			#c4d.documents.SaveDocument(doc, str(fullpath), c4d.SAVEDOCUMENTFLAGS_NONE, c4d.FORMAT_C4DEXPORT)
			c4d.documents.SaveDocument(doc, str(fullpath), c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
			wci = c4d.GetWorldContainerInstance()
			wci[90003] = str(fullpath)
			self.updateFilesAndFilters()

	def newFile(self, name, department, tag):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]
		if(self.type == "Shot"):
			filename = project.newShot(name, department, tag) + ".c4d"
			fullpath = project.getShotPath(filename)
			homepath = project.getShotHomePath(filename)
		elif(self.type == "Char"):
			filename = project.newChar(name, department, tag) + ".c4d"
			fullpath = project.getCharPath(filename)
			homepath = project.getCharHomePath(filename)
		elif(self.type == "Env"):
			filename = project.newEnv(name, department, tag) + ".c4d"
			fullpath = project.getEnvPath(filename)
			homepath = project.getEnvHomePath(filename)
		else:
			filename = project.newProp(name, department, tag) + ".c4d"
			fullpath = project.getPropPath(filename)
			homepath = project.getPropHomePath(filename)

		self.saveFile(project, homepath, fullpath)

	def upVersion(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		if(self.type == "Shot"):
			filename = GLProject.upShotVersion(file) + ".c4d"
			fullpath = project.getShotPath(filename)
			homepath = project.getShotHomePath(file)
		elif(self.type == "Char"):
			filename = GLProject.upAssetVersion(file) + ".c4d"
			fullpath = project.getCharPath(filename)
			homepath = project.getCharHomePath(file)
		elif(self.type == "Env"):
			filename = GLProject.upAssetVersion(file) + ".c4d"
			fullpath = project.getEnvPath(filename)
			homepath = project.getEnvHomePath(file)
		else:
			filename = GLProject.upAssetVersion(file) + ".c4d"
			fullpath = project.getPropPath(filename)
			homepath = project.getPropHomePath(file)

		if not (os.path.exists(fullpath)):
			self.saveFile(project, homepath, fullpath)

	def overwrite(self, file):
		idx = self.projectList.row(self.projectList.currentItem())
		project = self.glprojects[idx]

		if(self.type == "Shot"):
			fullpath = project.getShotPath(file)
			homepath = project.getShotHomePath(file)
		elif(self.type == "Char"):
			fullpath = project.getCharPath(file)
			homepath = project.getCharHomePath(file)
		elif(self.type == "Env"):
			fullpath = project.getEnvPath(file)
			homepath = project.getEnvHomePath(file)
		else:
			fullpath = project.getPropPath(file)
			homepath = project.getPropHomePath(file)

		if (os.path.exists(fullpath)):
			self.saveFile(project, homepath, fullpath)


	###################################################
	# Events
	###################################################

	def kdriveClicked(self):
		self.drive = self.drives[0]
		self.updateDrive(self.drive)

	def wdriveClicked(self):
		self.drive = self.drives[1]
		self.updateDrive(self.drive)

	def idriveClicked(self):
		self.drive = self.drives[2]
		self.updateDrive(self.drive)

	def yearCboxActivated(self, index):
		if (index != -1):
			self.year = self.yearCbox.currentText()
			self.clearProjects()
			projectsAux = GLProject.getProjects(self.drive + "/" + self.year)

			projects = []
			for i in range(len(projectsAux)):
				project = GLProject.GLProject(self.drive + "/" + self.year + "/" + projectsAux[i])
				if(project.valid):
					self.glprojects.append(project)
					projects.append(projectsAux[i])

			projects.sort()
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

	def overwriteButtonClicked(self):
		if(self.project != "" and self.file != ""):
			self.overwrite(self.file)

	######################################################################################

	def setupEvents(self):

		self.kdrive.clicked.connect(self.kdriveClicked)
		self.wdrive.clicked.connect(self.wdriveClicked)
		self.idrive.clicked.connect(self.idriveClicked)

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
		self.overwriteButton.clicked.connect(self.overwriteButtonClicked)

	def preSelect(self):
		toks = c4d.documents.GetActiveDocument().GetDocumentPath().split("\\")
		print(toks)
		#print(toks)
		#toks = hou.c4dFile.path().split("/")
		if (len(toks) < 7):
			return False

		# DRIVE -- ADJUST MANUALLY
		drive = toks[0]
		if drive == self.drives[0]:
			self.kdrive.click()
			self.kdrive.setChecked(True)
		elif drive == self.drives[1]:
			self.wdrive.click()
			self.wdrive.setChecked(True)
		elif drive == self.drives[2]:
			self.idrive.click()
			self.idrive.setChecked(True)
		else:
			return False

		# YEAR
		year = toks[1]
		years = []
		for i in range(0, self.yearCbox.count()):
			years.append(self.yearCbox.itemText(i))
		if year in years:
			self.yearCbox.setCurrentIndex(years.index(year))
			self.yearCboxActivated(years.index(year))
		else:
			return False

		# PROJECT
		project = toks[2]
		projects = []
		for i in range(0, self.projectList.count()):
			self.projectList.setCurrentRow(i)
			projects.append(self.projectList.currentItem().text())
		if project in projects:
			self.projectList.setCurrentRow(projects.index(project))
			self.projectList.itemClicked.emit(self.projectList.currentItem())
			self.projectListClicked(self.projectList.currentItem())
		else:
			return False

		# ASSET / SHOT
		filetype = toks[3]
		if filetype == "30_shots":
			self.shotRadio.click()
		elif filetype == "20_assets":
			assettype = toks[4]
			if assettype == "chars":
				self.charRadio.click()
			elif assettype == "env":
				self.envRadio.click()
			elif assettype == "props":
				self.propRadio.click()
			else:
				return False
		else:
			return False

		# FILENAME
		filename = c4d.documents.GetActiveDocument().GetDocumentName()
		files = []
		for i in range(0, self.fileList.count()):
			self.fileList.setCurrentRow(i)
			files.append(self.fileList.currentItem().text())
		if filename in files:
			self.fileList.setCurrentRow(files.index(filename))
			self.fileList.itemClicked.emit(self.fileList.currentItem())
			self.fileListClicked(self.fileList.currentItem())
		else:
			return False

		return True

	def projectPreSelect(self):
		cache = open(self.cachePath, "r")

		# DRIVE -- ADJUST MANUALLY
		drive = cache.readline().rstrip()
		if drive == self.drives[0]:
			self.kdrive.click()
			self.kdrive.setChecked(True)
		elif drive == self.drives[1]:
			self.wdrive.click()
			self.wdrive.setChecked(True)
		elif drive == self.drives[2]:
			self.idrive.click()
			self.idrive.setChecked(True)
		else:
			cache.close()
			return False

		# YEAR
		year = cache.readline().rstrip()
		years = []
		for i in range(0, self.yearCbox.count()):
			years.append(self.yearCbox.itemText(i))
		if year in years:
			self.yearCbox.setCurrentIndex(years.index(year))
			self.yearCboxActivated(years.index(year))
		else:
			cache.close()
			return False

		# PROJECT
		project = cache.next().rstrip()
		projects = []
		for i in range(0, self.projectList.count()):
			self.projectList.setCurrentRow(i)
			projects.append(self.projectList.currentItem().text())
		if project in projects:
			self.projectList.setCurrentRow(projects.index(project))
			self.projectList.itemClicked.emit(self.projectList.currentItem())
			self.projectListClicked(self.projectList.currentItem())
		else:
			cache.close()
			return False

		cache.close()
		self.shotRadio.click()
		return True

	# write last project selection to cache (need drive year and project name)
	def closeEvent(self, event):
		if platform != "linux2":
			if(self.drive != "" and self.year != "" and self.project != ""):

				if not(os.path.exists("C:/temp")):
					os.mkdir("C:/temp")

				if not (os.path.exists(self.cachePath)):
					cache = open(self.cachePath, "w")
				else:
					cache = open(self.cachePath, "r+")
					cache.truncate(0)

				cache.write(self.drive + "\n" + self.year + "\n" + self.project)
				cache.close()


	def __init__(self):
		super(FileManager, self).__init__()
		# This one has to be put manually
		if platform == "linux2":
			self.drives = ["/home/diogo/work2", "/home/diogo/work", "/home/diogo/work3"]
		else:
			self.drives = ["E:", "W:", "I:"]
			self.cachePath = "C:/temp/cache.txt"
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

		# pre select
		if platform != "linux2":
			if not ( self.preSelect() ):
				# try to load prev project selection
				if (os.path.exists(self.cachePath)):
					if not (self.projectPreSelect() ):
						print("Error in project pre select!")
				else:
					# default startup
					self.kdrive.click()
					self.kdrive.setChecked(True)
					self.shotRadio.click()
		else:
			if not ( self.preSelect() ):
				self.kdrive.click()
				self.kdrive.setChecked(True)
				self.shotRadio.click()

def main():
	app = QtGui.QApplication.instance()
	if not app:
		app = QtGui.QApplication(sys.argv)

	mainWin = FileManager()

	mainWin.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint);
	mainWin.setProperty("saveWindowPref", True)

	mainWin.show()
	mainWin.raise_()
	mainWin.activateWindow()
	
	app.setActiveWindow(mainWin)
	#app.raise_()
	#app.activateWindow()

	#sys.exit(app.exec_()) #<---Closes C4D too!!
 	app.exec_()  #Closes the Qt dialog

if __name__ == '__main__':
	main()