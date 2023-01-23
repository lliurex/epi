#!/usr/bin/python3

import epi.epimanager as EpiManager
import os
import subprocess
import shutil
import sys
import syslog
import copy

class EpiGuiManager:

	ERROR_EPI_FILE_NOT_EXISTS=-1
	ERROR_EPI_EMPTY_FILE=-2
	ERROR_EPI_JSON=-3
	ERROR_SCRIPT_FILE_NOT_EXISTS=-4
	ERROR_SCRIPT_FILE_NOT_EXECUTE=-5
	ERROR_USER_NO_ROOT=-6
	ERROR_LOADING_LOCAL_DEB=-7
	ERROR_DEPENDS_LOCAL_DEB=-8
	ERROR_LOCAL_DEB_PROBLEMS=-9

	def __init__(self):

		self.packagesData=[]
		self.defaultIconPath="/usr/lib/python3/dist-packages/epigtk/rsrc/"
		self.clearCache()

	#def __init__

	def initProcess(self,epiFile,noCheck,debug):

		self.epiManager=EpiManager.EpiManager(debug)
		self.epiFile=epiFile
		self.noCheck=noCheck
		ret=self._checkEpiFile()

		if ret[0]:
			ret=self._loadEpiFile()
			if ret[0]:
				ret=self._createPackagesModel()
		
		return ret

	#def initProcess

	def _checkEpiFile(self):

		ret=["",""]
		validJson=self.epiManager.read_conf(self.epiFile)
		if validJson["status"]:
			validScript=self.epiManager.check_script_file()
			if validScript["status"]:
				ret=[True,'']
			else:
				if validScript["error"]=="path":
					ret=[False,EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXISTS]
				else:
					ret=[False,EpiGuiManager.ERROR_SCRIPT_FILE_NOT_EXECUTE]
		else:
			if validJson["error"]=="path":
				ret=[False,EpiGuiManager.ERROR_EPI_FILE_NOT_EXISTS]
			elif validJson["error"]=="json":
				ret=[False,EpiGuiManager.ERROR_EPI_JSON]
			else:
				ret=[False,EpiGuiManager.ERROR_EPI_EMPTY_FILE]

		return ret

	#def _checkEpiFile

	def _loadEpiFile(self):

		epiLoaded=self.epiManager.epiFiles
		order=len(epiLoaded)
		ret=[True,""]

		if order>0:
			checkRoot=self.epiManager.check_root()
			self.epiManager.get_pkg_info()
			requiredRoot=self.epiManager.required_root()
			self.requiredEula=self.epiManager.required_eula()
			
			if len(self.requiredEula)>0:
				self.eulaAccepted=False
			if checkRoot:
				if not self.noCheck:	
					self.lockInfo=self.epiManager.check_locks()
				else:
					self.lockInfo={}
				self.writeLog("Locks info: "+ str(self.lockInfo))
			else:
				self.lockInfo={}
				self.writeLog("Locks info: Not checked. User is not root")
					
			testInstall=self.epiManager.test_install()
			self.loadEpiConf=self.epiManager.epiFiles
			self.order=len(self.loadEpiConf)
		else:
			self.loadEpiConf=epiLoaded
			self.order=order

		if requiredRoot:
			ret=[False,EpiGuiManager.ERROR_USER_NO_ROOT]
		else:
			if testInstall[0]!="":
				if testInstall[0]=="1":
					ret=[False,EpiGuiManager.ERROR_LOADING_LOCAL_DEB]
				else:
					if testInstall[1]!="":
						return self._localDebError(testInstall)
		
		return ret

	#def _loadEpiFile

	def _localDebError(self,testInstall):

		if self.testInstall[1]!="":
			ret=[False,EpiGuiManager.ERROR_DEPENDS_LOCAL_DEB]
			self.msgLocalDebError=msg+"\n"+str(self.testInstall[1])
		else:
			ret=[False,EpiGuiManager.ERROR_LOCAL_DEB_PROBLEMS]
			self.msgLocalDebError=msg+"\n"+str(self.testinstall[0])

		self.writeLog("Test to install local deb: Unable to install package:"+str(self.testInstall))
	
		return ret

	#def _localDebError
	
	def _createPackagesModel(self):

		self.info=copy.deepcopy(self.loadEpiConf)
		self.areDepends=False
		self.searchEntry=False
		defaultChecked=False

		if len(self.info)>1:
			self.areDepends=True

		for item in self.info:
			pkgOrder=0
			showCB=False
			order=item
			self.uncheckAll=False
			if order==0:
				if self.info[item]["selection_enabled"]["active"]:
					self.searchEntry=True
					self.selectPkg=True
					showCB=True
					if self.info[item]["selection_enabled"]["all_selected"]:
						defaultChecked=True
						self.uncheckAll=True

				
			count=len(self.info[item]["pkg_list"])
			for element in self.info[item]["pkg_list"]:
				if order>0 and pkgOrder>0:
					pass
				else:
					tmp={}
					tmp["pkgId"]=element["name"]
					tmp["showCb"]=showCB

					if defaultChecked:
						tmp["isChecked"]=True
					else:
						try:
							tmp["isChecked"]=element["default_pkg"]
						except:
							tmp["isChecked"]=False			
					
					if order!=0:
						tmp["customName"]=self.info[item]["zomando"]
					else:
						try:
							tmp["customName"]=element["custom_name"]
						except:
							tmp["customName"]=element["name"]

					if order==0:
						try:
							iconPath=self.info[item]["custom_icon_path"]
							if iconPath!="":
								if iconPath[-1]!="/":
									iconPath="%s/"%iconPath
								tmp["pkgIcon"]="%s%s"%(iconPath,element["custom_icon"])
							else:
								tmp["pkgIcon"]="%s%s"%(self.defaultIconPath,"package.png")
						except:
							tmp["pkgIcon"]="%s%s"%(self.defaultIconPath,"package.png")
					else:
						tmp["pkgIcon"]="%s%s"%(self.defaultIconPath,"package_dep")

					tmp["status"]=self.epiManager.pkg_info[element["name"]]["status"]
					
					if order==0:
						tmp["isVisible"]=True
					else:
						tmp["isVisible"]=False

					tmp["isRunning"]=False
					tmp["resultProcess"]=-1
					tmp["order"]=order
					self.packagesData.append(tmp)
					
				pkgOrder+=1
		print(self.packagesData)
		return [True,""]

	#def _createPackagesModel

	def clearCache(self):

		clear=False
		versionFile="/root/.epi-gui.conf"
		cachePath1="/root/.cache/epi-gtk"
		installedVersion=self.getPackageVersion()

		if not os.path.exists(versionFile):
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)
				fd.close()

			clear=True

		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline()
				fd.close()

			if fileVersion!=installedVersion:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
					fd.close()
				clear=True
		
		if clear:
			if os.path.exists(cachePath1):
				shutil.rmtree(cachePath1)

	#def clearCache

	def getPackageVersion(self):

		command = "LANG=C LANGUAGE=en apt-cache policy epi-gtk"
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
		installed = None
		for line in iter(p.stdout.readline,b""):
			if type(line) is bytes:
				line=line.decode()

			stripedline = line.strip()
			if stripedline.startswith("Installed"):
				installed = stripedline.replace("Installed: ","")

		return installed

	#def getPackageVersion

	def writeLog(self,msg):

		syslog.openlog("EPI")
		syslog.syslog(msg)	

	#def writeLog			

#class EpiGuiManager